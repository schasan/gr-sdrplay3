/* -*- c++ -*- */
/*
 * Copyright 2020 Mario Schulz.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "rsp1a_impl.h"

bool g_masterInitialised = false;
bool g_slaveUninitialised = false;
static long g_samples = 0L;
static long g_lastsamples = 0L;
static long g_r = 0L;
static long g_x = 0L;

namespace gr {
namespace msz {

struct cplx {
	short xi, xq;
};
boost::circular_buffer<cplx> cb(50000000);
boost::mutex g_mutex;

void StreamACallback(short *xi, short *xq, sdrplay_api_StreamCbParamsT *params,
                unsigned int numSamples, unsigned int reset, void *cbContext)
{
        static long calls = 0L;
        static time_t starttime;
        cplx c;

        //if (samples == 0)
        //        time(&starttime);

        g_samples += numSamples;
        if (numSamples > g_r) g_r = numSamples;

        if (reset) {
        }

        // Process stream callback data here
        boost::mutex::scoped_lock push_lock(g_mutex);
        for (int i; i<numSamples; i++) {
        	c.xi = xi[i];
        	c.xq = xq[i];
        	cb.push_back(c);
        }
        push_lock.unlock();

        return;
}

void StreamBCallback(short *xi, short *xq, sdrplay_api_StreamCbParamsT *params,
                unsigned int numSamples, unsigned int reset, void *cbContext) {
        if (reset) {
        }

        // Process stream callback data here - this callback will only be used in dual tuner mode

        return;
}

void EventCallback(sdrplay_api_EventT eventId, sdrplay_api_TunerSelectT tuner,
                sdrplay_api_EventParamsT *params, void *cbContext) {
}

rsp1a::sptr rsp1a::make(float frequency, long sample_rate) {
	return gnuradio::get_initial_sptr(new rsp1a_impl(frequency, sample_rate));
}

/*
 * The private constructor
 */
rsp1a_impl::rsp1a_impl(float frequency, long sample_rate) :
		gr::sync_block("rsp1a", gr::io_signature::make(0, 0, sizeof(float)),
				gr::io_signature::make(1, 1, sizeof(gr_complex))) {
	GR_LOG_INFO(d_logger, "Open SDRPlay API");
	if ((m_err = sdrplay_api_Open()) != sdrplay_api_Success) {
		GR_LOG_FATAL(d_logger, "Failed to open SDRPlay API");
		GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
		exit(1);
	} else {                // API opened successfully
		GR_LOG_INFO(d_logger, "SDRPlay API opened successfully");
		// Enable debug logging output
		if ((m_err = sdrplay_api_DebugEnable(NULL, sdrplay_api_DbgLvl_Verbose))
				!= sdrplay_api_Success) {
			GR_LOG_FATAL(d_logger, "sdrplay debug enable failed");
			GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
			sdrplay_api_Close();
			exit(1);
		} else {
			GR_LOG_INFO(d_logger, "sdrplay debug enable ok");
		}
		// Check API versions match
		if ((m_err = sdrplay_api_ApiVersion(&m_ver)) != sdrplay_api_Success) {
			GR_LOG_FATAL(d_logger, "Cannot get API version");
			GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
			sdrplay_api_Close();
			exit(1);
		} else {
			GR_LOG_INFO(d_logger, "sdrplay API version get ok");
		}
		if (m_ver != SDRPLAY_API_VERSION) {
			GR_LOG_FATAL(d_logger, "sdrplay API version mismatch");
			sdrplay_api_Close();
			exit(1);
		} else {
			GR_LOG_INFO(d_logger, "sdrplay API version check ok");
		}

		// Lock API while device selection is performed
		sdrplay_api_LockDeviceApi();

		// Fetch list of available devices
		if ((m_err = sdrplay_api_GetDevices(m_devs, &m_ndev,
				sizeof(m_devs) / sizeof(sdrplay_api_DeviceT)))
				!= sdrplay_api_Success) {
			GR_LOG_FATAL(d_logger, "sdrplay get devices fails");
			GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
			sdrplay_api_UnlockDeviceApi();
			sdrplay_api_Close();
			exit(1);
		} else {
			GR_LOG_INFO(d_logger, "sdrplay get devices succeeds");
			if (!(m_ndev > 0)) {
				GR_LOG_FATAL(d_logger, "sdrplay ... but no devices found");
				sdrplay_api_UnlockDeviceApi();
				sdrplay_api_Close();
				exit(1);
			} else {
				for (int i = 0; i < (int) m_ndev; i++) {
					if (m_devs[i].hwVer == SDRPLAY_RSPduo_ID) {
						sprintf(m_pr_buffer,
								"Dev%d: SerNo=%s hwVer=%d tuner=0x%.2x rspDuoMode=0x%.2x",
								i, m_devs[i].SerNo, m_devs[i].hwVer,
								m_devs[i].tuner, m_devs[i].rspDuoMode);
						GR_LOG_INFO(d_logger, m_pr_buffer);
					} else {
						sprintf(m_pr_buffer,
								"Dev%d: SerNo=%s hwVer=%d tuner=0x%.2x", i,
								m_devs[i].SerNo, m_devs[i].hwVer,
								m_devs[i].tuner);
						GR_LOG_INFO(d_logger, m_pr_buffer);
					}
				}

				// Choose device
#ifdef RSPDUO_CODE
				if ((reqTuner == 1) || m_master_slave) { // requires RSPduo
					// Pick first RSPduo
					for (i = 0; i < (int) ndev; i++) {
						if (m_devs[i].hwVer == SDRPLAY_RSPduo_ID) {
							chosenIdx = i;
							break;
						}
					}
				} else {
#endif
				// Pick first device of any type
				for (int i = 0; i < (int) m_ndev; i++) {
					m_chosenIdx = i;
					break;
				}
#ifdef RSPDUO_CODE
				}
#endif
				if (m_chosenIdx < 0) {
					GR_LOG_FATAL(d_logger, "sdrplay no device index could be selected");
					sdrplay_api_UnlockDeviceApi();
					sdrplay_api_Close();
					exit(1);
				}

				m_chosenDevice = &m_devs[m_chosenIdx];

				// Select chosen device
				if ((m_err = sdrplay_api_SelectDevice(m_chosenDevice)) != sdrplay_api_Success) {
					GR_LOG_FATAL(d_logger, "sdrplay api_SelectDevice failed");
					GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
					sdrplay_api_UnlockDeviceApi();
					sdrplay_api_Close();
					exit(1);
				}

				// Unlock API now that device is selected
				sdrplay_api_UnlockDeviceApi();

				// Retrieve device parameters so they can be changed if wanted
				if ((m_err = sdrplay_api_GetDeviceParams(m_chosenDevice->dev, &m_deviceParams)) != sdrplay_api_Success) {
					GR_LOG_FATAL(d_logger, "sdrplay_api_GetDeviceParams failed");
					GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
					sdrplay_api_Close();
					exit(1);
				}

				// Check for NULL pointers before changing settings
				if (m_deviceParams == NULL) {
					GR_LOG_FATAL(d_logger, "sdrplay_api_GetDeviceParams returned NULL deviceParams pointer");
					GR_LOG_FATAL(d_logger, sdrplay_api_GetErrorString(m_err));
					sdrplay_api_Close();
					exit(1);
				}

				// Configure dev parameters
				if (m_deviceParams->devParams != NULL) {// This will be NULL for slave devices as only the master can change these parameters
					// Only need to update non-default settings
					if (!m_master_slave) {
						// Change from default Fs  to 8MHz
						m_deviceParams->devParams->fsFreq.fsHz = 2000000.0; // Sample rate
					} else {
						// Can't change Fs in master/slave mode
					}
				}

				// Configure tuner parameters (depends on selected Tuner which set of parameters to use)
				m_chParams = (m_chosenDevice->tuner == sdrplay_api_Tuner_B) ? m_deviceParams->rxChannelB : m_deviceParams->rxChannelA;
				if (m_chParams != NULL) {
					m_chParams->tunerParams.rfFreq.rfHz = 94400000.0;       // hr1
					m_chParams->tunerParams.rfFreq.rfHz = 89300000.0;       // hr3
					m_chParams->tunerParams.bwType = sdrplay_api_BW_1_536;
					if (!m_master_slave) {		// Change single tuner mode to ZIF
						m_chParams->tunerParams.ifType = sdrplay_api_IF_Zero;
					}
					m_chParams->tunerParams.gain.gRdB = 40;
					m_chParams->tunerParams.gain.LNAstate = 5;

					// Disable AGC
					m_chParams->ctrlParams.agc.enable = sdrplay_api_AGC_DISABLE;
				} else {
					GR_LOG_FATAL(d_logger, "sdrplay_api_GetDeviceParams returned NULL chParams pointer");
					sdrplay_api_Close();
					exit(1);
				}

				// Assign callback functions to be passed to sdrplay_api_Init()
				m_cbFns.StreamACbFn = StreamACallback;
				m_cbFns.StreamBCbFn = StreamBCallback;
				m_cbFns.EventCbFn = EventCallback;

				// Now we're ready to start by calling the initialisation function
				// This will configure the device and start streaming
				if ((m_err = sdrplay_api_Init(m_chosenDevice->dev, &m_cbFns, NULL)) != sdrplay_api_Success) {
					GR_LOG_INFO(d_logger, "sdrplay_api_Init failed - but may be ok");
					GR_LOG_INFO(d_logger, sdrplay_api_GetErrorString(m_err));
					if (m_err == sdrplay_api_StartPending) { // This can happen if we're starting in master/slave mode as a slave and the master is not yet running
						while (true) {
							sleep(1);
							if (g_masterInitialised) { // Keep polling flag set in event callback until the master is initialised
								// Redo call - should succeed this time
								if ((m_err = sdrplay_api_Init(m_chosenDevice->dev, &m_cbFns, NULL)) != sdrplay_api_Success) {
									GR_LOG_FATAL(d_logger, "sdrplay_api_Init failed after wait and retry");
								}
								sdrplay_api_Close();
								exit(1);
							}
							GR_LOG_INFO(d_logger, "Waiting for master to initialise");
						}
					} else {
						sdrplay_api_Close();
						exit(1);
					}
				}
			}
		}
	}
}

/*
 * Our virtual destructor.
 */
rsp1a_impl::~rsp1a_impl() {
	// We never get here ...
	GR_LOG_INFO(d_logger, "sdrplay closing down");
	sdrplay_api_Close();
}

int rsp1a_impl::work(int noutput_items, gr_vector_const_void_star &input_items,
		gr_vector_void_star &output_items) {
	gr_complex *out = (gr_complex*) output_items[0];
	float i[4096], q[4096];
	unsigned int cb_size;

	// Do <+signal processing+>
	if (noutput_items > g_x) g_x = noutput_items;
#ifdef FLATLINE
	switch (m_toggle++ & 3) {
	case 0:
		i = 0.4;
		q = 0.7;
		break;
	case 1:
		i = 0.6;
		q = 0.7;
		break;
	case 2:
		i = 0.4;
		q = 0.9;
		break;
	case 3:
		i = 0.6;
		q = 0.9;
		break;
	default:
		i = 0.0;
		q = 0.0;
		break;
	}
	volk_32f_x2_interleave_32fc(out, &i, &q, 1);
#else
    boost::mutex::scoped_lock pull_lock(g_mutex);
    cb_size = cb.size();
    int items_to_handle = cb_size > noutput_items ? noutput_items : cb_size;
    items_to_handle = items_to_handle > 4096 ? 4096 : items_to_handle;

    for (int ii = 0; ii<items_to_handle; ii++) {
		i[ii] = cb[0].xi;
		q[ii] = cb[0].xq;
		cb.pop_front();
    }
    pull_lock.unlock();
	volk_32f_x2_interleave_32fc(out, i, q, items_to_handle);
#endif
    if (g_samples - g_samples % 5000000 > g_lastsamples) {
    	g_lastsamples = g_samples;
    	sprintf(m_pr_buffer, "Receive stream alive - active elements in ring buffer: %d MaxR %ld MaxX %ld", cb_size, g_r, g_x);
    	GR_LOG_INFO(d_logger, m_pr_buffer);
    }

	// Tell runtime system how many output items we produced.
	// return noutput_items;
	return items_to_handle;
}
} /* namespace msz */
} /* namespace gr */


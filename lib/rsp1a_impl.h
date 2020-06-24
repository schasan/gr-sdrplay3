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

#ifndef INCLUDED_MSZ_RSP1A_IMPL_H
#define INCLUDED_MSZ_RSP1A_IMPL_H

#include <msz/rsp1a.h>
#include <volk/volk.h>
#include "sdrplay_api.h"
#include <boost/circular_buffer.hpp>
#include <boost/thread/mutex.hpp>

namespace gr {
  namespace msz {

    class rsp1a_impl : public rsp1a
    {
     private:
      long m_toggle = 0;
      float m_ver;
      sdrplay_api_DeviceT m_devs[6];
      unsigned int m_ndev;
      sdrplay_api_DeviceT *m_chosenDevice = NULL;
      sdrplay_api_ErrT m_err;
      static const int buffersize = 132;
      char m_pr_buffer[buffersize];
      unsigned int m_chosenIdx = 0;
      bool m_master_slave = false;
      sdrplay_api_CallbackFnsT m_cbFns;
      sdrplay_api_DeviceParamsT *m_deviceParams = NULL;
      sdrplay_api_RxChannelParamsT *m_chParams;
      int m_gain = 40;
      float m_freq = 89300000.0;

     public:
      rsp1a_impl(float frequency, long sample_rate, float gain);
      ~rsp1a_impl();
      void set_frequency(float freq);
      void set_gain(int gain);
      void set_sample_rate(long sample_rate);

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace msz
} // namespace gr

#endif /* INCLUDED_MSZ_RSP1A_IMPL_H */


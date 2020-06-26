#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Morse reception
# Author: Mario Schulz
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import msz

from gnuradio import qtgui

class CW_Rec(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Morse reception")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Morse reception")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "CW_Rec")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 50
        self.samp_rate = samp_rate = 2e6
        self.gain = gain = 40
        self.frequency = frequency = 144475e3

        ##################################################
        # Blocks
        ##################################################
        self._gain_range = Range(20, 59, 1, 40, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, 'Gain', "counter_slider", int)
        self.top_grid_layout.addWidget(self._gain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._frequency_options = (144475e3, 89.3e6, )
        # Create the labels list
        self._frequency_labels = ('Bake Feldberg', 'hr3', )
        # Create the combo box
        # Create the radio buttons
        self._frequency_group_box = Qt.QGroupBox('Frequenz' + ": ")
        self._frequency_box = Qt.QVBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._frequency_button_group = variable_chooser_button_group()
        self._frequency_group_box.setLayout(self._frequency_box)
        for i, _label in enumerate(self._frequency_labels):
            radio_button = Qt.QRadioButton(_label)
            self._frequency_box.addWidget(radio_button)
            self._frequency_button_group.addButton(radio_button, i)
        self._frequency_callback = lambda i: Qt.QMetaObject.invokeMethod(self._frequency_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._frequency_options.index(i)))
        self._frequency_callback(self.frequency)
        self._frequency_button_group.buttonClicked[int].connect(
            lambda i: self.set_frequency(self._frequency_options[i]))
        self.top_grid_layout.addWidget(self._frequency_group_box, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._volume_range = Range(0, 100, 1, 50, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "counter_slider", float)
        self.top_grid_layout.addWidget(self._volume_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=441,
                decimation=100,
                taps=None,
                fractional_bw=None)
        self.qtgui_waterfall_sink_x_1 = qtgui.waterfall_sink_c(
            128, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            1000, #bw
            "", #name
            1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_1.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_1.enable_grid(False)
        self.qtgui_waterfall_sink_x_1.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_1.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_1.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_1.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_1_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_1_win, 1, 0, 6, 3)
        for r in range(1, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.msz_rsp1a_0 = msz.rsp1a(frequency, samp_rate, gain)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.band_pass_filter_0 = filter.fir_filter_ccf(
            200,
            firdes.band_pass(
                1,
                samp_rate,
                50,
                500,
                50,
                firdes.WIN_HAMMING,
                6.76))
        self.audio_sink_0 = audio.sink(44100, '', True)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter_0, 0), (self.qtgui_waterfall_sink_x_1, 0))
        self.connect((self.band_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.audio_sink_0, 0))
        self.connect((self.msz_rsp1a_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_real_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "CW_Rec")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, 50, 500, 50, firdes.WIN_HAMMING, 6.76))
        self.msz_rsp1a_0.set_sample_rate(self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.msz_rsp1a_0.set_gain(self.gain)

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self._frequency_callback(self.frequency)
        self.msz_rsp1a_0.set_frequency(self.frequency)





def main(top_block_cls=CW_Rec, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()

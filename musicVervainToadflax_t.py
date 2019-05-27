#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Musicvervaintoadflax T
# Generated: Mon May 27 09:58:48 2019
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import Music
import custom
import sip
import sys
import time
from gnuradio import qtgui
import threading


# Event to shut down thread if exitThread.is_set()
exitThread = threading.Event()
exitThread.clear()


class musicVervainToadflax_t(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Musicvervaintoadflax T")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Musicvervaintoadflax T")
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

        self.settings = Qt.QSettings("GNU Radio", "musicVervainToadflax_t")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.freq = freq = 2.5e9

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(("addr0=192.168.192.40, addr1=192.168.192.41", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(4),
        	),
        )
        self.uhd_usrp_source_0.set_clock_source('external', 0)
        self.uhd_usrp_source_0.set_time_source('external', 0)
        self.uhd_usrp_source_0.set_clock_source('external', 1)
        self.uhd_usrp_source_0.set_time_source('external', 1)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(10, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_source_0.set_center_freq(freq, 1)
        self.uhd_usrp_source_0.set_gain(10, 1)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 1)
        self.uhd_usrp_source_0.set_center_freq(freq, 2)
        self.uhd_usrp_source_0.set_gain(10, 2)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 2)
        self.uhd_usrp_source_0.set_center_freq(freq, 3)
        self.uhd_usrp_source_0.set_gain(10, 3)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 3)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1
        )
        self.qtgui_number_sink_0.set_update_time(0.10)
        self.qtgui_number_sink_0.set_title("")

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        units = ['', '', '', '', '',
                 '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
                  ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        for i in xrange(1):
            self.qtgui_number_sink_0.set_min(i, -1)
            self.qtgui_number_sink_0.set_max(i, 1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0.enable_autoscale(False)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_win)
        self.custom_Arg_to_Complex_0_1 = custom.Arg_to_Complex()
        self.custom_Arg_to_Complex_0_0 = custom.Arg_to_Complex()
        self.custom_Arg_to_Complex_0 = custom.Arg_to_Complex()
        self.blocks_multiply_xx_0_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vff((-1, ))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vff((-1, ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((-1, ))
        self.analog_const_source_x_0_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 5.79)
        self.analog_const_source_x_0_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 5.79)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 5.79)
        self.Music_music_0 = Music.music(4, 30000, 1, 0.06, freq/1e6, 0.01)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.Music_music_0, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_const_source_x_0_1, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.custom_Arg_to_Complex_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.custom_Arg_to_Complex_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.custom_Arg_to_Complex_0_1, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.Music_music_0, 1))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.Music_music_0, 3))
        self.connect((self.blocks_multiply_xx_0_1, 0), (self.Music_music_0, 2))
        self.connect((self.custom_Arg_to_Complex_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.custom_Arg_to_Complex_0_0, 0), (self.blocks_multiply_xx_0_1, 1))
        self.connect((self.custom_Arg_to_Complex_0_1, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.uhd_usrp_source_0, 0), (self.Music_music_0, 0))
        self.connect((self.uhd_usrp_source_0, 1), (self.blocks_multiply_xx_0, 0))
        self.connect((self.uhd_usrp_source_0, 3), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 2), (self.blocks_multiply_xx_0_1, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "musicVervainToadflax_t")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 1)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 2)
        self.uhd_usrp_source_0.set_center_freq(self.freq, 3)


# Function to shut down GNU Radio app
def shutDown(qapp):
    while True:
        if (exitThread.is_set()):
            qapp.quit()
            break
        else:
            time.sleep(1)

def main(top_block_cls=musicVervainToadflax_t, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    threading.Thread(target = shutDown, args=(qapp,)).start()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()

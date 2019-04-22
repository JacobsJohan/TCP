#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Musicvervaintoadflax
# Generated: Thu Apr 11 10:42:18 2019
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
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import custom
import musicToFile
import sys
import time
from gnuradio import qtgui
import threading


# Event to shut down thread if exitThread.is_set()
exitThread = threading.Event()
exitThread.clear()


class musicVervainToadflax(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Musicvervaintoadflax")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Musicvervaintoadflax")
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

        self.settings = Qt.QSettings("GNU Radio", "musicVervainToadflax")
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
        self.musicToFile_musicToFile_0 = musicToFile.musicToFile(4, 200000, 1, 0.06, freq/1e6)
        self.custom_Arg_to_Complex_2 = custom.Arg_to_Complex()
        self.custom_Arg_to_Complex_1 = custom.Arg_to_Complex()
        self.custom_Arg_to_Complex_0 = custom.Arg_to_Complex()
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_2 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_1 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_vff((-1, ))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vff((-1, ))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((-1, ))
        self.analog_const_source_x_0_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 5.56)
        self.analog_const_source_x_0_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 6.06)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 5.79)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_const_source_x_0_1, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.custom_Arg_to_Complex_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.custom_Arg_to_Complex_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.custom_Arg_to_Complex_2, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.musicToFile_musicToFile_0, 1))
        self.connect((self.blocks_multiply_xx_1, 0), (self.musicToFile_musicToFile_0, 3))
        self.connect((self.blocks_multiply_xx_2, 0), (self.musicToFile_musicToFile_0, 2))
        self.connect((self.custom_Arg_to_Complex_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.custom_Arg_to_Complex_1, 0), (self.blocks_multiply_xx_2, 1))
        self.connect((self.custom_Arg_to_Complex_2, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.musicToFile_musicToFile_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 1), (self.blocks_multiply_xx_0, 0))
        self.connect((self.uhd_usrp_source_0, 3), (self.blocks_multiply_xx_1, 0))
        self.connect((self.uhd_usrp_source_0, 2), (self.blocks_multiply_xx_2, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.musicToFile_musicToFile_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "musicVervainToadflax")
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


def main(top_block_cls=musicVervainToadflax, options=None):

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

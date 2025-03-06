#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: gr_ble_adv_tx
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import soapy
import threading




class gr_ble_adv_tx(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "gr_ble_adv_tx", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.tx_freq = tx_freq = 2402000000
        self.samp_rate = samp_rate = 4e6
        self.channel = channel = 37

        ##################################################
        # Blocks
        ##################################################

        self.soapy_plutosdr_sink_0 = None
        dev = 'driver=plutosdr'
        stream_args = ''
        tune_args = ['']
        settings = ['']

        self.soapy_plutosdr_sink_0 = soapy.sink(dev, "fc32", 1, '',
                                  stream_args, tune_args, settings)
        self.soapy_plutosdr_sink_0.set_sample_rate(0, samp_rate)
        self.soapy_plutosdr_sink_0.set_bandwidth(0, 0.0)
        self.soapy_plutosdr_sink_0.set_frequency(0, tx_freq)
        self.soapy_plutosdr_sink_0.set_gain(0, min(max(89, 0.0), 89.0))
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, 'normalization_sample.bin', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.intern("Begin"))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.soapy_plutosdr_sink_0, 0))


    def get_tx_freq(self):
        return self.tx_freq

    def set_tx_freq(self, tx_freq):
        self.tx_freq = tx_freq
        self.soapy_plutosdr_sink_0.set_frequency(0, self.tx_freq)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.soapy_plutosdr_sink_0.set_sample_rate(0, self.samp_rate)

    def get_channel(self):
        return self.channel

    def set_channel(self, channel):
        self.channel = channel




def main(top_block_cls=gr_ble_adv_tx, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()

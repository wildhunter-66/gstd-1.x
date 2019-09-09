#!/usr/bin/env python3
import unittest
import gstc

class TestGstcDebugThresholdMethods(unittest.TestCase):
    def test_debug_threshold_none(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("0")

    def test_debug_threshold_error(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("1")

    def test_debug_threshold_warning(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("2")

    def test_debug_threshold_fixme(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("3")

    def test_debug_threshold_info(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("4")

    def test_debug_threshold_debug(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("5")

    def test_debug_threshold_log(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("6")

    def test_debug_threshold_trace(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("7")

    def test_debug_threshold_memdump(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("8")

    def test_debug_threshold_invalid(self):
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.gstd_client.debug_threshold("9")
if __name__ == '__main__':
    unittest.main()

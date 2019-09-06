#!/usr/bin/env python3
import unittest
import threading
import gstc
import time
import os

ret_val=""

def signal_connect_test():
    global ret_val
    gstd_client = gstc.client(loglevel='DEBUG', port=5001)
    ret_val = gstd_client.signal_connect("p0", "identity", "handoff")

class TestGstcSignalDisconnectMethods(unittest.TestCase):

    def test_libgstc_python_signal_disconnect(self):
        global ret_val
        pipeline = "videotestsrc ! identity name=identity ! fakesink"
        self.gstd_client = gstc.client(loglevel='DEBUG')
        self.assertEqual(self.gstd_client.pipeline_create ("p0", pipeline), 0)
        ret_thr = threading.Thread(target=signal_connect_test)
        ret_thr.start()
        time.sleep(1)
        self.assertEqual(self.gstd_client.signal_disconnect("p0", "identity", "handoff"), 0)
        time.sleep(1)
        self.assertEqual(ret_val['response'], None)
        self.assertEqual(self.gstd_client.pipeline_stop ("p0"), 0)
        self.assertEqual(self.gstd_client.pipeline_delete ("p0"), 0)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
# GStreamer Daemon - gst-launch on steroids
# Python client library abstracting gstd interprocess communication

# Copyright (c) 2015-2019 RidgeRun, LLC (http://www.ridgerun.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from pygstc.gstc import *
from pygstc.logger import *

class TestGstcCreateMethods(unittest.TestCase):

    def test_create_pipeline(self):
        pipeline = "videotestsrc name=v0 ! fakesink"
        self.gstd_logger = CustomLogger("test_libgstc", loglevel='DEBUG')
        self.gstd_client = GstdClient(logger=self.gstd_logger)
        ret = self.gstd_client.read("pipelines")
        initial_n_pipes = len(ret['nodes'])
        self.gstd_client.create ("pipelines", "p0", pipeline)
        ret = self.gstd_client.read("pipelines")
        final_n_pipes = len(ret['nodes'])
        self.assertEqual(final_n_pipes, initial_n_pipes+1)
        self.gstd_client.pipeline_delete ("p0")

if __name__ == '__main__':
    unittest.main()

# GStreamer Daemon - gst-launch on steroids
# Python client library abstracting gstd interprocess communication

# Copyright (c) 2015-2020 RidgeRun, LLC (http://www.ridgerun.com)

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

import json
import psutil
import traceback

from pygstc.gstcerror import *
from pygstc.logger import *
from pygstc.tcp import *

GSTD_PROCNAME = 'gstd'

"""
GSTC - GstdClient Class
"""


class GstdClient:

    """
    Class used as client to comunicate with the GStreamer Daemon over
    an abstract inter-process communication class.

    Methods
    ----------
    bus_filter(pipe_name, filter)
        Select the types of message to be read from the bus. Separate
        with a '+', i.e.: eos+warning+error
    bus_read(pipe_name)
        Read the bus and wait
    bus_timeout(pipe_name, timeout)
        Apply a timeout for the bus polling. -1: forever, 0: return
        immediately, n: wait n nanoseconds
    create(uri, property, value)
        Create a resource at the given URI
    debug_color(colors)
        Enable/Disable colors in the debug logging
    debug_enable(enable)
        Enable/Disable GStreamer debug
    debug_reset(reset)
        Enable/Disable debug threshold reset
    debug_threshold(threshold)
        The debug filter to apply (as you would use with gst-launch)
    delete(uri, name)
        Delete the resource held at the given URI with the given name
    element_get(pipe_name, element, prop)
        Queries a property in an element of a given pipeline
    element_set(pipe_name, element, prop, value)
        Set a property in an element of a given pipeline
    event_eos(pipe_name)
        Send an end-of-stream event
    event_flush_start(pipe_name)
        Put the pipeline in flushing mode
    event_flush_stop(pipe_name, reset='true')
        Take the pipeline out from flushing mode
    event_seek(
        self,
        pipe_name,
        rate='1.0',
        format='3',
        flags='1',
        start_type='1',
        start='0',
        end_type='1',
        end='-1',
        )
        Perform a seek in the given pipeline
    list_elements(pipe_name)
        List the elements in a given pipeline
    list_pipelines( )
        List the existing pipelines
    list_properties(pipe_name, element)
        List the properties of an element in a given pipeline
    list_signals(pipe_name, element)
        List the signals of an element in a given pipeline
    pipeline_create(pipe_name,  pipe_desc)
        Create a new pipeline based on the name and description
    pipeline_delete(pipe_name)
        Delete the pipeline with the given name
    pipeline_pause(pipe_name)
        Set the pipeline to paused
    pipeline_play(pipe_name)
        Set the pipeline to playing
    pipeline_stop(pipe_name)
        Set the pipeline to null
    read(uri)
        Read the resource held at the given URI with the given name
    signal_connect(pipe_name, element, signal)
        Connect to signal and wait
    signal_disconnect(pipe_name, element, signal)
        Disconnect from signal
    signal_timeout(pipe_name, element, signal, timeout)
        Apply a timeout for the signal waiting. -1: forever, 0: return
        immediately, n: wait n microseconds
    update(uri, value)
        Update the resource at the given URI
    """

    def __init__(
        self,
        ip='localhost',
        port=5000,
        logger=None,
        timeout=0,
    ):
        """
        Initialize new GstdClient.

        Parameters
        ----------
        ip : string
            IP where GSTD is running
        port : string
            Port where GSTD is running
        logger : CustomLogger
            Custom logger where all log messages from this class are going
            to be reported
        """

        if logger:
            self._logger = logger
        else:
            self._logger = DummyLogger()
        self._ip = ip
        self._port = port
        self._logger.info('Starting GStreamer Daemon Client with ip=%s port=%d'
                          % (self._ip, self._port))
        self._test_gstd()
        self._ipc = Ipc(self._logger, self._ip, self._port)
        self._timeout = timeout

    def _send_cmd_line(self, cmd_line):
        """
        Send a command using an abstract IPC and wait for the response.

        Parameters
        ----------
        cmd_line : string list
            Command to be send

        Raises
        ------
        GstdError
            Error is triggered when Gstd IPC fails
        GstcError
            Error is triggered when the Gstd python client fails internally

        Returns
        -------
        result : dictionary
            Response from the IPC
        """

        cmd = cmd_line[0]
        try:
            jresult = self._ipc.send(cmd_line, timeout=self._timeout)
            result = json.loads(jresult)
        except Exception as exception:
            self._logger.error('%s error: %s' % (cmd,
                                                 type(exception).__name__))
            traceback.print_exc()
            raise GstcError(type(exception).__name__)
        if result['code'] != 0:
            self._logger.error('%s error: %s' % (cmd,
                                                 result['description']))
            raise GstdError(result['description'])
        return result

    def _test_gstd(self):
        """
        Test if GSTD is running (only works for localhost)

        Returns
        -------
        result : bool
            Whether or not GSTD is running in localhost
        """

        if self._ip not in ['localhost', '127.0.0.1']:

            # bypass process check, we don't know how to start gstd remotely

            self._logger.warning(
                'Assuming GSTD is running in the remote host at %s' %
                self._ip)
            return True
        for proc in psutil.process_iter():

            # check whether the process name matches

            if proc.name() == GSTD_PROCNAME:
                return True
            else:
                self._logger.error('GStreamer Daemon is not running')
                return False

    def bus_filter(self, pipe_name, filter):
        """
        Select the types of message to be read from the bus. Separate
        with a '+', i.e.: eos+warning+error.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        filter: string
            Filter to be applied to the bus. '+' reparated strings
        """

        self._logger.info('Setting bus read filter of pipeline %s to %s'
                          % (pipe_name, filter))
        self._send_cmd_line(['bus_filter', pipe_name, filter])

    def bus_read(self, pipe_name):
        """
        Read the bus and wait.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline

        Returns
        -------
        result : dictionary
            Command response
        """

        self._logger.info('Reading bus of pipeline %s' % pipe_name)
        result = self._send_cmd_line(['bus_read', pipe_name])
        return result['response']

    def bus_timeout(self, pipe_name, timeout):
        """
        Apply a timeout for the bus polling.
        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        timeout: string
            Timeout in nanosecons. -1: forever, 0: return
            immediately, n: wait n nanoseconds.
        """

        self._logger.info('Setting bus read timeout of pipeline %s to %s'
                          % (pipe_name, timeout))
        self._send_cmd_line(['bus_timeout', pipe_name, timeout])

    def create(
        self,
        uri,
        property,
        value,
    ):
        """
        Create a resource at the given URI.

        Parameters
        ----------
        uri: string
            Resource identifier
        property: string
            The name of the property
        value: string
            The initial value to be set
        """

        self._logger.info('Creating property %s in uri %s with value "%s"'
                          % (property, uri, value))
        self._send_cmd_line(['create', uri, property, value])

    def debug_color(self, colors):
        """
        Enable/Disable colors in the debug logging.

        Parameters
        ----------
        colors: string
            Enable color in the debug: 'true' or 'false'
        """

        self._logger.info('Enabling/Disabling GStreamer debug colors')
        self._send_cmd_line(['debug_color', colors])

    def debug_enable(self, enable):
        """
        Enable/Disable GStreamer debug.

        Parameters
        ----------
        enable: string
            Enable GStreamer debug: 'true' or 'false'
        """

        self._logger.info('Enabling/Disabling GStreamer debug')
        self._send_cmd_line(['debug_enable', enable])

    def debug_reset(self, reset):
        """
        Enable/Disable debug threshold reset.

        Parameters
        ----------
        reset: string
            Reset the debug threshold: 'true' or 'false'
        """

        self._logger.info('Enabling/Disabling GStreamer debug threshold reset')
        self._send_cmd_line(['debug_reset', reset])

    def debug_threshold(self, threshold):
        """
        The debug filter to apply (as you would use with gst-launch).

        Parameters
        ----------
        threshold: string
            Debug threshold:
            0   none    No debug information is output.
            1   ERROR   Logs all fatal errors.
            2   WARNING Logs all warnings.
            3   FIXME   Logs all "fixme" messages.
            4   INFO    Logs all informational messages.
            5   DEBUG   Logs all debug messages.
            6   LOG     Logs all log messages.
            7   TRACE   Logs all trace messages.
            9   MEMDUMP Logs all memory dump messages.
        """

        self._logger.info('Setting GStreamer debug threshold to %s'
                          % threshold)
        self._send_cmd_line(['debug_threshold', threshold])

    def delete(self, uri, name):
        """
        Delete the resource held at the given URI with the given name.

        Parameters
        ----------
        uri: string
            Resource identifier
        name: string
            The name of the resource to delete
        """

        self._logger.info('Deleting name %s at uri "%s"' % (name, uri))
        self._send_cmd_line(['delete', uri, name])

    def element_get(
        self,
        pipe_name,
        element,
        prop,
    ):
        """
        Queries a property in an element of a given pipeline.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element
        prop: string
            The name of the property

        Returns
        -------
        result : string
            Command response
        """

        self._logger.info(
            'Getting value of element %s %s property in pipeline %s' %
            (element, prop, pipe_name))
        result = self._send_cmd_line(cmd_line=['element_get',
                                               pipe_name, element, prop])
        return result['response']['value']

    def element_set(
        self,
        pipe_name,
        element,
        prop,
        value,
    ):
        """
        Set a property in an element of a given pipeline.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element
        prop: string
            The name of the property
        value: string
            The value to set
        """

        self._logger.info('Setting element %s %s property in pipeline %s to:%s'
                          % (element, prop, pipe_name, value))
        self._send_cmd_line(['element_set', pipe_name, element, prop,
                             value])

    def event_eos(self, pipe_name):
        """
        Send an end-of-stream event.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        """

        self._logger.info('Sending end-of-stream event to pipeline %s'
                          % pipe_name)
        self._send_cmd_line(['event_eos', pipe_name])

    def event_flush_start(self, pipe_name):
        """
        Put the pipeline in flushing mode.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        """

        self._logger.info('Putting pipeline %s in flushing mode'
                          % pipe_name)
        self._send_cmd_line(['event_flush_start', pipe_name])

    def event_flush_stop(self, pipe_name, reset='true'):
        """
        Take the pipeline out from flushing mode.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        reset: string
            Reset the event flush: 'true' or 'false'
        """

        self._logger.info('Taking pipeline %s out of flushing mode'
                          % pipe_name)
        self._send_cmd_line(['event_flush_stop', pipe_name, reset])

    def event_seek(
        self,
        pipe_name,
        rate='1.0',
        format='3',
        flags='1',
        start_type='1',
        start='0',
        end_type='1',
        end='-1',
    ):
        """
        Perform a seek in the given pipeline

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        rate: string
            The new playback rate. Default value: '1.0'.
        format: string
            The format of the seek values. Default value: '3'.
        flags: string
            The optional seek flags. Default value: '1'.
        start_type: string
            The type and flags for the new start position. Default value: '1'.
        start: string
            The value of the new start position. Default value: '0'.
        end_type: string
            The type and flags for the new end position. Default value: '1'.
        end: string
            The value of the new end position. Default value: '-1'.
        """

        self._logger.info('Performing event seek in pipeline %s'
                          % pipe_name)
        self._send_cmd_line([
            'event_seek',
            pipe_name,
            rate,
            format,
            flags,
            start_type,
            start,
            end_type,
            end,
        ])

    def list_elements(self, pipe_name):
        """
        List the elements in a given pipeline.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline

        Returns
        -------
        result : string
            List of elements
        """

        self._logger.info('Listing elements of pipeline %s' % pipe_name)
        result = self._send_cmd_line(cmd_line=['list_elements',
                                               pipe_name])
        return result['response']['nodes']

    def list_pipelines(self):
        """
        List the existing pipelines
        """

        self._logger.info('Listing pipelines')
        result = self._send_cmd_line(cmd_line=['list_pipelines'])
        return result['response']['nodes']

    def list_properties(self, pipe_name, element):
        """
        List the properties of an element in a given pipeline.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element

        Returns
        -------
        result : string
            List of properties
        """

        self._logger.info('Listing properties of  element %s from pipeline %s'
                          % (element, pipe_name))
        result = self._send_cmd_line(['list_properties', pipe_name,
                                      element])
        return result['response']['nodes']

    def list_signals(self, pipe_name, element):
        """
        List the signals of an element in a given pipeline.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element

        Returns
        -------
        result : string
            List of signals
        """

        self._logger.info('Listing signals of  element %s from pipeline %s'
                          % (element, pipe_name))
        result = self._send_cmd_line(['list_signals', pipe_name,
                                      element])
        return result['response']['nodes']

    def pipeline_create(self, pipe_name, pipe_desc):
        """
        Create a new pipeline based on the name and description.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        pipe_desc: string
            Pipeline description (same as gst-launch-1.0)
        """

        self._logger.info('Creating pipeline %s with description "%s"'
                          % (pipe_name, pipe_desc))
        self._send_cmd_line(['pipeline_create', pipe_name, pipe_desc])

    def pipeline_delete(self, pipe_name):
        """
        Delete the pipeline with the given name.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        """

        self._logger.info('Deleting pipeline %s' % pipe_name)
        self._send_cmd_line(['pipeline_delete', pipe_name])

    def pipeline_pause(self, pipe_name):
        """
        Set the pipeline to paused.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        """

        self._logger.info('Pausing pipeline %s' % pipe_name)
        self._send_cmd_line(['pipeline_pause', pipe_name])

    def pipeline_play(self, pipe_name):
        """
        Set the pipeline to playing.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        """

        self._logger.info('Playing pipeline %s' % pipe_name)
        self._send_cmd_line(['pipeline_play', pipe_name])

    def pipeline_stop(self, pipe_name):
        """
        Set the pipeline to null.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        """

        self._logger.info('Stoping pipeline %s' % pipe_name)
        self._send_cmd_line(['pipeline_stop', pipe_name])

    def read(self, uri):
        """
        Read the resource held at the given URI with the given name.

        Parameters
        ----------
        uri: string
            Resource identifier

        Returns
        -------
        result : string
            Command response
        """

        self._logger.info('Reading uri %s' % uri)
        result = self._send_cmd_line(['read', uri])
        return result['response']

    def signal_connect(
        self,
        pipe_name,
        element,
        signal,
    ):
        """
        Connect to signal and wait.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element
        signal: string
            The name of the signal

        Returns
        -------
        result : string
            Command response
        """

        self._logger.info(
            'Connecting to signal %s of element %s from pipeline %s' %
            (signal, element, pipe_name))
        result = self._send_cmd_line(['signal_connect', pipe_name,
                                      element, signal])
        return result['response']

    def signal_disconnect(
        self,
        pipe_name,
        element,
        signal,
    ):
        """
        Disconnect from signal.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element
        signal: string
            The name of the signal
        """

        self._logger.info(
            'Disonnecting from signal %s of element %s from pipeline %s' %
            (signal, element, pipe_name))
        self._send_cmd_line(['signal_disconnect', pipe_name, element,
                             signal])

    def signal_timeout(
        self,
        pipe_name,
        element,
        signal,
        timeout,
    ):
        """
        Apply a timeout for the signal waiting. -1: forever, 0: return
        immediately, n: wait n microseconds.

        Parameters
        ----------
        pipe_name: string
            The name of the pipeline
        element: string
            The name of the element
        signal: string
            The name of the signal
        timeout: string
            Timeout in nanosecons. -1: forever. 0: return
        """

        self._logger.info(
            'Connecting to signal %s of element %s from pipeline %s with timeout %s' %
            (signal, element, pipe_name, timeout))
        self._send_cmd_line(['signal_timeout', pipe_name, element,
                             signal, timeout])

    def update(self, uri, value):
        """
        Update the resource at the given URI.

        Parameters
        ----------
        uri: string
            Resource identifier
        value: string
            The value to set
        """

        self._logger.info('Updating uri %s with value "%s"' % (uri,
                                                               value))
        self._send_cmd_line(['update', uri, value])

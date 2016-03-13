#!/usr/bin/env python
#
# Copyright (c) 2016, Nimbix, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Nimbix, Inc.
#
# Author: Stephen Fox (stephen.fox@nimbix.net)

import requests
import json
import logging


class Client(object):
    """Static class for making API calls to JARVICE.  Credentials are
    inserted to the payload by passing as parameters to the
    classmethods.
    """
    BASE_URL = 'https://api.jarvice.com'

    COMPLETED_STATUSES = ['completed', 'completed with error', 'terminated',
                          'canceled']

    @classmethod
    def shutdown(cls, username, apikey, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/shutdown'
        params = {}

        if not name and not number:
            raise Exception("Job 'name' or 'number' must be specified")

        params = {
            'username': username,
            'apikey': apikey
        }
        if name:
            params.update({'name': name})
        else:
            params.update({'number': number})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def machines(cls, username, apikey, name=None):
        method = 'GET'
        endpoint = '/jarvice/machines'
        params = {}

        params = {
            'username': username,
            'apikey': apikey,
        }
        if name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def apps(cls, username, apikey, name=None):
        method = 'GET'
        endpoint = '/jarvice/apps'
        params = {}

        params = {
            'username': username,
            'apikey': apikey
        }
        if name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def action(cls, username, apikey, action, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/action'
        params = {
            'username': username,
            'apikey': apikey,
            'action': action
        }
        if number:
            params.update({'number': number})
        elif name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def terminate(cls, username, apikey, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/terminate'
        params = {}

        if not name and not number:
            raise Exception("Job 'name' or 'number' must be specified")

        params = {
            'username': username,
            'apikey': apikey
        }
        if number:
            params.update({'number': number})
        elif name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def status(cls, username, apikey, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/status'
        params = {}

        if not name and not number:
            raise Exception("Job 'name' or 'number' must be specified")

        params = {
            'username': username,
            'apikey': apikey
        }
        if number:
            params.update({'number': number})
        elif name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def info(cls, username, apikey, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/info'
        params = {}

        if not name and not number:
            raise Exception("Job 'name' or 'number' must be specified")

        params = {
            'username': username,
            'apikey': apikey
        }
        if number:
            params.update({'number': number})
        elif name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def submit(cls, username, apikey, job):
        method = 'POST'
        endpoint = '/jarvice/submit'
        params = job

        # Add API credentials
        if 'user' not in params:
            params.update({
                'user': {
                    'username': username,
                    'apikey': apikey
                }
            })
        return cls._call_api(method, endpoint, params)

    @classmethod
    def connect(cls, username, apikey, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/connect'
        params = {
            'username': username,
            'apikey': apikey,
        }
        if number is not None:
            params.update({'number': number})
        elif name is not None:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def jobs(cls, username, apikey, name=None):
        method = 'GET'
        endpoint = '/jarvice/jobs'
        params = {
            'username': username,
            'apikey': apikey,
        }
        if name:
            params.update({'name': name})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def output(cls, username, apikey, lines=None, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/output'
        params = {
            'username': username,
            'apikey': apikey
        }
        if number:
            params.update({'number': number})
        elif name:
            params.update({'name': name})
        if lines:
            params.update({'lines': lines})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def tail(cls, username, apikey, lines=None, number=None, name=None):
        method = 'GET'
        endpoint = '/jarvice/tail'
        params = {
            'username': username,
            'apikey': apikey
        }
        if number:
            params.update({'number': number})
        elif name:
            params.update({'name': name})
        if lines:
            params.update({'lines': lines})
        return cls._call_api(method, endpoint, params)

    @classmethod
    def _call_api(cls, method, endpoint, params):
        """API Call wrapper for endpoints with application/json return types

        Args:
          method(str): one of 'GET' or 'POST'
          endpoint(str): Jarvice endpoint, e.g., '/jarvice/jobs'
          params(dict): Python dictionary of params to pass in API call
        """
        result = None
        api_result = {}
        errors = None

        if method == 'GET':
            result = requests.get(cls.BASE_URL+endpoint, params=params)
        elif method == 'POST':
            result = requests.post(cls.BASE_URL+endpoint, json=params)
        else:
            raise Exception("Method %(method)s is not implemented" %
                            {'method': method})

        if result is not None:
            if result.status_code >= 300:
                logging.error("Failure to retrieve API data: %s" % (endpoint))
                logging.error("Job payload: %s" % params)
                logging.error("Status code: %s" % (result.status_code))
                errors = {'error': {
                    'code': result.status_code,
                }}
            content_type = result.headers.pop('content-type', '')
            if content_type == 'application/json':
                api_result = json.loads(result.text)
            elif content_type == 'text/plain':
                api_result = result.text
            else:
                if 'error' not in errors:
                    errors.update({'error': {}})
                errors['error'].update({'message': "Unknown content type (%s)"
                                        % content_type})
                logging.error("Unknown content type (%s)" % content_type)
        return (api_result, errors)


class AuthenticatedClient(object):
    """Set the credentials in the constructor and make calls
    to the Jarvice API. Even though it is a client, it is sessionless
    since it is calling HTTP endpoints of https://api.jarvice.com
    """
    def __init__(self, username, apikey):
        self.username = username
        self.apikey = apikey

    def connect(self, *args, **kwargs):
        return Client.connect(self.username, self.apikey,
                              *args, **kwargs)

    def submit(self, *args, **kwargs):
        return Client.submit(self.username, self.apikey,
                             *args, **kwargs)

    def machines(self, *args, **kwargs):
        return Client.machines(self.username, self.apikey,
                               *args, **kwargs)

    def apps(self, *args, **kwargs):
        return Client.apps(self.username, self.apikey,
                           *args, **kwargs)

    def info(self, *args, **kwargs):
        return Client.info(self.username, self.apikey,
                           *args, **kwargs)

    def status(self, *args, **kwargs):
        return Client.status(self.username, self.apikey,
                             *args, **kwargs)

    def action(self, *args, **kwargs):
        return Client.action(self.username, self.apikey,
                             *args, **kwargs)

    def terminate(self, *args, **kwargs):
        return Client.terminate(self.username, self.apikey,
                                *args, **kwargs)

    def shutdown(self, *args, **kwargs):
        return Client.shutdown(self.username, self.apikey,
                               *args, **kwargs)

    def jobs(self, *args, **kwargs):
        return Client.jobs(self.username, self.apikey,
                           *args, **kwargs)

    def output(self, *args, **kwargs):
        return Client.output(self.username, self.apikey,
                             *args, **kwargs)

    def tail(self, *args, **kwargs):
        return Client.tail(self.username, self.apikey,
                           *args, **kwargs)

    def terminate_all(self, *args, **kwargs):
        jobs, error = self.jobs(*args, **kwargs)
        killed = []
        errors = []
        for job_number, job in jobs.iteritems():
            result, error = self.terminate(number=job_number)
            if error:
                errors.append({'number': error})
            killed.append({'number': job_number, 'result': result})
        return killed, errors

    def shutdown_all(self, *args, **kwargs):
        jobs, errors = self.jobs(*args, **kwargs)
        killed = []
        errors = []
        for job_number, job in jobs.iteritems():
            result, error = self.shutdown(number=job_number)
            if error:
                errors.append({'number': error})
            killed.append({'number': job_number, 'result': result})
        return killed, errors


if __name__ == '__main__':
    print "Jarvice API Python Client for running on-demand HPC work flows."
    print "This client calls https://api.jarvice.com"

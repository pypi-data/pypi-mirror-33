#!/usr/bin/env python

import os
import json
import logging
import requests


class XNATException(Exception):
    '''
    XNAT-specific Exception class for handling library-related errors
    '''
    pass


class Connection(object):
    '''
    Class with set of functionalities for interfacing/communicating with XNAT using REST API
    To instantiate properly, provide: XNAT hostname (URL), credentials (either sessionID token or basic auth. credentials)
    Note I: that a valid XNAT account is required to interface with the XNAT
    Note II: Support for self-signed SSL certificates provided (unverified_context)
    '''
    def __init__(self, hostname, credentials, verify=True, verbose=True):

        self.host = self.normalize_URL(hostname)
        self.verbose = verbose
        self.verified_SSL_context = verify

        if not verify :
            # Suppress warning messages which may get quite annoying
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # credentials handling
        self.jsession_id = None
        if isinstance(credentials, tuple) and len(credentials) == 2:
            # Basic HTTP auth. method
            self.jsession_id = {"JSESSIONID": self.open_jsession(credentials)}
        elif isinstance(credentials, basestring) :
            # jsessionID token auth. method
            self.jsession_id = {"JSESSIONID": credentials}

        if self.jsession_id :
            if self.resource_exist(self.host).status_code != requests.codes.ok:
                logging.error('Unable to connect to server %s, check credentials and/or server availability.' %self.host)
            else :
                logging.info('Connected to server %s' % self.host)
        else :
            logging.warning('No credentials provided, offline connection')


    def __enter__(self):

        return self


    def __exit__(self, type, value, traceback):

        if self.jsession :
            self.close_jsession()


    def normalize_URL(self, url):
        '''
        Helper to check if the given URL ends or not with an slash char
        :return: A normalized URL string
        '''

        return url.strip('/')


    def open_jsession(self, credentials):
        '''
        Authenticates and returns a jsessionID token
        '''

        URL = self.host + '/data/JSESSION'

        response = requests.post(URL, auth=(credentials[0], credentials[1]),
                                 verify=self.verified_SSL_context, timeout=10)

        if response.status_code != requests.codes.ok:
            raise XNATException('HTTP response: #%s' % response.status_code)

        return response.content


    def close_jsession(self):
        '''
        Destroy the jsessionID (closing the connection to the XNAT instance)
        '''

        URL = self.host + '/data/JSESSION'

        response = requests.delete(URL, cookies=self.jsession_id,
                                   verify=self.verified_SSL_context, timeout=10)

        if response.status_code != requests.codes.ok:
            raise XNATException('HTTP response: #%s' % response.status_code)

        return self.jsession_id


    def resource_exist(self,URL):
        '''
        HTTP query to check if a given URL already exists
        :returns: An HTTP response structure
        '''

        response = requests.head(URL, cookies=self.jsession_id,
                                 verify=self.verified_SSL_context, timeout=10)

        return response


    def get_raw_data(self, URL, options=None):
        '''
        Performs a REST API query
        :return: Raw data structure object (string formatted data chunk)
        '''

        response = requests.get(URL, params=options, cookies=self.jsession_id,
                                verify=self.verified_SSL_context, timeout=100)

        if response.status_code != requests.codes.ok:
            raise XNATException('HTTP response: #%s' %response.status_code)

        return response.content


    def get_json_data(self, URL, options=None):
        '''
        Performs a REST API query
        :return: Manipulable data structure parsed as a JSON object
        '''

        # force output data specification to JSON format
        if not options :
            options = {}
        options['format'] = 'json'

        data = self.get_raw_data(URL, options)

        json_data = json.loads(data)
        result_set = json_data['ResultSet']['Result']

        return result_set


    def put_data(self, URL, data="", options=None):
        '''
        Creates a new XNAT entity with/without data
        '''

        response = requests.put(URL, data=data, params=options, cookies=self.jsession_id,
                                verify=self.verified_SSL_context, timeout=100)

        if response.status_code not in [200, 201]:
            raise XNATException('HTTP response: #%s' % response.status_code)

        return response


    def put_file(self, URL, filename, options=None):
        '''
        Uploads file content included as message body using requests library
        '''

        with open(filename, 'rb') as f:
            response = requests.put(URL, params=options, cookies=self.jsession_id,
                                    verify=self.verified_SSL_context, timeout=100,
                                    files={os.path.basename(filename): f})

        if response.status_code != requests.codes.ok:
            raise XNATException('HTTP response: #%s' %response.status_code)
        #else:
            #log.info(response.request.url)

        return response

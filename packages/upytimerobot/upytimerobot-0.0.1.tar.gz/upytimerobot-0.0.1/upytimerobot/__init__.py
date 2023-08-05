#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Python3 module to interact with UptimeRobot API
"""
import json
import requests
import sys
from urllib.parse import quote
from upytimerobot import colors
from upytimerobot import config

__name__ = "upytimerobot"
__version__ = "0.0.1"
__author__ = "Frederico Freire Boaventura"
__email__ = "frederico@boaventura.net"
__url__ = "https://gitlab.com/fboaventura/upytimerobot"
__all__ = ['get_account_details', 'get_monitors', 'get_monitor_by_name', 'get_monitor_by_id',
           'get_alert_contacts', 'get_mwindows', 'get_psps']


class UptimeRobot():
    def __init__(self, **kwargs):
        try:
            self.api_key = kwargs['api_key']
        except KeyError:
            try:
                config.init(kwargs['config'])
                self.config = config.conf['default']
                self.api_key = self.config['api_key']
            except KeyError:
                config.init()
                self.config = config.conf['default']
                self.api_key = self.config['api_key']

        if not self.api_key:
            config.error_exit('No API Key provided!')

        if self.config['output']:
            self.output = self.config['output']
        elif kwargs['output']:
            self.output = kwargs['output']
        else:
            self.output = 'json'

        if self.config['logs']:
            self.logs = self.config['logs']
        elif kwargs['logs']:
            self.output = kwargs['logs']
        else:
            self.logs = 0

        self.baseUrl = "https://api.uptimerobot.com/v2/"
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
        }

    @staticmethod
    def get_request_status(status_code: int):
        """
        Recover and treat HTTP status code from requests
        :param status_code:
        :return:
        """
        if status_code == 200:
            return True
        elif status_code == 401:
            print(f"[{colors.red('ERR')}] Error {status_code}: Authorization Error! "
                  f"Please check your credentials and try again...")
            sys.exit(status_code)
        elif status_code == 500:
            print(f"[{colors.red('ERR')}] Error {status_code}: Internal Server Error.  "
                  f"Nothing we can do now, but you may try again later.")
            sys.exit(status_code)
        elif status_code == 403:
            print(f"[{colors.red('ERR')}] Error {status_code}: Permission to see this "
                  f"resource is denied on server! Contact the administrator")
            sys.exit(status_code)
        else:
            print(f"[{colors.red('ERR')}] Error {status_code}: There was an unexpected "
                  f"error with the request.")
            sys.exit(status_code)

    @staticmethod
    def error_messages(message: str, code: int = 1):
        print(f"({code}) {message}\n")
        sys.exit(code)

    @staticmethod
    def url_encode(url: str):
        return quote(url, encoding='utf-8')

    def http_request(self, api_call: str, **kwargs):
        """
        Make the HTTP requests to the API
        :param api_call: what will be queried
        :param kwargs: options to be passed to the query
        :return: json or xml result from API
        """
        payload = {'api_key': self.api_key, 'format': self.output, 'logs': self.logs}
        url = self.baseUrl + str(api_call)

        if kwargs:
            for option, value in kwargs.items():
                payload.update({option: value})

        try:
            result_post = requests.post(url, data=payload, headers=self.headers)

            if self.get_request_status(result_post.status_code):
                return result_post.json()
        except requests.exceptions.RequestException as e:
            err_msg = 'Error: {}'.format(e)
            return json.dumps(dict({'stat': 'fail', 'message': err_msg}))

    #######################################################################
    # START ACCOUNT DETAILS DEFINITIONS
    #######################################################################
    def get_account_details(self, **kwargs):
        """
        Returns Alert Contacts defined on the account.
        """
        return self.http_request('getAccountDetails', **kwargs)
    #######################################################################
    # END OF ACCOUNT DETAILS DEFINITIONS
    #######################################################################

    #######################################################################
    # START MONITORS DEFINITIONS
    #######################################################################
    def get_monitors(self, **kwargs):
        """
        Returns status and response payload for all known monitors.
        """
        return self.http_request('getMonitors', **kwargs)

    def get_monitor_by_name(self, friendly_name: str):
        """
        Returns monitor by name
        """
        monitor = self.get_monitors(search=friendly_name)
        if not monitor:
            return {'stat': 'fail', 'message': 'Monitor not found'}
        else:
            return monitor

    def get_monitor_by_id(self, monitor_id: str):
        """
        Returns the monitor by ID
        """
        monitor = self.get_monitors(monitors=monitor_id)
        if not monitor:
            return {'stat': 'fail', 'message': 'Monitor not found'}
        else:
            return monitor
    #######################################################################
    # END OF MONITORS DEFINITIONS
    #######################################################################

    #######################################################################
    # START ALERT CONTACTS DEFINITIONS
    #######################################################################
    def get_alert_contacts(self, **kwargs):
        """
        Returns Alert Contacts defined on the account.
        """
        return self.http_request('getAlertContacts', **kwargs)
    #######################################################################
    # END OF ALERT CONTACTS DEFINITIONS
    #######################################################################

    #######################################################################
    # START MAINTENANCE WINDOWS DEFINITIONS
    #######################################################################
    def get_mwindows(self, **kwargs):
        """
        Returns Alert Contacts defined on the account.
        """
        return self.http_request('getMWindows', **kwargs)
    #######################################################################
    # END OF MAINTENANCE WINDOWS DEFINITIONS
    #######################################################################

    #######################################################################
    # START PUBLIC STATUS PAGES DEFINITIONS
    #######################################################################
    def get_psps(self, **kwargs):
        """
        Returns Alert Contacts defined on the account.
        """
        return self.http_request('getPSPs', **kwargs)
    #######################################################################
    # END OF PUBLIC STATUS PAGES DEFINITIONS
    #######################################################################

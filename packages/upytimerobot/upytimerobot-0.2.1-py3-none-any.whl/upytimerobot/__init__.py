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
from upytimerobot import config
from .colors import reset, red, yellow, blue, green
from .constants import ts_monitor, ts_alert_contacts, ts_log, ts_mwidow, ts_psp

__name__ = "upytimerobot"
__version__ = "0.2.1"
__author__ = "Frederico Freire Boaventura"
__email__ = "frederico@boaventura.net"
__url__ = "https://gitlab.com/fboaventura/upytimerobot"
__all__ = ["get_account_details", "get_monitors", "get_monitor_by_name", "get_monitor_by_id",
           "get_alert_contacts", "get_mwindows", "get_psps"]


class UptimeRobot():
    """
    All the interaction with UptimeRobot is added here.  The queries to the API are made through HTTP requests,
    using the URL defined at `api_url`
    """
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

        if self.config['alert_contacts']:
            self.alert_contacts = self.config['alert_contacts']
        elif kwargs['alert_contacts']:
            self.alert_contacts = kwargs['alert_contacts']
        else:
            pass

        self.api_url = "https://api.uptimerobot.com/v2/"
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
        }

    @staticmethod
    def _get_request_status(status_code: int):
        """
        Recover and treat HTTP status code from requests
        :param status_code:
        :return:
        """
        if status_code == 200:
            return True
        elif status_code == 401:
            print(f"[{red('ERR')}] Error {status_code}: Authorization Error! "
                  f"Please check your credentials and try again...")
            sys.exit(status_code)
        elif status_code == 500:
            print(f"[{red('ERR')}] Error {status_code}: Internal Server Error.  "
                  f"Nothing we can do now, but you may try again later.")
            sys.exit(status_code)
        elif status_code == 403:
            print(f"[{red('ERR')}] Error {status_code}: Permission to see this "
                  f"resource is denied on server! Contact the administrator")
            sys.exit(status_code)
        else:
            print(f"[{red('ERR')}] Error {status_code}: There was an unexpected "
                  f"error with the request.")
            sys.exit(status_code)

    @staticmethod
    def _error_messages(message: str, code: int = 1):
        """
        Print formatted error message and code.
        :param message:
        :param code:
        :return: formatted error code and message
        """
        print(f"({code}) {message}\n")
        sys.exit(code)

    @staticmethod
    def _url_encode(url: str):
        """
        Properly encode URL to be used on API requests
        :param url:
        :return:
        """
        return quote(url, encoding='utf-8')

    def _http_request(self, api_call: str, **kwargs):
        """
        Make the HTTP requests to the UptimeRobot API
        :param api_call: what will be queried
        :param kwargs: options to be passed to the query
        :return: json or xml result from API
        """
        payload = {'api_key': self.api_key, 'format': self.output, 'logs': self.logs}
        url = self.api_url + str(api_call)

        if kwargs:
            for option, value in kwargs.items():
                payload.update({option: value})

        try:
            result_post = requests.post(url, data=payload, headers=self.headers)

            if self._get_request_status(result_post.status_code):
                return result_post.json()
        except requests.exceptions.RequestException as e:
            return json.dumps(dict({'stat': 'fail', 'message': f'Error: {e}'}))

    #######################################################################
    # START ACCOUNT DETAILS DEFINITIONS
    #######################################################################
    def get_account_details(self):
        """
        Fetch and returns Account details.
             `email` -> email under witch the account was registered
             `monitor_limit` -> maximum number of monitors (always 50 for free plan)
             `monitor_interval` -> interval between monitor queries (always 5 for free plan)
             `down_monitors` -> how many monitors are down
             `paused_monitors` -> how many monitors are paused
             `up_monitors` -> how many monitors are up
        """
        return self._http_request('getAccountDetails')
    #######################################################################
    # END OF ACCOUNT DETAILS DEFINITIONS
    #######################################################################

    #######################################################################
    # START MONITORS DEFINITIONS
    #######################################################################
    def get_monitors(self, **kwargs):
        """
        Fetch and returns status and response payload for all known monitors.
        Parameters:
        :parameter: monitor - optional (if not used, will return all monitors in an account. Else, it is possible to
            define any number of monitors with their IDs like: monitors=15830-32696-83920)
        :parameter: type - optional (if not used, will return all monitors types (HTTP, keyword, ping..) in an account.
            Else, it is possible to define any number of monitor types like: types=1-3-4)
        :parameter: status - optional (if not used, will return all monitors statuses (up, down, paused) in an
            account. Else, it is possible to define any number of monitor statuses like: statuses=2-9)
        :parameter: custom_uptime_ratios - optional (defines the number of days to calculate the uptime ratio(s) for.
            Ex: custom_uptime_ratios=7-30-45 to get the uptime ratios for those periods)
        :parameter: custom_uptime_ranges - optional (defines the ranges to calculate the uptime ratio(s) for.
            Ex: custom_uptime_ranges=1465440758_1466304758 to get the uptime ratios for those periods. It is possible
            to send multiple ranges like 1465440758_1466304758-1434682358_1434855158)
        :parameter: all_time_uptime_ratio - optional (returns the "all time uptime ratio". It will slow down the
            response a bit and, if not really necessary, suggest not using it. Default is 0)
        :parameter: all_time_uptime_durations - optional (returns the "all time durations of up-down-paused events".
            It will slow down the response a bit and, if not really necessary, suggest not using it. Default is 0)
        :parameter: logs - optional (defines if the logs of each monitor will be returned. Should be set to 1 for
            getting the logs. Default is 0)
        :parameter: logs_start_date - optional (works only for the Pro Plan as 24 hour+ logs are kept only in the
            Pro Plan, formatted as Unix time and must be used with logs_end_date)
        :parameter: logs_end_date - optional (works only for the Pro Plan as 24 hour+ logs are kept only in the
            Pro Plan, formatted as Unix time and must be used with logs_start_date)
        :parameter: logs_limit - optional (the number of logs to be returned (descending order). If empty, all
            logs are returned.
        :parameter: response_times - optional (defines if the response time data of each monitor will be returned.
            Should be set to 1 for getting them. Default is 0)
        :parameter: response_times_limit - optional (the number of response time logs to be returned
            (descending order). If empty, last 24 hours of logs are returned (if response_times_start_date
            and response_times_end_date are not used).
        :parameter: response_times_average - optional (by default, response time value of each check is returned.
            The API can return average values in given minutes. Default is 0. For ex: the Uptime Robot dashboard
            displays the data averaged/grouped in 30 minutes)
        :parameter: response_times_start_date - optional (formatted as Unix time and must be used with
            response_times_end_date) (response_times_end_date - response_times_start_date can't be more than 7 days)
        :parameter: response_times_end_date - optional (formatted as Unix time and must be used with
            response_times_start_date) (response_times_end_date - response_times_start_date can't be more than 7 days)
        :parameter: alert_contacts - optional (defines if the alert contacts set for the monitor to be
            returned. Default is 0)
        :parameter: mwindows - optional (the maintenance windows for the monitor which can be mentioned with
            their IDs like 345-2986-71)
        :parameter: ssl - optional (defines if SSL certificate info for each monitor will be returned)
        :parameter: custom_http_headers - optional (defines if the custom HTTP headers of each monitor will be
            returned. Should be set to 1 for getting them. Default is 0)
        :parameter: timezone - optional (defines if the user's timezone should be returned. Should be set to 1
            for getting it. Default is 0)
        :parameter: offset - optional (used for pagination. Defines the record to start paginating. Default is 0)
        :parameter: limit - optional (used for pagination. Defines the max number of records to return for
            the response. Default and max. is 50)
        :parameter: search - optional (a keyword of your choice to search within url and friendly_name and
            get filtered results)

        """
        parameters = ['api_key', 'monitors', 'types', 'statuses', 'custom_uptime_ratios', 'custom_uptime_ranges',
                      'all_time_uptime_ratio', 'all_time_uptime_durations', 'logs', 'logs_start_date',
                      'logs_end_date', 'logs_limit', 'response_times', 'response_times_limit',
                      'response_times_average', 'response_times_start_date', 'response_times_end_date',
                      'alert_contacts', 'mwindows', 'ssl', 'custom_http_headers', 'timezone', 'offset',
                      'limit', 'search']

        return self._http_request('getMonitors', **kwargs)

    def get_monitor_by_name(self, friendly_name: str):
        """
        Fetch and return monitor(s) by name.
        :parameter: friendly_name: it can be the exact or part of the monitor's name
        :return: list of the monitors that have the friendly_name match with the string used as parameter
        """
        monitor = self.get_monitors(search=friendly_name)
        if not monitor or monitor['stat'] == 'fail':
            return {'stat': 'fail', 'message': 'Monitor not found'}
        else:
            return monitor

    def get_monitor_by_id(self, monitor_id: str):
        """
        Fetch and returns the monitor by ID
        """
        monitor = self.get_monitors(monitors=monitor_id)
        if not monitor['monitors'] or monitor['stat'] == 'fail':
            return {'stat': 'fail', 'message': 'Monitor not found'}
        else:
            return monitor

    def get_monitor_by_type(self, types: str):
        """
        Fetch and returns the monitor by type. The possible types are:
            1: HTTP(S)
            2: Keyword
            3: Ping
            4: Port
        One can concatenate the types IDs to make a query for multiple monitors, using `X-X-X` as string format.
        """
        monitor = self.get_monitors(types=types)
        if not monitor['monitors'] or monitor['stat'] == 'fail':
            return {'stat': 'fail', 'message': 'Monitor not found'}
        else:
            return monitor

    def get_monitor_by_status(self, statuses: int = 2):
        """
        Fetch and returns the monitor by status. The possible statuses are:
            0: paused
            1: not checked yet
            2: up
            8: seems down
            9: down
        :parameter: statuses: one of the above IDs or a combination of them in the format `X-X-X`
        """
        monitor = self.get_monitors(statuses=statuses)
        if not monitor['monitors'] or monitor['stat'] == 'fail':
            return {'stat': 'fail', 'message': 'Monitor not found'}
        else:
            return monitor['monitors']

    def add_monitor(self, friendly_name: str, url: str, types: int, **kwargs):
        """
        Add a new monitor.
        :param friendly_name: How the monitor will be known as
        :param url: IP address or FQDN
        :param types: 1 - HTTP(s), 2 - Keyword, 3 - Ping, 4 - Port
        :param sub_type: It's mandatory and only used if type = 4.  Options are
            1 - HTTP (80), 2 - HTTPS (443), 3 - FTP (21), 4 - SMTP (25),
            5 - POP3 (110), 6 - IMAP (143), 99 - Custom Port
        :param port: It's mandatory and only used if sub_type = 99
        :param kwargs:
        :return:
        """
        if types == 4:
            if not int(kwargs['sub_type']):
                raise ValueError('Missing parameter sub_type or wrong type passed')

        if 'alert_contacts' in kwargs:
            pass
        elif self.alert_contacts:
            kwargs.update({'alert_contacts': self.alert_contacts})
        else:
            pass

        return self._http_request('newMonitor', friendly_name=friendly_name, url=url,
                                  type=types, **kwargs)

    def add_http_monitor(self, friendly_name: str, url: str, **kwargs):
        """
        Add new HTTP(s) monitor
        :param friendly_name: How the monitor will be known as
        :param url: http:// or https:// and domain name
        :param kwargs: Among the options available for a new monitor, HTTP(s) have
            http_username and http_password, to allow for HTTP Authentication
        :return:
        """
        if 'alert_contacts' in kwargs:
            pass
        elif self.alert_contacts:
            kwargs.update({'alert_contacts': self.alert_contacts})
        else:
            pass

        return self._http_request('newMonitor', friendly_name=friendly_name,
                                  url=url, type=1, **kwargs)

    def add_ping_monitor(self, friendly_name: str, url: str, **kwargs):
        """
        Add new ping monitor
        :param friendly_name: How the monitor will be known as
        :param url: IP address or FQDN to be monitored
        :param kwargs:
        :return:
        """
        if 'alert_contacts' in kwargs:
            pass
        elif self.alert_contacts:
            kwargs.update({'alert_contacts': self.alert_contacts})
        else:
            pass

        return self._http_request('newMonitor', friendly_name=friendly_name,
                                  url=url, type=3, **kwargs)

    def add_port_monitor(self, friendly_name: str, url: str, port: int, **kwargs):
        """
        Add new port monitor
        :param friendly_name: How the monitor will be known as
        :param url: IP address or FQDN to be monitored
        :param port: Port to be monitored
        :param kwargs:
        :return:
        """
        if 'alert_contacts' in kwargs:
            pass
        elif self.alert_contacts:
            kwargs.update({'alert_contacts': self.alert_contacts})
        else:
            pass

        return self._http_request('newMonitor', friendly_name=friendly_name,
                                  url=url, type=3, sub_type=99, port=port, **kwargs)
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
        return self._http_request('getAlertContacts', **kwargs)
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
        return self._http_request('getMWindows', **kwargs)
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
        return self._http_request('getPSPs', **kwargs)
    #######################################################################
    # END OF PUBLIC STATUS PAGES DEFINITIONS
    #######################################################################

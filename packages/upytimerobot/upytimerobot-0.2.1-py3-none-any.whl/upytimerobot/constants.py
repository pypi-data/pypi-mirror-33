#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Constants used in other parts of the program.
"""
from __future__ import absolute_import, division, unicode_literals

ts_monitor = {
    'type': {'1': 'HTTP(S)', '2': 'Keyword', '3': 'Ping', '4': 'Port'},
    'sub_type': {'1': 'HTTP (80)', '2': 'HTTPS (443)', '4': 'SMTP (25)',
                 '5': 'POP3 (110)', '6': 'IMAP (143)', '99': 'Custom Port'},
    'keyword_type': {'1': 'exists', '2': 'not exists'},
    'status': {'0': 'paused', '1': 'not checked yet', '2': 'up', '8': 'seems down', '9': 'down'}
}

ts_log = {'types': {'1': 'down', '2': 'up', '99': 'paused', '98': 'started'}}

ts_alert_contacts = {
    'type': {'1': 'SMS', '2': 'E-mail', '3': 'Twitter DM', '4': 'Boxcar', '5': 'Web-Hook', '6': 'Pushbullet',
             '7': 'Zapier', '9': 'Pushover', '10': 'HipChat', '11': 'Slack'},
    'status': {'0': 'not activated', '1': 'paused', '2': 'active'},
    'threshold': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30,
                  35, 40, 45, 50, 55, 60, 70, 80, 90, 100, 110, 120, 150, 180,
                  210, 240, 270, 300, 360, 420, 480, 540, 600, 660, 720),
    'recurrence': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                   20, 30, 35, 40, 45, 50, 55, 60),
}

ts_mwidow = {
    'type': {'1': 'Once', '2': 'Daily', '3': 'Weekly', '4': 'Monthly'},
    'status': {'0': 'paused', '1': 'active'}
}

ts_psp = {
    'sort': {'1': 'friendly name (a-z)', '2': 'friendly name (z-a)',
             '3': 'status (up-down-paused)', '4': 'status (down-up-paused)'},
    'status': {'0': 'paused', '1': 'active'},
}

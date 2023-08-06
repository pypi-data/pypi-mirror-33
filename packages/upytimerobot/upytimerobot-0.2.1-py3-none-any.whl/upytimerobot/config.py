#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Helper library for configuration handling
"""

# Imports
import configparser
import os
import sys

conf = configparser.ConfigParser()


def init(config_file='config.ini', config_section='default'):
    """
    Initialize the configuration file handling
    :param config_file: File that will be used to consult the configurations
    :param config_section: Profile to be used
    """
    config_file = config_file
    config_section = config_section
    config_open(config_file)


def config_write(config_file):
    """
    Write configuration into file
    :param config_file:
    """
    conf.write(open(config_file, 'w'))


def error_exit(error_message: str = "Oops! There was an error...", error_code: int = 1):
    print(f'{error_message}\n')
    sys.exit(error_code)


def new_config(config_file, config_section='default'):
    """
    Get data for new configuration file
    :param config_file:
    :param config_section:
    """
    conf[config_section] = {}
    conf[config_section]['api_key'] = str(input("Enter your UptimeRobot API Key: ") or
                                         error_exit('Missing API Key!'))
    conf[config_section]['output'] = str(input("Which is your favourite output format (json, xml or pretty)? [json]")
                                         or 'json')
    conf[config_section]['logs'] = str(input("Want to see logs by default (1: Yes or 0: No)? [0] "))
    config_write(config_file)


def config_open(config_file, config_section='default'):
    """
    Read configuration file
    :param config_file:
    :param config_section:
    :return:
    """
    if not os.path.exists(config_file):
        new_config(config_file, config_section)

    cfg = conf.read(config_file)
    return cfg

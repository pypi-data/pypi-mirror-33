#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
Colorizing output
"""

# Imports
from colorama import init, Fore, Style

# Initializing colorama
init()


def reset():
    """
    Apply the reset style
    :return:
    """
    return Style.RESET_ALL


def red(text: str):
    """
    Foreground color red
    :param text:
    :return:
    """
    return Fore.RED + str(text) + Style.RESET_ALL


def green(text: str):
    """
    Foreground color green
    :param text:
    :return:
    """
    return Fore.GREEN + str(text) + Style.RESET_ALL


def blue(text: str):
    """
    Foreground color blue
    :param text:
    :return:
    """
    return Fore.BLUE + str(text) + Style.RESET_ALL


def yellow(text: str):
    """
    Foreground color yellow
    :param text:
    :return:
    """
    return Fore.YELLOW + str(text) + Style.RESET_ALL

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: winrmmanager.py
#
# Copyright 2018 Gareth Hawker
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for winrmmanager

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

import requests
import winrm

from winrm.exceptions import InvalidCredentialsError

__author__ = '''Gareth Hawker <ghawker@schubergphilis.com>'''
__docformat__ = '''google'''
__date__ = '''2018-07-06'''
__copyright__ = '''Copyright 2018, Gareth Hawker'''
__credits__ = ["Gareth Hawker", "Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Gareth Hawker'''
__email__ = '''<ghawker@schubergphilis.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''winrmmanager'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class WinRMManager(object):  # pylint: disable=too-few-public-methods
    """class containing all methods required to setup secure and insecure WinRM sessions"""

    def __init__(self,  # pylint: disable=too-many-arguments
                 host,
                 username,
                 password,
                 read_timeout=3,
                 operation_timeout=2,
                 unencrypted_port=5985,
                 encrypted_port=5986):
        logger_name = u'{base}.{suffix}'.format(base=LOGGER_BASENAME,
                                                suffix=self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)
        self.host = host
        self.unencrypted_session, self.encrypted_session = self._get_sessions(host,
                                                                              username,
                                                                              password,
                                                                              read_timeout,
                                                                              operation_timeout,
                                                                              unencrypted_port,
                                                                              encrypted_port)

    def _get_sessions(self,  # pylint: disable=too-many-arguments
                      host,
                      username,
                      password,
                      read_timeout,
                      operation_timeout,
                      unencrypted_port,
                      encrypted_port):
        arguments_ = {'read_timeout_sec': read_timeout,
                      'operation_timeout_sec': operation_timeout}
        unencrypted_target = '{host}:{port}'.format(host=host, port=unencrypted_port)
        self._logger.info('Trying unencrypted connection to port {}'.format(unencrypted_port))
        unencrypted_session = self._check_protocol(unencrypted_target,
                                                   username,
                                                   password,
                                                   **arguments_)
        arguments_.update({'transport': 'ssl',
                           'server_cert_validation': 'ignore'})
        encrypted_target = '{host}:{port}'.format(host=host, port=encrypted_port)
        self._logger.info('Trying encrypted connection to port {}'.format(encrypted_port))
        encrypted_session = self._check_protocol(encrypted_target,
                                                 username,
                                                 password,
                                                 **arguments_)
        return unencrypted_session, encrypted_session

    def _check_protocol(self, target, username, password, **kwargs):
        protocol = 'https' if kwargs.get('transport') == 'ssl' else 'http'
        try:
            session = winrm.Session(target,
                                    auth=(username, password),
                                    **kwargs)
            self._logger.info('Trying to execute powershell command over WinRM')
            session.run_ps('write-host "winrm enabled"')
            return session
        except InvalidCredentialsError:
            message = ("Credentials Error while connecting to host "
                       "{} over {}").format(target, protocol)
        except requests.exceptions.ConnectTimeout:
            message = ("Connection timed out while connecting to host "
                       "{} over {}").format(target, protocol)
        except requests.exceptions.ConnectionError:
            message = "WinRM not accessible for host {} over {}".format(target, protocol)
        except Exception as e:  # pylint: disable=broad-except, invalid-name
            message = "Unexpected exception happened :{}".format(e)
        self._logger.warning(message)
        return None

    def get_session(self):
        """Return a WinRM session to the user with preference for encrypted"""
        return self.encrypted_session or self.unencrypted_session

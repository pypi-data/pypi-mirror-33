# -*- coding: utf-8 -*-
"""tigereye main module."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)


class Error(Exception):

    def __init__(self, msg):
        self.msg = msg

class InternalError(Error):

    def error_message(self):
        return self.msg

class UsageError(Error):

    def error_message(self):
        return self.msg


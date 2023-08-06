#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    exc.py
    ~~~~~~

    Exceptions for TAP file handling.

    (c) BSD 3-clause.
"""


import os
import sys

__all__ = ["TapParseError", "TapMissingPlan", "TapInvalidNumbering", "TapBailout"]


class TapParseError(Exception):
    """Parsing of TAP file failed"""
    pass


class TapMissingPlan(TapParseError):
    """TAP file is missing a plan"""
    pass


class TapInvalidNumbering(TapParseError):
    """Invalid enumeration of testcase results"""
    pass


class TapBailout(Exception):
    """TAP file triggered a bailout"""
    is_testcase = False
    is_bailout = True
    encoding = sys.stdout.encoding

    def __init__(self, *args, **kwargs):
        super(TapBailout, self).__init__(*args, **kwargs)
        self.data = []

    @property
    def msg(self):
        """Error message"""
        return getattr(self, 'message', self.args[0])

    def __str__(self):
        return "Bail out! {}{}{}".format(
            self.msg, os.linesep, os.linesep.join(self.data)
        )

    def copy(self, memo=None):
        inst = TapBailout(memo or self.msg)
        inst.data = self.data
        return inst

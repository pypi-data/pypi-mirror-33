# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from CodeConvert import CodeConvert as cc

from .compat import basestring


class StrSnippets(object):
    def strip_ascii_control_characters(self, s):
        # ASCII Control Characters
        return re.sub(r'[\x01-\x1F\x7F]', '', s)

    def strip(self, s, cc=False):
        if not isinstance(s, basestring):
            return s
        return self.strip_ascii_control_characters(s) if cc else s.strip()

    def trim(self, s, length=None, joint=''):
        if not isinstance(s, basestring):
            return s
        if length is None:
            return s
        return '{0}{1}'.format(s[:length], joint) if len(s) > length else s[:length]

    # https://github.com/fredshare/blog/issues/21
    # https://my.oschina.net/konglo/blog/738678
    def removeU2006(self, s):
        return cc.Convert2Unicode(s).replace(u'\u2006', '').replace('\u2006', '')


_global_instance = StrSnippets()
strip = _global_instance.strip
trim = _global_instance.trim
removeU2006 = _global_instance.removeU2006

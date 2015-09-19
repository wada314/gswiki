# -*- coding: utf-8 -*-
"""
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.parser import text_moin_wiki

class Parser(text_moin_wiki.Parser):
    def __init__(self, raw, request, filename=None, format_args='', **kw):
        # fake request... > /dev/null
        pass


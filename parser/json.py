# -*- coding: utf-8 -*-
"""
    @copyright: 2008 Radomir Dopieralski <moindev@sheep.art.pl>
    @license: GNU GPL, see COPYING for details.
"""

import json
from MoinMoin.formatter.text_html import Formatter as HTMLFormatter

Dependencies = [] # No dependencies

class Parser:
    Dependencies = Dependencies

    def __init__(self, raw, request, filename=None, format_args='', **kw):
        self.request = request
        self.entry_name = format_args
        if not self.entry_name:
            self.json_obj = '#!json requires the entry name.'
            return
        try:
            self.json_obj = json.loads(raw)
        except Exception as e:
            self.json_obj = 'Something wrong in JSON data: %s' % e
    
    def format(self, formatter, **kw):
        if isinstance(formatter, HTMLFormatter):
            self.request.write(formatter.rawHTML('<u>html output of json! %s</u>' % self.entry_name))
        else:
            self.request.write(formatter.text('[placeholder of json]'))

# -*- coding: utf-8 -*-
"""
    @license: GNU GPL, see COPYING for details.
"""

import json
from MoinMoin.formatter.text_html import Formatter as HTMLFormatter

Dependencies = [] # No dependencies

class Parser:
    Dependencies = Dependencies

    def __init__(self, raw, request, filename=None, format_args='', **kw):
        self.request = request
        try:
            self.json_obj = json.loads(raw)
        except Exception as e:
            self.json_obj = 'Something wrong in JSON data: %s' % e

    def format(self, formatter, **kw):
        if isinstance(formatter, HTMLFormatter):
            self.request.write(formatter.rawHTML(u'<u>html output of json!</u><br>%s' 
                                                 % json.dumps(self.json_obj, ensure_ascii=False)))
        else:
            self.request.write(formatter.text('[placeholder of json]'))

# -*- coding: utf-8 -*-
"""
    @license: GNU GPL, see COPYING for details.
"""

import json

from MoinMoin.formatter.text_html import Formatter as HTMLFormatter
from MoinMoin.Page import Page
from MoinMoin import wikiutil

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

    def load_json_from_page(self, page_name, parser_name):
        formatterClass = wikiutil.searchAndImportPlugin(
            self.request.cfg, 'formatter', 'extracting_formatter')
        extracting_formatter = formatterClass(parser_name, self.request)
        page = Page(self.request, page_name, formatter=extracting_formatter)
        extracting_formatter.setPage(page)

        # Discarding the return value
        self.request.redirectedOutput(
            Page.send_page_content, page, self.request, page.data, 'wiki')

        return extracting_formatter.get_extracted()

# -*- coding: utf-8 -*-
"""
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.formatter import text_html

class Formatter(text_html.Formatter):
    def __init__(self, extracting_parser_name, request):
        text_html.Formatter.__init__(self, request)
        self.extracting_parser_name = extracting_parser_name
        self.extracted = None

    def parser(self, parser_name, lines):
        """ Extract a specified parser name item.
        """
        if parser_name != self.extracting_parser_name:
            return u''
        if lines:
            args = self._get_bang_args(lines[0])
            if args is not None:
                lines = lines[1:]
            # save the {{{}}} content
            self.extracted = u'\n'.join(lines)
        return u''

    def get_extracted(self):
        return self.extracted

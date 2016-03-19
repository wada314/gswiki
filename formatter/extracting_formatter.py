# -*- coding: utf-8 -*-
"""
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.formatter import text_html

class Formatter(text_html.Formatter):
    """A formatter to extract json data part from the given page.
    """

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

    def macro(self, macro_obj, name, args, markup=None):
        """We need to ignore macro to avoid recursive call when this formatter
        is triggered from a macro.
        """
        return u''

# -*- coding: utf-8 -*-

from MoinMoin.parser.text_moin_wiki import Parser as ParserBase

class Parser(ParserBase):
    quickhelp = u'<<Include(編集のヘルプ)>>'

    def __init__(self, raw, request, **kw):
        ParserBase.__init__(self, raw, request, **kw)

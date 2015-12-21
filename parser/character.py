# -*- coding: utf-8 -*-

import math

import _json
from _table import _Table, _Row, _Cell

class Parser(_json.Parser):
    def format(self, formatter, **kw):
        j = self.json_obj

        title = (formatter.heading(True, 2)
                 + formatter.text(u'キャラクター性能')
                 + formatter.heading(False, 2))
        fight = (formatter.table(True)
                 + formatter.table_row(True, {u'rowclass':u'header'})
                 + formatter.table_cell(True) + formatter.text(u'種類') + formatter.table_cell(False)
                 + formatter.table_cell(True) + formatter.text(u'威力') + formatter.table_cell(False)
                 + formatter.table_cell(True) + formatter.text(u'解説') + formatter.table_cell(False)
                 + formatter.table_row(False))
        fight += formatter.table(False)
        self.request.write(title + fight)
        

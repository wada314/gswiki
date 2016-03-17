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
        self.request.write(title)

        self.create_desc(formatter)

    def create_desc(self, formatter, **kw):
        grapple_title = (formatter.heading(True, 2)
                 + formatter.text(u'格闘性能')
                 + formatter.heading(False, 2))
        self.request.write(grapple_title)

        grapple_table = self.create_grapple_table(formatter).toHtmlTable()
        self.request.write(grapple_table.format(formatter))

    def create_grapple_table(self, formatter, **kw):
        table = _Table()
        j = self.json_obj.get(u'格闘', {})
        grapple_types = [u'N格', u'上格', u'左格', u'右格', u'下格']

        for grapple_type in grapple_types:
            grapple = j.get(grapple_type, {})
            row = _Row()
            row.cells.append(_Cell(u'種類', grapple_type))
            row.cells.append(_Cell(u'威力', unicode(grapple.get(u'威力', u'???'))))
            row.cells.append(_Cell(u'威力', unicode(grapple.get(u'解説', u''))))
            table.rows.append(row)
        
        return table

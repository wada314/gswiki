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
        

# -*- encoding: utf-8 -*-

import itertools
import math
import json

import _json, weapon
from _table import _Table, _Row, _Cell
from MoinMoin.Page import Page

class Parser(_json.Parser):
    def format(self, formatter, **kw):
        """Do nothing for data itself. Use <<WPData>> macro to display the data.
        """
        pass

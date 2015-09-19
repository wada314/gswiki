# -*- encoding: utf-8 -*-

import math

import _json
from _table import _Table, _Row, _Cell
from MoinMoin.Page import Page

class Parser(_json.Parser):
    def format(self, formatter, **kw):
        j = self.json_obj
        table = _Table()
        
        text = u"""
        コスト: %(cost)s　耐久力: %(life)s　格闘補正: x%(melee)s倍　入手条件: %(howtoget)s\n
        """ % { u'cost': j[u'コスト'] or u'???',
                u'life': j[u'耐久力'] or u'???',
                u'melee': j[u'格闘補正'] or u'???',
                u'howtoget': j.get(u'入手条件', u'') or u'???'}

        weapon_names = (j[u'右手武器'], j[u'左手武器'],
                        j[u'サイド武器'], j[u'タンデム武器'])
        place_names = (u'右手', u'左手', u'サイド', u'タンデム')
        rows = []
        for place_name, weapon_name in zip(place_names, weapon_names):
            name = weapon_name.get(u'名称', u'unknown')
            level = weapon_name.get(u'レベル', 0)
            row, subrow = self._get_leveled_weapon_and_subweapon_rows(
                formatter, name, level)

    def _get_leveled_weapon_and_subweapon_rows(self, formatter, name, level):
        

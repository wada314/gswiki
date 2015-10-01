# -*- encoding: utf-8 -*-

import math
import json

import _json, weapon
from _table import _Table, _Row, _Cell
from MoinMoin.Page import Page

class Parser(_json.Parser):
    def format(self, formatter, **kw):
        j = self.json_obj
        table = _Table()

        text = formatter.linebreak(preformatted=False)
        text += u"""
        コスト: %(cost)s　耐久力: %(life)s　格闘補正: x%(melee)s倍　入手条件: %(howtoget)s\n
        """ % { u'cost': j[u'コスト'] or u'???',
                u'life': j[u'耐久力'] or u'???',
                u'melee': j[u'格闘補正'] or u'???',
                u'howtoget': j.get(u'入手条件', u'') or u'???'}

        weapon_names = (j[u'右手武器'], j[u'左手武器'],
                        j[u'サイド武器'], j[u'タンデム武器'])
        place_names = (u'右手', u'左手', u'サイド', u'タンデム')
        for place_name, weapon_name in zip(place_names, weapon_names):
            name = weapon_name.get(u'名称', u'unknown')
            level = weapon_name.get(u'レベル', 0)
            row, subrow = self._get_leveled_weapon_and_subweapon_rows(
                formatter, name, level, place_name)
            table.rows.append(row)
            if subrow:
                table.rows.append(subrow)
        text += table.format(formatter)
        self.request.write(text)

    def _get_leveled_weapon_and_subweapon_rows(self, formatter, name, level, place_name):
        json_text = self.load_json_text_from_page(name, u'weapon')
        weapon_parser = weapon.Parser(json_text, self.request)
        row = _Row()
        row.cells.append(_Cell(u'装備箇所', place_name, {u'class':u'center,hc'}))
        weapon_parser.create_row(row, level, formatter,
                                 subweapon_in_row=False, subtrigger_in_row=False,
                                 show_name=True)
        subrow = _Row()
        subrow.cells.append(_Cell(u'装備箇所', u'サブ', {u'class':u'center,hc'}))

        leveled_weapon = weapon_parser.json_obj.get(u'レベル', {}).get(u'%d' % level, {})
        print(json.dumps(leveled_weapon, ensure_ascii=False))
        if u'_サブウェポン' in leveled_weapon:
            subweapon = leveled_weapon[u'_サブウェポン']
            subname = subweapon[u'名称']
            sublevel = subweapon[u'レベル']
            subweapon_parser = weapon.Parser(self.load_json_text_from_page(subname, u'weapon'), self.request)
            subweapon_parser.create_row(subrow, sublevel, formatter,
                                        subweapon_in_row=False, subtrigger_in_row=False,
                                        show_name=True)
            return row, subrow
        elif u'_サブトリガー' in leveled_weapon:
            subrow.cells.append(_Cell(u'武装名', u'(サブ)', {u'class':u'center'}))
            # fill empty columns so that this row does not be shorter than the other rows
            subrow.cells.extend([_Cell()] * 20)
            return row, subrow
        else:
            return row, None

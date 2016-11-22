# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell, TitleRow, TitleCell
from utils.json_loader import load_all_jsons

import WeaponData

Dependencies = ['pages']

def life_per_1000cost(j):
    return j.get(u'耐久力', 0) * 1000.0 / j.get(u'コスト', 1)

def macro_LifeCostRatioList(macro, _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    all_jsons = load_all_jsons(request)
    wp_json_list = all_jsons.get(u'wps', [])
    wp_json_list.sort(key=life_per_1000cost)

    table = Table()

    header_row = TitleRow()
    for header in [u'WP名', u'耐久力', u'コスト', u'1000コストあたりの耐久']:
        header_row.cells.append(TitleCell(header, formatted=False, cls=['center']))
    table.rows.append(header_row)
        
    for wp in wp_json_list:
        row = Row()
        life = wp.get(u'耐久力', 0)
        cost = wp.get(u'コスト', 0)
        wp_name = wp.get(u'名称', u'BadWPName')
        wp_name_with_link = (formatter.pagelink(True, wp_name)
                             + formatter.text(wp_name)
                             + formatter.pagelink(False))
        row.cells.append(Cell(None, wp_name_with_link, formatted=True, cls=['center']))
        row.cells.append(Cell(None, u'%d' % life, cls=['right']))
        row.cells.append(Cell(None, u'%d' % cost, cls=['right']))
        row.cells.append(Cell(None, u'%3.1f' % life_per_1000cost(wp), cls=['right']))
        table.rows.append(row)

    html_table = table.toHtmlTable(generate_header=False)
    return html_table.format(formatter)

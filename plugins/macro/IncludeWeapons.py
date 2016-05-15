# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell, HtmlRow, HtmlTable, HtmlCell
from utils.json_loader import load_json_from_page

import WeaponData

Dependencies = ['pages']

# Very very hacky...
def macro_IncludeWeapons(macro, _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    requested_weapons = _trailing_args
    if not requested_weapons:
        # assume the caller requested to show a weapon data of the current page.
        requested_weapons = [macro.formatter.page.page_name]
    else:
        parser = None
    requested_weapons.reverse()
    
    tables = []
    all_rows = []
    existing_weapons = []
    for weapon_name in requested_weapons:
        w = load_json_from_page(request, parser, weapon_name, u'weapon') or {}
        table = Table()
        if w:
            WeaponData.create_table(request, w, table, formatter, show_wp_owners=True)
            existing_weapons.append(weapon_name)
            all_rows.extend(table.rows)
            tables.append(table)

    table.remove_empty_columns(all_rows)

    html_tables = []
    for table in tables:
        html_tables.append(table.toHtmlTable(remove_empty_columns=False))

    html_rows = []
    for (weapon_name, html_table) in zip(existing_weapons, html_tables):
        row_cells = []
        row_cells.append(HtmlCell(
            formatter.pagelink(True, weapon_name) + formatter.text(weapon_name) + formatter.pagelink(False),
            attrs={u'colspan': (u'%d' % len(all_rows[0].cells))},
            formatted=True
        ))
        # row_cells has only 1 column because the all cells are colspan-ed.
        html_rows.append(HtmlRow(row_cells, cls=[u'wheader left']))
        html_rows.extend(html_table.rows)

    final_table = HtmlTable(html_rows)
    return final_table.format(formatter)

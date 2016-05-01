# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell
from utils.json_loader import load_json_from_page

Dependencies = ['pages']

def macro_CharacterData(macro, character_name=None):
    request = macro.request
    formatter = macro.formatter

    if not character_name:
        character_name = macro.formatter.page.page_name

    return create_character_data(request, formatter, character_name)

def create_character_data(request, formatter, character_name):
    j = load_json_from_page(request, character_name, u'character')

    title = (formatter.heading(True, 2)
             + formatter.text(u'キャラクター性能')
             + formatter.heading(False, 2))
    return title + create_desc(j, formatter)

def create_desc(j, formatter):
    grapple_title = (formatter.heading(True, 3)
             + formatter.text(u'格闘性能')
             + formatter.heading(False, 3))
    grapple_title

    grapple_table = create_grapple_table(j).toHtmlTable()
    return grapple_title + grapple_table.format(formatter)

def create_grapple_table(j):
    table = Table()
    j = j.get(u'格闘', {})
    grapple_types = [u'N格', u'上格', u'左格', u'右格', u'下格']

    for grapple_type in grapple_types:
        grapple = j.get(grapple_type, {})
        row = Row()
        row.cells.append(Cell(u'種類', grapple_type))
        row.cells.append(Cell(u'威力', unicode(grapple.get(u'威力', u'???'))))
        row.cells.append(Cell(u'解説', unicode(grapple.get(u'解説', u''))))
        table.rows.append(row)

    return table

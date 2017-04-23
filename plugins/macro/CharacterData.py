# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell
from utils.json_loader import load_json_from_page

Dependencies = ['pages']

generates_headings = True

def macro_CharacterData(macro, prefix=u'', character_name=None):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    if not character_name:
        character_name = macro.formatter.page.page_name
    else:
        parser = None

    return create_character_data(request, parser, formatter, prefix, character_name)

def create_character_data(request, parser, formatter, prefix, character_name):
    j = load_json_from_page(request, parser, prefix + character_name, u'character')

    return create_desc(j, formatter)

def create_desc(j, formatter):
    grapple_title = (formatter.heading(True, 3)
             + formatter.text(u'格闘性能')
             + formatter.heading(False, 3))

    grapple_table = create_grapple_table(j).toHtmlTable()

    status_title = (formatter.heading(True, 3)
             + formatter.text(u'基本ステータス')
             + formatter.heading(False, 3))

    status_table = create_status_table(j).toHtmlTable(generate_header=False)

    return (status_title + status_table.format(formatter)
            + grapple_title + grapple_table.format(formatter))

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

def create_status_table(j):
    table = Table()
    j = j.get(u'キャラクターデータ', {})
    row1 = Row()
    row1.cells.append(Cell(text=u'ダッシュ初速度', cls=[u'header']))
    row1.cells.append(Cell(text=unicode(j.get(u'空中ダッシュ初速度', u'?')), cls=[u'center']))
    row1.cells.append(Cell(text=u'ダッシュ最終速度', cls=[u'header']))
    row1.cells.append(Cell(text=unicode(j.get(u'空中ダッシュ最終速度', u'?')), cls=[u'center']))
    table.rows.append(row1)
    
    row2 = Row()
    row2.cells.append(Cell(text=u'ジャンプ上昇力', cls=[u'header']))
    row2.cells.append(Cell(text=unicode(j.get(u'ジャンプ上昇力', u'?')), cls=[u'center']))
    row2.cells.append(Cell(text=u'腕力', cls=[u'header']))
    row2.cells.append(Cell(text=unicode(j.get(u'腕力', u'?')), cls=[u'center']))
    table.rows.append(row2)

    row3 = Row()
    row3.cells.append(Cell(text=u'よろけにくさ', cls=[u'header']))
    row3.cells.append(Cell(text=unicode(j.get(u'よろけにくさ', u'?')), cls=[u'center']))
    row3.cells.append(Cell(text=u'格闘距離', cls=[u'header']))
    row3.cells.append(Cell(text=unicode(u'%dm' % j.get(u'格闘距離', 0)), cls=[u'right']))
    table.rows.append(row3)

    return table

# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell
from utils.json_loader import load_json_from_page
import WeaponData

Dependencies = ['pages']

def macro_WPData(macro, _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    requested_wps = _trailing_args
    if not requested_wps:
        # assume the caller requested to show a weapon data of the current page.
        requested_wps = [macro.formatter.page.page_name]
    else:
        parser = None

    if len(requested_wps) == 1:
        pass
    else:
        raise NotImplementedError()
    return create_wp_data(request, parser, formatter, requested_wps)

def create_wp_data(request, parser, formatter, requested_wps):
    j = load_json_from_page(request, parser, requested_wps[0], u'wp') or {}
    if not j:
        return u'no wp data'
    table = Table()

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
        row, subrow = get_leveled_weapon_and_subweapon_rows(
            request, j, formatter, name, level, place_name)
        table.rows.append(row)
        if subrow:
            table.rows.append(subrow)
    html_table = table.toHtmlTable()
    text += html_table.format(formatter)
    text += get_tune_table(j, formatter)
    return text

def get_leveled_weapon_and_subweapon_rows(request, j, formatter, name, level, place_name):
    weapon_json = load_json_from_page(request, None, name, u'weapon') or {}
    row = Row()
    row.cells.append(Cell(u'装備箇所', place_name, cls=['center','hc']))
    WeaponData.create_row(request, weapon_json, row, level, formatter,
                          subweapon_in_row=False, subtrigger_in_row=False,
                          show_name=True)
    subrow = Row()
    subrow.cells.append(Cell(u'装備箇所', u'サブ', cls=[u'center','hc']))

    leveled_weapon = weapon_json.get(u'レベル', {}).get(u'%d' % level, {})
    if u'_サブウェポン' in leveled_weapon:
        subweapon = leveled_weapon[u'_サブウェポン']
        subname = subweapon[u'名称']
        sublevel = subweapon[u'レベル']
        subweapon_json = load_json_from_page(request, subname, u'weapon') or {}
        WeaponData.create_row(request, subweapon_json, subrow, sublevel, formatter,
                              subweapon_in_row=False, subtrigger_in_row=False,
                              show_name=True)
        return row, subrow
    elif u'_サブトリガー' in leveled_weapon:
        subtrigger = leveled_weapon[u'_サブトリガー']
        subrow.cells.append(Cell(u'武装名', u'(%s)' % subtrigger, cls=[u'center']))
        # fill empty columns so that this row does not be shorter than the other rows
        subrow.cells.extend([Cell()] * (len(row.cells) - 2))
        return row, subrow
    else:
        return row, None

def get_tune_table(j, formatter):
    tunes = j.get(u'チューン', {})
    if not tunes:
        return u''
    text = u''
    text += formatter.table(True)
    # header row
    text += formatter.table_row(True, {u'rowclass':u'header'})
    for header in [u'チューンLv', u'名称', u'メリット', u'デメリット']:
        text += (formatter.table_cell(True) 
                 + formatter.text(header) 
                 + formatter.table_cell(False))
    text += formatter.table_row(False)
    for i in map(lambda x: u'%d' % x, [2, 3, 4]):
        if i not in tunes:
            break
        tune = tunes[i]

        # align the size of merits and demerits
        merits = tune[u'メリット']
        demerits = tune[u'デメリット']
        merits_len = max(len(merits), len(demerits))
        merits += [u''] * (merits_len - len(merits))
        demerits += [u''] * (merits_len - len(demerits))

        for (j, (merit, demerit)) in enumerate(zip(merits, demerits)):
            text += formatter.table_row(True)

            if j == 0:
                for cell in [i, tune.get(u'名称', u'???')]:
                    text += formatter.table_cell(True, attrs={u'rowspan': u'%d' % merits_len})
                    text += formatter.text(cell)
                    text += formatter.table_cell(False)
            else:
                pass

            for effect in [merit, demerit]:
                text += formatter.table_cell(True)
                text += formatter.text(effect)
                text += formatter.table_cell(False)

            text += formatter.table_row(False)
    text += formatter.table(False)
    return text

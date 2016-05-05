# -*- coding: utf-8 -*-

import os

from utils.table import Table, Row, Cell, TitleRow, TitleCell
from utils.json_loader import load_json_from_page
import WeaponData
from MoinMoin import caching

Dependencies = ['pages']

def macro_CompactWeaponPack(macro, _trailing_args=[]):    
    request = macro.request
    formatter = macro.formatter
    requested_wps = _trailing_args
    if not _trailing_args:
        return u'Please specify at least one WP name.'

    cache = caching.CacheEntry(request, 'gswiki-wpowners', 'wpowners', 'wiki', use_pickle=True)
    if cache.needsUpdate(os.path.join(request.cfg.data_dir, 'edit-log')):
        print u'updating cache'
        wp_to_character = load_wp_to_character_table(request)
        cache.update(wp_to_character)
    else:
        print u'using cache'
        wp_to_character = cache.content()
    import json
    print json.dumps(wp_to_character, ensure_ascii=False)

    output = formatter.table(True)
    for wp_name in requested_wps:
        if wp_name not in wp_to_character:
            continue
        character_name = wp_to_character[wp_name]
        output += wp_to_rows(request, formatter, character_name, wp_name)
    output += formatter.table(False)

    return output

def load_wp_to_character_table(request):
    character_list = load_json_from_page(request, u'CharacterList', u'characters') or []
    wp_to_character = {}
    for character_name in character_list:
        character = load_json_from_page(request, character_name, u'character') or {}
        wp_list = character.get(u'ウェポンパック', [])
        for wp in wp_list:
            wp_to_character[wp] = character_name
    return wp_to_character


def wp_to_rows(request, formatter, character_name, wp_name):
    output = u''
    wp = load_json_from_page(request, wp_name, u'wp') or {}
    
    # First row: WP brief data
    output += formatter.table_row(True, attrs={u'rowclass': u'wpheader'})
    output += formatter.table_cell(True, colspan=4)
    
    output += formatter.pagelink(True, wp_name)
    output += formatter.text(u'%s: %s' % (character_name, wp_name))
    output += formatter.pagelink(False)
    output += formatter.linebreak(preformatted=False)
    cost = wp.get(u'コスト', u'???')
    hp = wp.get(u'耐久力', u'???')
    grapple = wp.get(u'格闘補正', u'???')
    output += formatter.text(
        u'コスト: %s　耐久力: %s　格闘補正: %s' % (cost, hp, grapple),
        style=u'font-size:70%')

    output += formatter.table_cell(False)
    output += formatter.table_row(False)


    return output

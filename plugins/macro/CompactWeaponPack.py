# -*- coding: utf-8 -*-

import base64
import os

from utils.table import Table, Row, Cell, TitleRow, TitleCell
from utils.json_loader import load_json_from_page
import WeaponData
import WPData
from MoinMoin import caching

Dependencies = ['pages']

def macro_CompactWeaponPack(macro, _trailing_args=[], _kwargs={}):
    request = macro.request
    formatter = macro.formatter
    requested_wps = _trailing_args
    if not _trailing_args:
        return u'Please specify at least one WP name.'
    requested_wps.reverse()
    if _kwargs and u'prefix' in _kwargs:
        prefix = _kwargs[u'prefix']
    else:
        prefix = u''

    cache = caching.CacheEntry(
        request,
        'gswiki-wpowners',
        base64.b16encode(prefix.encode('utf-8')) + 'wpowners',
        'wiki',
        use_pickle=True)
    if cache.needsUpdate(os.path.join(request.cfg.data_dir, 'edit-log')):
        wp_to_character = load_wp_to_character_table(request, prefix)
        cache.update(wp_to_character)
    else:
        wp_to_character = cache.content()

    output = formatter.table(True)
    for wp_name in requested_wps:
        if wp_name not in wp_to_character:
            continue
        character_name = wp_to_character[wp_name]
        output += wp_to_rows(request, formatter, character_name, wp_name, prefix)
    output += formatter.table(False)

    return output

def load_wp_to_character_table(request, prefix=u''):
    character_list = load_json_from_page(request, None, prefix + u'CharacterList', u'characters') or []
    wp_to_character = {}
    for character_name in character_list:
        character = load_json_from_page(request, None, prefix + character_name, u'character') or {}
        wp_list = character.get(u'ウェポンパック', [])
        for wp in wp_list:
            wp_to_character[wp] = character_name
    return wp_to_character


def wp_to_rows(request, formatter, character_name, wp_name, prefix=u''):
    output = u''
    wp = load_json_from_page(request, None, prefix + wp_name, u'wp') or {}
    is_xi = WPData.is_xi_wp(request, wp_name, prefix)
    
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

    # Second row: |  | double style | side style | tandem style |
    output += formatter.table_row(True, attrs={u'rowclass': u'sheader'})
    output += formatter.table_cell(True) + formatter.table_cell(False)
    output += formatter.table_cell(True) + formatter.text(u'ダブルスタイル') +  formatter.table_cell(False)
    output += formatter.table_cell(True) + formatter.text(u'サイドスタイル') +  formatter.table_cell(False)
    output += formatter.table_cell(True) + formatter.text(u'タンデムスタイル') +  formatter.table_cell(False)
    output += formatter.table_row(False)

    # Third & forth row: weapons
    right_weapon = wp.get(u'右手武器', {})
    left_weapon = wp.get(u'左手武器', {})
    side_weapon = wp.get(u'サイド武器', {})
    tandem_weapon = wp.get(u'タンデム武器', {})

    def find_sub_weapon(weapon, place_name, prefix):
        weapon_json = load_json_from_page(request, None, prefix + weapon.get(u'名称', u''), u'weapon') or {}
        leveled_weapon = weapon_json.get(u'レベル', {}).get(u'%d' % weapon.get(u'レベル', 0), {})
        subweapon = leveled_weapon.get(u'サブウェポン', {})
        if subweapon:
            return subweapon
        subtrigger = leveled_weapon.get(u'サブトリガー', u'')
        if subtrigger:
            return subtrigger
        if is_xi:
            subname = u'クシーバルカン' if place_name == u'サイド' else u'クシーグレネード'
            return { u'名称': subname, u'レベル': 1 }
        return None

    side_sub_weapon = find_sub_weapon(side_weapon, u'サイド', prefix)
    tandem_sub_weapon = find_sub_weapon(tandem_weapon, u'タンデム', prefix)

    def get_weapon_name(weapon):
        if isinstance(weapon, unicode):
            return u'(%s)' % weapon
        else:
            return u'%s Lv%d' % (weapon.get(u'名称', u'???'), weapon.get(u'レベル', 0))

    def get_weapon_link(weapon, prefix=u''):
        weapon_name = get_weapon_name(weapon)
        if isinstance(weapon, unicode):
            return formatter.text(weapon_name)
        else:
            return (formatter.pagelink(True, prefix + weapon.get(u'名称', u'???'))
                    + formatter.text(weapon_name)
                    + formatter.pagelink(False))

    # first row of weapons rows
    output += formatter.table_row(True)
    output += formatter.table_cell(True) + formatter.text(u'右') + formatter.table_cell(False)
    output += formatter.table_cell(True) + get_weapon_link(right_weapon, prefix) + formatter.table_cell(False)

    output += formatter.table_cell(True, rowspan=(1 if side_sub_weapon else 2))
    output += get_weapon_link(side_weapon, prefix)
    output += formatter.table_cell(False)
    output += formatter.table_cell(True, rowspan=(1 if tandem_sub_weapon else 2))
    output += get_weapon_link(tandem_weapon, prefix)
    output += formatter.table_cell(False)
    output += formatter.table_row(False)

    # second row of weapons rows
    output += formatter.table_row(True)
    output += formatter.table_cell(True) + formatter.text(u'左') + formatter.table_cell(False)
    output += formatter.table_cell(True) + get_weapon_link(left_weapon, prefix) + formatter.table_cell(False)

    if side_sub_weapon: 
        output += formatter.table_cell(True) + get_weapon_link(side_sub_weapon, prefix) + formatter.table_cell(False)
    if tandem_sub_weapon: 
        output += formatter.table_cell(True) + get_weapon_link(tandem_sub_weapon, prefix) + formatter.table_cell(False)
    output += formatter.table_row(False)

    return output

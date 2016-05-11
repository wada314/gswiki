#!/usr/bin/python2
# -*- coding: utf-8 -*-

"""
You may need to replace the security policy (page read/write/delete policies)
in your wiki config like this:
    #from MoinMoin.security.antispam import SecurityPolicy
    from MoinMoin.security import Default as DefaultPolicy
    class SecurityPolicy(DefaultPolicy):
        def write(self, _):
            return True
        def delete(self, _):
            return True
"""

import sys
sys.path.append('/home/shohei/gs3/myplugin/plugins')
sys.path.append('/home/shohei/gs3/moin-1.9.8')
import re
import json
import argparse

from MoinMoin.PageEditor import PageEditor
from MoinMoin.web.contexts import ScriptContext
from MoinMoin.web.request import TestRequest
from MoinMoin.Page import RootPage

from macro.utils import json_printer, json_loader

WP_PAGE_DEFAULT_BODY_PRE = u'''
=== @PAGE@ ===
<<WPData>>

==== 解説 ====

==== コメント ====
<<AddComment>>
<<Comments>>

{{{#!wp
'''

WP_PAGE_DEFAULT_BODY_POST = u'''
}}}
'''

WEAPON_PAGE_DEFAULT_BODY_PRE = u'''
=== @PAGE@ ===
<<WeaponData>>

==== 解説 ====

==== コメント ====
<<AddComment>>
<<Comments>>

{{{#!weapon
'''

WEAPON_PAGE_DEFAULT_BODY_POST = u'''
}}}
'''

RE_WP_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!wp)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)
RE_WEAPON_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!weapon)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)
RE_CHARA_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!character)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)

WEAPON_INTERNAL_TO_ATTRS = {
    u'ATK': u'攻撃力',
    u'BATK': u'散弾攻撃力',
    u'EXATK': u'攻撃力(爆風)',
    u'RAP': u'連射間隔',
    u'NUM': u'装填数',
    u'RANGE': u'射程距離',
    u'BRANGE': u'散弾射程',
    u'EXRANGE': u'爆発半径',
    u'CHARGE': u'発射準備時間',
    u'ROCK': u'ロックオン時間',
    u'RECO': u'回復力',
    u'DEF': u'防御力',
    u'SRANGE': u'シールド範囲',
    u'CONTI': u'最低持続時間',
    u'SUCK': u'吸引力',
    u'ATKRAN': u'攻撃範囲',
    u'RECORAN': u'回復範囲',
    u'SUPP': u'弾薬補給量',
    u'SUPRAN': u'弾薬回復範囲',
    u'MOVE': u'移動時間',
    u'STIME': u'シールド展開時間',
    u'TIME': u'効果時間',
}
# Special cases need to be handled:
#    "RELO": "リロード性能", It's frac (string) generally. e.g. "4/300F"
#    "DAMA": "反動", It may be a string like "30%" or an integer like "20".
RE_NUMBER = re.compile(ur'^[0-9]+$')
RE_DISTANCE = re.compile(ur'^[0-9]+(?:\.[0-9]+)?m$')
RE_FRAME_NUMBER = re.compile(ur'^[0-9]+F$')

def masterToAttrs(master):

    def maybeToInt(s):
        if RE_NUMBER.match(s):
            return int(s)
        elif RE_FRAME_NUMBER.match(s):
            return int(s[:-1])
        elif RE_DISTANCE.match(s):
            return float(s[:-1])
        else:
            return s

    attrs = {}
    i = 1
    while True:
        field_name = u'weaponStatus%d' % i
        kv = master.get(field_name, u'')
        if not kv or u'=' not in kv:
            break
        key, value = kv.split(u'=', 1)
        if key in WEAPON_INTERNAL_TO_ATTRS:
            attrs[WEAPON_INTERNAL_TO_ATTRS[key]] = maybeToInt(value)
        elif key == u'RELO':
            value1, value2 = value.split(u'/', 1)
            attrs[u'リロード分母'] = maybeToInt(value2)
            if value1 == u'全弾':
                attrs[u'リロード分子'] = u'all'
            else:
                attrs[u'リロード分子'] = maybeToInt(value1)
        elif key == u'DAMA':
            if RE_NUMBER.match(value):
                attrs[u'反動ダメージ量'] = maybeToInt(value)
            else:
                attrs[u'反動ダメージ割合'] = int(value[:-1])
        else:
            raise Exception('Unknown weapon status key %s' % kv.encode('utf-8'))
        i += 1
    return attrs

def processWeaponPack(j, context, dry_run):
    wp_name = j.get(u'weaponPackName', None)
    if not wp_name:
        return
    page = PageEditor(context, wp_name)
    body_pre = u''
    body_json = {}
    body_post = u''
    if page.isStandardPage():
        match = RE_WP_PAGE.match(page.get_body())
        if match:
            body_pre = match.group(u'pre')
            body_post = match.group(u'post')
            try:
                body_json = json.loads(match.group(u'body'))
            except Error:
                pass

    def getBriefWeaponJson(weapon):
        return {
            u'名称': weapon.get(u'weaponName'),
            u'レベル': weapon.get(u'weaponLevel'),
        }

    w_map = j.get(u'weaponMap', {})
    json_diff = {
        u'コスト': j.get(u'cost', 0),
        u'耐久力': j.get(u'hitPoint', 0),
        u'格闘補正': j.get(u'grappleUp', 1.0),
        u'右手武器': getBriefWeaponJson(w_map.get(u'right', {})),
        u'左手武器': getBriefWeaponJson(w_map.get(u'left', {})),
        u'サイド武器': getBriefWeaponJson(w_map.get(u'side', {})),
        u'タンデム武器': getBriefWeaponJson(w_map.get(u'tandem', {})),
    }

    if not body_json:
        body_pre = WP_PAGE_DEFAULT_BODY_PRE
        body_json = {
            u'名称': wp_name,
            u'入手条件': u''
        }
        body_post = WP_PAGE_DEFAULT_BODY_POST

    body_json.update(json_diff)

    output = (body_pre + u'\n'
              + json_printer.print_json(body_json, indent=2) + u'\n'
              + body_post)

    try:
        if not dry_run:
            page.saveText(output, page.current_rev())
            print u'Processed %s correctly.' % wp_name
        else:
            print u'(dry_run) Processed %s correctly.' % wp_name
    except PageEditor.Unchanged:
        pass

def processWpPackAddToCharacter(j, context, dry_run):
    wp_name = j.get(u'weaponPackName', None)
    if not wp_name:
        return
    all_j = json_loader.load_all_jsons(context) or {}
    characters_j = all_j.get(u'characters', [])
    owner_name = u''
    for character_j in characters_j:
        if character_j.get(u'携帯サイトID', -1) == j.get(u'master', {}).get(u'equipmentCharaId', -2):
            owner_name = character_j.get(u'名称', u'')
            break
    if not owner_name:
        print u'WP %s \'s owner not found.' % wp_name
        return

    page = PageEditor(context, owner_name)
    if not page.isStandardPage():
        print u'Character %s \'s page is not created yet.' % owner_name
        return

    match = RE_CHARA_PAGE.match(page.get_body())
    if not match:
        print u'Character %s \'s page may be broken (outside of json).' % owner_name
        return

    body_pre = match.group(u'pre')
    body_post = match.group(u'post')
    try:
        body_json = json.loads(match.group(u'body'))
    except Error:
        print u'Character %s \'s page may be broken (inside of json).' % owner_name
        return

    new_wp_list = body_json.get(u'ウェポンパック', []) or []
    if wp_name not in new_wp_list:
        new_wp_list.append(wp_name)
    body_json[u'ウェポンパック'] = new_wp_list

    output = (body_pre + u'\n'
              + json_printer.print_json(body_json, indent=2) + u'\n'
              + body_post)

    try:
        if not dry_run:
            page.saveText(output, page.current_rev())
            print u'Processed %s.append(%s) correctly.' % (owner_name, wp_name)
        else:
            print u'(dry_run) Processed %s.append(%s) correctly.' % (owner_name, wp_name)
    except PageEditor.Unchanged:
        pass


def processWeapon(j, context, is_sub, dry_run):
    master = j.get(u'subMaster' if is_sub else u'master', {}) or {}
    status_map = j.get(u'subStatusMap' if is_sub else  u'statusMap', {}) or {}
    weapon_name = master.get(u'weaponName', u'').strip()
    level = master.get(u'weaponLevel', 0)
    if not master or not status_map or not weapon_name or not level:
        print u'Weapon %s is missing critical params.' % weapon_name
        return

    page = PageEditor(context, weapon_name)
    body_pre = u''
    body_json = {}
    body_post = u''
    if page.isStandardPage():
        match = RE_WEAPON_PAGE.match(page.get_body())
        if match:
            body_pre = match.group(u'pre')
            body_post = match.group(u'post')
            try:
                body_json = json.loads(match.group(u'body'))
            except Error:
                pass

    diff_dst_json = masterToAttrs(master)

    if not body_json:
        body_pre = WEAPON_PAGE_DEFAULT_BODY_PRE
        body_post = WEAPON_PAGE_DEFAULT_BODY_POST
        body_json = {
            u'名称': weapon_name,
            u'レベル': {},
            u'弾種': j.get(u'subBulletTypeName' if is_sub else u'bulletTypeName', u''),
        }

    levels_json = body_json.get(u'レベル', {})
    if not levels_json:
        levels_json = {}
        body_json[u'レベル'] = levels_json

    dst_json = levels_json.get(u'%d' % level, {})
    if not dst_json:
        dst_json = {}
        levels_json[u'%d' % level] = dst_json

    dst_json.update(diff_dst_json)

    output = (body_pre + u'\n'
              + json_printer.print_json(body_json, indent=2) + u'\n'
              + body_post)

    try:
        if not dry_run:
            page.saveText(output, page.current_rev())
            print u'Processed weapon %s correctly.' % weapon_name
        else:
            print u'(dry_run) Processed weapon %s correctly.' % weapon_name
    except PageEditor.Unchanged:
        pass

    if not is_sub and j.get(u'subMaster', {}) and j.get(u'subStatusMap', {}):
        processWeapon(j, context, True, dry_run)

if __name__ == '__main__':
    from MoinMoin import config
    context = ScriptContext()
    context.remote_addr = '127.0.0.1'
    root_page = RootPage(context)

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=file)
    parser.add_argument('--no-dry-run', dest='no_dry_run', type=bool, default=True)
    args = parser.parse_args()

    dry_run = not args.no_dry_run
    
    json_lines = args.file.readlines()

    for json_text in json_lines:
        j = json.loads(json_text)
        processWeaponPack(j, context, dry_run)
        processWpPackAddToCharacter(j, context, dry_run)
        for weapon_slot in [u'right', u'left', u'side', u'tandem']:
            processWeapon(j.get(u'weaponMap', {}).get(weapon_slot, {}), context, False, dry_run)

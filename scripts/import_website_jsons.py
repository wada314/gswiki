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
import difflib

from MoinMoin.PageEditor import PageEditor
from MoinMoin.web.contexts import ScriptContext
from MoinMoin.web.request import TestRequest
from MoinMoin.Page import RootPage

from macro.utils import json_printer, json_loader

PAGE_PREFIX = u'sigma/'

WP_PAGE_DEFAULT_BODY_PRE = u'''
=== %(名称)s ===
<<WPData("sigma/")>>

==== 解説 ====

{{{#!wp
'''

WP_PAGE_DEFAULT_BODY_POST = u'''
}}}

==== コメント ====
<<AddComment>>
<<Comments>>
'''

WEAPON_PAGE_DEFAULT_BODY_PRE = u'''
=== %(名称)s ===
<<WeaponData("sigma/")>>

==== 解説 ====

{{{#!weapon
'''

WEAPON_PAGE_DEFAULT_BODY_POST = u'''
}}}

==== コメント ====
<<AddComment>>
<<Comments>>
'''

RE_WP_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!wp)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)
RE_WEAPON_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!weapon)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)
RE_CHARA_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!character)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)

WEAPON_ATTRS = {
    u'攻撃力',
    u'散弾攻撃力',
    u'攻撃力(爆風)',
    u'覚醒攻撃力',
    u'連射間隔',
    u'装填数',
    u'射程距離',
    u'散弾射程',
    u'爆発範囲',
    u'発射準備時間',
    u'ロックオン時間',
    u'回復力',
    u'防御力',
    u'吸引力',
    u'シールド範囲',
    u'最低持続時間',
    u'攻撃範囲',
    u'回復範囲',
    u'弾薬補給量',
    u'弾薬回復範囲',
    u'移動時間',
    u'シールド展開時間',
    u'効果時間',
    u'チャージ時間',
    u'点火時間',
}
# Special cases need to be handled:
#    "RELO": "リロード性能", It's frac (string) generally. e.g. "4/300F"
#    "DAMA": "反動", It may be a string like "30%" or an integer like "20".
RE_NUMBER = re.compile(ur'^[0-9]+$')
RE_DISTANCE = re.compile(ur'^[0-9]+(?:\.[0-9]+)?\s*m$')
RE_FRAME_NUMBER = re.compile(ur'^[0-9]+\s*F$')
RE_FRAME_NUMBER_TEXT = re.compile(ur'^[0-9]+\s*フレーム$')
RE_FEEDBACK_DAMAGE = re.compile(ur'^回復量の([0-9]+)%$')

def statusMapToAttrs(status_map):

    def maybeToInt(s):
        if RE_NUMBER.match(s):
            return int(s)
        elif RE_FRAME_NUMBER.match(s):
            return int(s[:-1])
        elif RE_FRAME_NUMBER_TEXT.match(s):
            return int(s[:-4])
        elif RE_DISTANCE.match(s):
            return float(s[:-1])
        else:
            return s

    attrs = {}
    for key,value in status_map.iteritems():
        if not value:
            continue
        if key in WEAPON_ATTRS:
            attrs[key] = maybeToInt(value)
        elif key == u'射撃間隔':
            attrs[u'連射間隔'] = maybeToInt(value)
        elif key == u'リロード性能':
            if u'/' in value:
                value1, value2 = value.split(u'/', 1)
                value1 = value1.strip()
                value2 = value2.strip()
            else:
                value1 = u'1'
                value2 = value2.strip()
            attrs[u'リロード分母'] = maybeToInt(value2)
            if value1 == u'全弾':
                attrs[u'リロード分子'] = u'all'
            else:
                attrs[u'リロード分子'] = maybeToInt(value1)
        elif key == u'反動ダメージ':
            if RE_NUMBER.match(value):
                attrs[u'反動ダメージ量'] = maybeToInt(value)
            else:
                attrs[u'反動ダメージ割合'] = int(RE_FEEDBACK_DAMAGE.match(value).group(1))
        else:
            raise Exception('Unknown weapon status key %s' % key.encode('utf-8'))
    return attrs

def processWeaponPack(j, context, dry_run):
    wp_name = j.get(u'weaponPackName', None)
    if not wp_name:
        return
    page = PageEditor(context, PAGE_PREFIX + wp_name)
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
            u'名称': weapon.get(u'weaponName').strip(),
            u'レベル': weapon.get(u'weaponLevel'),
        }

    w_map = j.get(u'weaponMap', {})
    json_diff = {
        u'コスト': j.get(u'cost', 0),
        u'耐久力': j.get(u'hitPoint', 0),
        u'格闘補正': float(j.get(u'grappleUp', 1.0)),
        u'右手武器': getBriefWeaponJson(w_map.get(u'right', {})),
        u'左手武器': getBriefWeaponJson(w_map.get(u'left', {})),
        u'サイド武器': getBriefWeaponJson(w_map.get(u'side', {})),
        u'タンデム武器': getBriefWeaponJson(w_map.get(u'tandem', {})),
    }

    if not body_json:
        body_json = {
            u'名称': wp_name,
            u'入手条件': u'',
            u'タイプ': u''
        }
        body_pre = WP_PAGE_DEFAULT_BODY_PRE % body_json
        body_post = WP_PAGE_DEFAULT_BODY_POST

    body_json.update(json_diff)

    output = (body_pre + u'\n'
              + json_printer.print_json(body_json, indent=2) + u'\n'
              + body_post)

    try:
        if not dry_run:
            page.saveText(output, page.current_rev())
            print u'Processed %s correctly.' % (PAGE_PREFIX + wp_name)
        else:
            differ = difflib.Differ()
            l = map(lambda s: s.strip(), page.get_body().splitlines())
            r = map(lambda s: s.strip(), output.splitlines())
            if l != r:
                d = u'\n'.join(filter(lambda s: s and s[0] in u'+-?', differ.compare(l, r)))
                print((u'#### Diff in wp %s ####' % (PAGE_PREFIX + wp_name)).encode('utf-8'))
                print(d.encode('utf-8'))
    except PageEditor.Unchanged:
        pass

def processWeapon(j, context, is_sub, dry_run):
    status_map = j.get(u'subStatusMap' if is_sub else  u'statusMap', {}) or {}
    weapon_name = j.get(u'subWeaponName' if is_sub else u'weaponName', u'').strip()
    level = j.get(u'subWeaponLevel' if is_sub else u'weaponLevel', 0)
    if not status_map or not weapon_name or not level:
        print u'Weapon %s is missing critical params.' % weapon_name
        return

    page = PageEditor(context, PAGE_PREFIX + weapon_name)
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

    diff_dst_json = statusMapToAttrs(status_map)
    if not is_sub and j.get(u'subStatusMap', {}):
        diff_dst_json[u'サブウェポン'] = {
            u'名称': j[u'subWeaponName'].strip(),
            u'レベル': int(j[u'subWeaponLevel']),
        }

    if not body_json:
        body_json = {
            u'名称': weapon_name,
            u'レベル': {},
            u'弾種': j.get(u'subBulletTypeName' if is_sub else u'bulletTypeName', u''),
        }
        body_pre = WEAPON_PAGE_DEFAULT_BODY_PRE % body_json
        body_post = WEAPON_PAGE_DEFAULT_BODY_POST

    levels_json = body_json.get(u'レベル', {})
    if not levels_json:
        levels_json = {}
        body_json[u'レベル'] = levels_json

    dst_json = levels_json.get(u'%d' % level, {})
    if not dst_json:
        dst_json = {}
        levels_json[u'%d' % level] = dst_json

    dst_json.update(diff_dst_json)
    # clenup legacy attrs
    if u'爆発半径' in dst_json:
        del dst_json[u'爆発半径']
    if u'発射準備時間' in dst_json:
        del dst_json[u'発射準備時間']

    output = (body_pre + u'\n'
              + json_printer.print_json(body_json, indent=2) + u'\n'
              + body_post)

    try:
        if not dry_run:
            page.saveText(output, page.current_rev())
            print u'Processed weapon %s correctly.' % (PAGE_PREFIX + weapon_name)
        else:
            differ = difflib.Differ(charjunk=lambda c:c.isspace())
            l = map(lambda s: s.strip(), page.get_body().splitlines())
            r = map(lambda s: s.strip(), output.splitlines())   
            if l != r:
                d = u'\n'.join(filter(lambda s: s and s[0] in u'+-?', differ.compare(l, r)))
                print((u'#### Diff in weapon %s ####' % (PAGE_PREFIX + weapon_name)).encode('utf-8'))
                print(d.encode('utf-8'))
    except PageEditor.Unchanged:
        pass

    if not is_sub and j.get(u'subStatusMap', {}):
        processWeapon(j, context, True, dry_run)

if __name__ == '__main__':
    from MoinMoin import config
    context = ScriptContext()
    context.remote_addr = '127.0.0.1'
    root_page = RootPage(context)

    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=file)
    parser.add_argument('--no-dry-run', dest='no_dry_run', type=bool, default=False)
    args = parser.parse_args()

    dry_run = not args.no_dry_run
    
    json_lines = args.file.readlines()

    for json_text in json_lines:
        j = json.loads(json_text)
        if not isinstance(j, list):
            j = [j]
        for item in j:
            processWeaponPack(item, context, dry_run)
            for weapon_slot in [u'right', u'left', u'side', u'tandem']:
                processWeapon(item.get(u'weaponMap', {}).get(weapon_slot, {}), context, False, dry_run)

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
RE_WP_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!wp)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)
RE_CHARA_PAGE = re.compile(ur'^(?P<pre>.*{{{\s*#!character)(?P<body>.*)(?P<post>}}}.*)$', re.DOTALL)

def processWeaponPack(j, context):
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
        page.saveText(output, page.current_rev())
    except PageEditor.Unchanged:
        pass

def processWpPackAddToCharacter(j, context):
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
    new_wp_list.append(wp_name)
    body_json[u'ウェポンパック'] = new_wp_list

    output = (body_pre + u'\n'
              + json_printer.print_json(body_json, indent=2) + u'\n'
              + body_post)

    try:
        page.saveText(output, page.current_rev())
    except PageEditor.Unchanged:
        pass

if __name__ == '__main__':
    from MoinMoin import config
    context = ScriptContext()
    context.remote_addr = '127.0.0.1'
    root_page = RootPage(context)

    if len(sys.argv) != 2:
        print u'This script must be run with the path to the line-separated json file name.'
        exit(1)
    
    f = open(sys.argv[1], 'r')
    if not f:
        print u'The given file %s is not openable.' % sys.argv[1]
        exit(1)

    json_lines = f.readlines()

    for json_text in json_lines:
        j = json.loads(json_text)
        processWeaponPack(j, context)
        processWpPackAddToCharacter(j, context)

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
# TODO: Do something for these path...
sys.path.append('/home/shohei/gs3/gs2')
sys.path.append('/home/shohei/gs3/moin-1.9.8')
import re

from MoinMoin.PageEditor import PageEditor
from MoinMoin.web.contexts import ScriptContext
from MoinMoin.web.request import TestRequest
from MoinMoin.Page import RootPage

RE_OLD_INCLUDE_WEAPON = re.compile(ur'<<Include\(data/weapons.*>>')
RE_OLD_INCLUDE_WP = re.compile(ur'<<Include\(data/wps.*>>')
RE_OLD_FIND_OWNERS = re.compile(ur'<<FindWpOwner.*>>\n')
RE_OLD_INCLUDE_CHARACTER = re.compile(ur'<<Include\(data/characters/.*>>')

RE_OLD_INCLUDE_CHARACTER_LIST = re.compile(ur'<<Include\(data/characterList,.*>>')

def process_weapon_pages(data_page, text_page):
    print u'processing %s' % text_page.page_name
    json_data = data_page.get_raw_body()
    text_data = text_page.get_raw_body()
    if not json_data:
        return

    text_data = re.sub(
        RE_OLD_INCLUDE_WEAPON,
        u'''=== %s ===
<<WeaponData>>''' % text_page.page_name,
        text_data)

    text_data += u'''
{{{#!weapon
%s
}}}''' % json_data

    text_page.saveText(text_data, text_page.current_rev())
    data_page.deletePage()

def process_wp_pages(data_page, text_page):
    print u'processing %s' % text_page.page_name
    json_data = data_page.get_raw_body()
    text_data = text_page.get_raw_body()
    if not json_data:
        return

    text_data = re.sub(
        RE_OLD_INCLUDE_WP,
        u'<<WPData>>',
        text_data)
    text_data = re.sub(RE_OLD_FIND_OWNERS, u'', text_data)

    text_data += u'''
{{{#!wp
%s
}}}''' % json_data

    text_page.saveText(text_data, text_page.current_rev())
    data_page.deletePage()

def process_character_pages(data_page, text_page):
    print u'processing %s' % text_page.page_name
    json_data = data_page.get_raw_body()
    text_data = text_page.get_raw_body()
    if not json_data:
        return

    text_data = re.sub(
        RE_OLD_INCLUDE_CHARACTER,
        u'''
== キャラクター性能 ==
<<CharacterData>>

== 所有WP ==
<<CharacterWPs>>''',
        text_data)

    text_data += u'''
{{{#!character
%s
}}}''' % json_data

    text_page.saveText(text_data, text_page.current_rev())
    data_page.deletePage()

def process_common_pages(page):
    text_data = page.get_raw_body()

    if page.page_name == u'data/characterList':
        text_data = u'''
<<CharacterList>>
{{{#!characters
%s
}}}''' % text_data
        page.saveText(text_data, page.current_rev())
        page.renamePage(u'CharacterList')

    text_data = re.sub(
        RE_OLD_INCLUDE_CHARACTER_LIST,
        u'''
=== キャラクター一覧 ===
<<CharacterList>>''',
        text_data)

    page.saveText(text_data, page.current_rev())

if __name__ == '__main__':
    from MoinMoin import config
    context = ScriptContext()
    context.remote_addr = '127.0.0.1'
    root_page = RootPage(context)
    i = True
    for page_name in root_page.getPageList(user=''):
        if page_name.startswith(u'data/weapons/'):
            data_page = PageEditor(context, page_name)
            text_page = PageEditor(context, page_name[len(u'data/weapons/'):])
            if data_page.isStandardPage(False) and text_page.isStandardPage(False):
                try:
                    process_weapon_pages(data_page, text_page)
                except PageEditor.AccessDenied as e:
                    print e
        elif page_name.startswith(u'data/wps/'):
            data_page = PageEditor(context, page_name)
            text_page = PageEditor(context, page_name[len(u'data/wps/'):])
            if data_page.isStandardPage(False) and text_page.isStandardPage(False):
                try:
                    process_wp_pages(data_page, text_page)
                except PageEditor.AccessDenied as e:
                    print e
        elif page_name.startswith(u'data/characters/'):
            data_page = PageEditor(context, page_name)
            text_page = PageEditor(context, page_name[len(u'data/characters/'):])
            if data_page.isStandardPage(False) and text_page.isStandardPage(False):
                try:
                    process_character_pages(data_page, text_page)
                except PageEditor.AccessDenied as e:
                    print e
        else:
            page = PageEditor(context, page_name)
            if page.isStandardPage(False):
                try:
                    process_common_pages(page)
                    print u'processed %s' % page.page_name
                except PageEditor.AccessDenied as e:
                    print page.request.user.may
                    print u'while processing %s' % page.page_name
                    print e
                except PageEditor.Unchanged as e:
                    pass

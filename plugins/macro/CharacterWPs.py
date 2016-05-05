
# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell
from utils.json_loader import load_json_from_page

from MoinMoin.macro import Include

Dependencies = ['pages']

generates_headings = True

def macro_CharacterWPs(macro, character_name=None):
    request = macro.request
    formatter = macro.formatter

    if not character_name:
        character_name = macro.formatter.page.page_name

    return create_wp_list(macro, request, formatter, character_name)

def create_wp_list(macro, request, formatter, character_name):
    j = load_json_from_page(request, character_name, u'character')
    if not j:
        return 'No WP(s) are defined for this character.'

    j = j.get(u'ウェポンパック', [])
    text = u''
    for wp_name in j:
        include_args = u'%s, , , to="==== コメント ===="' % (wp_name, )
        text += Include.execute(macro, include_args)
    return text

# -*- coding: utf-8 -*-

from utils.table import Table, Row, Cell
from utils.json_loader import load_json_from_page

Dependencies = ['pages']

def macro_CharacterList(macro, prefix=u'', _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter

    characters = get_character_list(request, prefix) or []
    text = formatter.bullet_list(True)
    for c in characters:
        text += formatter.listitem(True)
        text += formatter.pagelink(True, prefix + c)
        text += formatter.text(c)
        text += formatter.pagelink(False)
        text += formatter.listitem(False)
    text += formatter.bullet_list(False)
    return text

def get_character_list(request, prefix):
    return load_json_from_page(request, None, prefix + u'CharacterList', u'characters')

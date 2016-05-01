#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/shohei/gs3/gs2')
sys.path.append('/home/shohei/gs3/moin-1.9.8')

from MoinMoin.PageEditor import PageEditor
from MoinMoin.web.contexts import ScriptContext
from MoinMoin.web.request import TestRequest
from MoinMoin.Page import RootPage

if __name__ == '__main__':
    from MoinMoin import config
    context = ScriptContext()
    request = context.request
    root_page = RootPage(context)
    for page in root_page.getPageList(user=''):
        print page

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

COMMENTS = u'''==== コメント ====
<<AddComment>>
<<Comments>>'''

RE_COMMENTS = re.compile(ur'====\s*コメント\s*====\s*<<AddComment>>\s*<<Comments>>')

if __name__ == '__main__':
    from MoinMoin import config
    context = ScriptContext()
    context.remote_addr = '127.0.0.1'
    root_page = RootPage(context)

    for page_name in root_page.getPageList(user=''):
        page = PageEditor(context, page_name)
        data = page.get_raw_body()
        match = RE_COMMENTS.search(data)
        if match:
            data = RE_COMMENTS.sub(u'', data)
            data += COMMENTS
            page.saveText(data, page.current_rev())

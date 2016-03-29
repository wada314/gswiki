# -*- coding: utf-8 -*-
"""
    MoinMoin - BriefRecentChanges Macro
    @copyright: 2014 wada314 <wiki@wada314.jp>

    Based on RecentChanges macro, copyrights following:

    Parameter "ddiffs" by Ralf Zosel <ralf@zosel.com>, 04.12.2003.

    @copyright: 2000-2004 Juergen Hermann <jh@web.de>
    @license: GNU GPL, see COPYING for details.
"""
import time

from MoinMoin import log
logging = log.getLogger(__name__)

from MoinMoin import util, wikiutil
from MoinMoin.Page import Page
from MoinMoin.logfile import editlog

#############################################################################
### RecentChanges Macro
#############################################################################

Dependencies = ["time"] # ["user", "pages", "pageparams", "bookmark"]

def format_page_edits(macro, line):
    request = macro.request
    _ = request.getText
    pagename = line.pagename
    rev = int(line.rev)
    page = Page(request, pagename)

    html_link = u''
    if not page.exists():
        revbefore = rev - 1
        if revbefore and page.exists(rev=revbefore, domain='standard'):
            # indicate page was deleted and show diff to last existing revision of it
            html_link = page.link_to_raw(request, u'(削除) %s' % pagename,
                                         querystr={'action': 'diff'}, rel='nofollow')
        else:
            html_link = pagename
    else:
        html_link = page.link_to(request, pagename, rel='nofollow')

    return u'<li>%s</li>' % html_link

def macro_BriefRecentChanges(macro, num=20):
    request = macro.request
    _ = request.getText
    output = []
    user = request.user
    page = macro.formatter.page
    pagename = page.page_name

    log = editlog.EditLog(request)

    tnow = time.time()

    output.append(u'<!-- -->')

    pages = []
    ignore_pages = set([u'BadContent'])

    today = request.user.getTime(tnow)[0:3]
    this_day = today
    remaining_item_num = num

    def flush_pages(pages):
        # new day reached: print out stuff

        #pages.sort(lambda p, q: cmp(q.time_tuple, p.time_tuple))

        date = request.user.getFormattedDate(wikiutil.version2timestamp(pages[0].ed_time_usecs))
        output.append(u'<h5>%s</h5><ul>' % date)

        for p in pages:
            output.append(format_page_edits(macro, p))

        output.append(u'</ul>')


    for line in log.reverse():
        if remaining_item_num <= 0:
            break

        if not request.user.may.read(line.pagename):
            continue
        # do not show data changes, it may confusing...
        if line.pagename.startswith(u'data/'):
            continue

        line.time_tuple = request.user.getTime(wikiutil.version2timestamp(line.ed_time_usecs))
        day = line.time_tuple[0:3]

        if this_day != day and len(pages) > 0:
            this_day = day
            if len(pages) > remaining_item_num:
                pages = pages[:remaining_item_num]
            remaining_item_num -= len(pages)
            flush_pages(pages)
            pages = []

        elif this_day != day:
            # new day but no changes
            this_day = day

        if line.pagename in ignore_pages:
            continue
        else:
            ignore_pages.add(line.pagename)
            pages.append(line)
    else:
        if pages:
            if len(pages) > remaining_item_num:
                pages = pages[:remaining_item_num]
            flush_pages(pages)

    output.append(u'<!-- -->')

    return ''.join(output)



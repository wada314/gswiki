# -*- coding: utf-8 -*-
"""
    MoinMoin - gs2mobile theme

    @copyright: 2003-2005 Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.theme import ThemeBase
from MoinMoin.Page import Page

from StringIO import StringIO

class Theme(ThemeBase):

    name = "gs2mobile"

    def header(self, d, **kw):
        """ Assemble wiki header

        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),

            # Header
            u'<div id="header">',
            u'<div id="locationline">',
            self.interwiki(d),
            self.title(d),
            u'</div>',

            self.username(d),
            self.trail(d),

            self.searchform(d),
            self.editbar(d),

            u'</div>', # <header>

            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),

            u'<div>',
            self.msg(d),
            u'</div>',

            # Start of page
            self.sidebar(d),
            self.startPage(),
        ]
        return u'\n'.join(html)

    def sidebar(self, d):
        """ Assemble wiki sidebar """
        name = u'サイドバー'
        page = Page(self.request, name)
        if not page.exists():
            return u''

        buff = StringIO()
        self.request.redirect(buff)
        page.send_page(content_only=1)
        self.request.redirect()
        return u'<div id="sidebar">%s</div>' % buff.getvalue()

    def title(self, d):
        return u'<div id="pagelocation">%s</div>' % d['title_text']

    def favicon(self, d, **keywords):
        return u'''
<link rel="shortcut icon" href="%(link)s" type="image/vnd.microsoft.icon" />
<link rel="icon" href="%(link)s" type="image/vnd.microsoft.icon" />
''' % {u'link': self.cfg.url_prefix_static + 
       u'/gs2mobile/img/gs2logo_bullet_favicon.png'}

    def editorheader(self, d, **kw):
        """ Assemble wiki header for editor

        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),

            # Header
            u'<div id="header">',
            self.title(d),
            u'</div>',

            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),

            # Start of page
            self.msg(d),
            self.sidebar(d),
            self.startPage(),
        ]
        return u'\n'.join(html)

    def footer(self, d, **keywords):
        """ Assemble wiki footer

        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            # End of page
            self.pageinfo(page),
            self.endPage(),

            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),

            # Footer
            u'<div id="footer">',
            self.editbar(d),
            self.credits(d),
            self.showversion(d, **keywords),
            u'</div>',

            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)

def execute(request):
    """
    Generate and return a theme object

    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)


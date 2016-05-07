# -*- coding: utf-8 -*-
"""
    MoinMoin - Collapsible Section  macro

    This macro provides a way to display the contents of another page into
    an HTML div that can be collapsed and expanded. Its useful for including
    supplemental information in a page that normal users might not care about.

    Example Usage:
     collapsed by default:
        <<CollapsibleSection("Title for Section", "PageName")>>
     expanded by default:
        <<CollapsibleSection("Title for Section", "PageName", 1)>>
        <<CollapsibleSection("Title for Section", "PageName", 1, "h3")>>
     set custom plus/minus signs:
        <<CollapsibleSection("Title for Section", "PageName", 1, "h3", plus=++, minus=--)>>

    @license: GNU GPL, see COPYING for details.
    @author: Andy Doan <andy.doan@linaro.org>
"""

from MoinMoin import wikiutil
from MoinMoin.macro import Include

section_js = u"""
<style type="text/css">
.CollapsibleSection {cursor: pointer;}
</style>
<script type='text/javascript'>
    function toggle_viz(id) {
        div = document.getElementById(id);
        h2 = document.getElementById('h2_'+id);
        if (div.style.display == 'none' ) {
            div.style.display = 'block';
            //strip the - from the old text
            old = h2.innerHTML.substring(2);
            h2.innerHTML = "%s" + " " + old;
        }
        else {
            div.style.display = 'none';
            //strip the "- " from the old text
            old = h2.innerHTML.substring(2)
            h2.innerHTML = "%s" + " " + old;
        }
    }
</script>
"""
section_template = u"""
<%s class='CollapsibleSection' id='h2_%s' onclick='toggle_viz("%s")'>%s</%s>
<div id='%s'>
%s
</div>
"""

section_hide_template = u"""
<script type='text/javascript'>
toggle_viz('%s');
</script>
"""

section_base = 'CollapsibleSection'

def macro_CollapsibleSection(macro, title, page, visible=False, header=u'h2', plus=u'+', minus=u'-'):
    request = macro.request
    idx = request.uid_generator(section_base)
    html = u''
    if idx == section_base:
        #this is the first call to this macro, include the main JS code
        html = section_js % (minus, plus)

    if header is None:
        header = u'h2'

    title = u"%s %s" % (minus, title)
    page_html = Include.execute(macro, page)
    html += section_template % (header, idx, idx, title, header, idx, page_html)
    if not visible:
        hide_html = section_hide_template % idx
        html += hide_html
    return macro.formatter.rawHTML(html)

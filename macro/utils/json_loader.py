
import json

from MoinMoin.Page import Page
from MoinMoin import wikiutil

def load_json_text_from_page(request, page_name, parser_name):
    formatterClass = wikiutil.searchAndImportPlugin(
        request.cfg, 'formatter', 'extracting_formatter')
    extracting_formatter = formatterClass(parser_name, request)
    page = Page(request, page_name, formatter=extracting_formatter)
    extracting_formatter.setPage(page)
    
    # Discarding the return value
    request.redirectedOutput(
        Page.send_page_content, page, request, page.data, 'wiki')

    return extracting_formatter.get_extracted()

def load_json_from_page(request, page_name, parser_name):
    json_text = load_json_text_from_page(request, page_name, parser_name)
    if not json_text:
        return None
    else:
        return json.loads(json_text)

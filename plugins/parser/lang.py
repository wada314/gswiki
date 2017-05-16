# -*- encoding: utf-8 -*-

from text_moin_wiki import Parser as ParserBase

class Parser(ParserBase):
    Dependencies = []

    def __init__(self, raw, request, filename=None, format_args=u'', **kw):
        text_lang = format_args.strip() or self.cfg.language_default
        user_lang = request.user.language
        quality = 0.0
        if not user_lang:
            for lang_quality in request.accept_languages:
                # select the first item of the accept-languages HTTP header.
                user_lang = lang_quality[0].partition(u'-')[0]
                break

        if user_lang == text_lang:
            ParserBase.__init__(self, raw, request, **kw)
        else:
            # Different language, show nothing
            ParserBase.__init__(self, u'', request, **kw)

        

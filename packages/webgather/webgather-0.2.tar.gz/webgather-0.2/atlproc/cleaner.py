# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2016-10-17 17:27:17
# @Last Modified by:   mithril
# @Last Modified time: 2016-10-18 08:48:34

from lxml import html
from lxml.html.clean import Cleaner

cleaner = Cleaner(allow_tags=['p', 'div', 'br', 'b', 'strong', 'small'],
                  remove_unknown_tags=False, safe_attrs_only=True, safe_attrs=frozenset())


def clean_html(text, plain=False):
    if plain:
        h = html.fromstring(text)
        text = h.text_content()
    else :
        text = cleaner.clean_html(text)
    return text
# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2016-06-08 16:01:27
# @Last Modified by:   mithril
# @Last Modified time: 2016-10-18 09:01:19


from lxml.html.clean import Cleaner
from lxml import html
from readability.readability import Document
from .models import MyArticle



# allow_tags=['p','div','br','b', 'strong', 'small']

cleaner = Cleaner(allow_tags=['p', 'div', 'br', 'b', 'strong', 'small'],
                  remove_unknown_tags=False, safe_attrs_only=True, safe_attrs=frozenset())


def parse(content, url=None, plain=False):

    doc = Document(content, url=url, min_text_length=18)

    title = doc.short_title()
    content = doc.summary(True)

    if plain:
        h = html.fromstring(content)
        text = h.text_content()
    else:
        text = cleaner.clean_html(content)

    return MyArticle(
        title=title,
        text=text
    )
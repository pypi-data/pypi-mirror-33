# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2016-07-06 09:40:03
# @Last Modified by:   mithril
# @Last Modified time: 2016-07-06 09:50:22

from lxml.html.clean import Cleaner
from lxml import html
import re
from readability.readability import Document

# allow_tags=['p','div','br','b', 'strong', 'small']

cleaner = Cleaner(allow_tags=['p', 'div', 'br', 'b', 'strong', 'small'],
                  remove_unknown_tags=False, safe_attrs_only=True, safe_attrs=frozenset())


def clean_text(text):
    s = re.sub(u'\s', '', text).replace(u'\xa0', '').replace(u'\u3000', '')
    return s


def get_best_candidate(doc):
    candidates = doc.score_paragraphs()
    best_candidate = doc.select_best_candidate(candidates)
    return best_candidate['elem'].text_content() if best_candidate else ''


def cal_word(html_str):
    h = html.fromstring(html_str)
    return len(clean_text(h.text_content()))


def parse(content, url=None, plain=False):

    doc = Document(content, url=url, min_text_length=18)

    title = doc.short_title()
    c0 = doc.content()
    c1 = get_best_candidate(doc)
    c2 = doc.summary(True)

    c0_c = cal_word(c0)
    c1_c = cal_word(c1)
    c2_c = cal_word(c2)

    # c0_c > c1_c > c2_c

    if c1_c < 100:
        content = c0
    elif c2_c < c1_c * 0.3:
        content = c1
    else:
        content = c2

    if plain:
        h = html.fromstring(content)
        text = h.text_content()
    else:
        text = cleaner.clean_html(content)

    return {
        'title': title,
        'text': text
    }


if __name__ == '__main__':
    import requests
    url = 'http://ecp.sgcc.com.cn/html/project/014002007/9990000000010135023.html'
    r = requests.get(url)
    a = parse(r.content, url, plain=True)

    print a['text']

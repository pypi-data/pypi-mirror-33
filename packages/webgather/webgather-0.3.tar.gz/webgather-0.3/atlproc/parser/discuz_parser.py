#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2015-12-11 10:10:23
# @Last Modified by:   mithril
# @Last Modified time: 2015-12-11 14:48:40

from lxml import html
from pyquery import PyQuery as pq
from .models import MyArticle


def parse(content):

    h = html.fromstring(content)
    doc = pq(h)

    title = doc('#thread_subject').text()

    text = doc('.t_f:first').text()

    try:
        authors = h.cssselect('.pls.favatar .xw1')[0].text_content()
    except:
        authors = ''

    try:
        publish_date = doc('em:contains("发表于")')[0].text_content().replace('发表于 ', '')
    except:
        publish_date = None


    return MyArticle(
        title=title,
        text=text,
        authors=authors,
        publish_date=publish_date
    )

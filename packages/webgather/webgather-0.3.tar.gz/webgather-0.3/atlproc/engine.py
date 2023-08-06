#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2015-09-24 10:10:08
# @Last Modified by:   mithril
# @Last Modified time: 2016-07-29 11:14:50

import time
from .detector import discuz_detector
# from .filter import discuz_filter
from .parser import discuz_parser, readability_parser

def parse_article(content, url=None, plain=False):
    if discuz_detector.detect(content):
        article = discuz_parser.parse(content)
    else:
        article = readability_parser.parse(content, url, plain)

    return article

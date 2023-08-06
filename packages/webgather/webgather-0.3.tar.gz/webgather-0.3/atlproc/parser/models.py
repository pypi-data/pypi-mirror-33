#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2015-12-11 11:14:48
# @Last Modified by:   mithril
# @Last Modified time: 2016-07-06 09:49:57


class MyArticle(object):

    def __init__(self, title='', text='', authors='', publish_time=None, publish_date=None, full_text='', childurl_count=0, image_count=0, is_custom=False, error_code=None, error_msg=None):
        self.title = title
        self.text = text
        self.authors = authors
        # must be datetime object
        self.publish_time = publish_time
        self.publish_date = publish_date
        self.full_text = full_text
        self.childurl_count = childurl_count
        self.image_count = image_count
        self.is_custom = is_custom
        self.error_code = error_code
        self.error_msg = error_msg

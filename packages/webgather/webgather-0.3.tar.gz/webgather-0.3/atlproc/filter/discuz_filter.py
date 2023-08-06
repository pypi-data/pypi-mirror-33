#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: mithril
# @Date:   2015-12-11 10:09:46
# @Last Modified by:   mithril
# @Last Modified time: 2016-08-04 17:06:52


extentions =['.png', '.jpg', '.jpeg', '.gif', '.xml', '.pdf', '.rar', '.zip', '.doc', '.docx']
keywords = ['profile', 'login', 'user', 'username', 'uid', 'userid', 'info', 'search', 'download', 'act=reg', 'mod=space','mod=redirect', 'register']

keywords.extend(extentions)

def is_useless(url):
    if any(url.find(kw) > -1 for kw in keywords):
        return True
    return False
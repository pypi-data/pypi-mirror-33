# -*- coding: utf-8 -*-

class PageListChecker(object):
    def __init__(self):
        pass

    # def clean_url(self):
    #     keywords = ['about']
    #     for item in self.urllst:
    #         if item['']

    def check_result(self, url):
        res, msg = self.__check_lst_count(url)
        return res,msg

    def __check_lst_count(self, urllst):
        if len(urllst) >= 10:
            return True, ''
        else:
            return False, "urllst < 10"

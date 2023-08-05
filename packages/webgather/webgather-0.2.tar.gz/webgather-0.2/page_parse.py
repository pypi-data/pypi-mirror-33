# -*- coding: utf-8 -*-
from gather.webgather_div import webgather_div
from gather.webgather_json_pick import webgather_json_picker
from gather.webgather_pick import webgather_picker
from gather.webgather_table import webgather_table
from page_list_url_checker import PageListChecker


class PageParse(object):
    def __init__(self):
        self.strcss = ''
        self.strjson = ''
        self.url = ''
        self.dict = {
            'css': self.__css,
            'json': self.__json,
            'detail_page': self.first_detail_page,
            'detailpage': self.first_detail_page,
            'selecter': self.func_selecter,
            'merge': self.merge
        }
        self.strdetail_page_format = ''

    def get_page_list_by_div(self, html):
        engine = webgather_div
        return self.__get_page_list_by_engine(html, engine)

    def get_page_list_by_table(self, html):
        engine = webgather_table
        return self.__get_page_list_by_engine(html, engine)

    def get_page_list(self, html, dic):
        """
        获取页面列表
        :param html:
        :param dic:
        :return:
        """
        self.parse_dict(dic)
        return self.__get_page_list(html)

    def parse_dict(self, dic):
        """
        'selecter': {
            'type': 'selecter',
            'struct': 'selecterValue'
        },
        'detailpage': {
            'detailpage': 'firstPageDetailPage',
            'param': 'firstRecordUrl',
        }
        }
        :param dic:
        :return:
        """
        for key, value in dic.items():
            if self.dict.has_key(key):
                self.dict[key](value)
        # if self.url == '':
        #     self.url = dic['url']

    # def clean_url(self):
    #     keywords = ['about']
    #     for item in self.urllst:
    #         if item['']

    def func_selecter(self, content):
        """
        {
            "type":"css/json",
            "struct":"body > div"
        }
        :param content:
        :return:
        """
        if not content:
            return
        if content['type'] == 'css':
            self.strcss = content['struct']
        elif content['type'] == 'json':
            self.strjson = content['struct']

    def first_detail_page(self, content):
        # if content['detailpage'] == '':
        #     return
        # content = content.strip('"')
        # detail_page, first_param = content.split("_$_", 1)

        if content['detailpage'] == '':
            return
        self.strdetail_page_format = content['detailpage'].replace(content['param'], '%s')
        return self.strdetail_page_format

        # self.strdetail_page_format = detail_page.replace(first_param, '%s')
        # print detail_page
        # print self.strdetail_page_format

    def merge(self, content):
        self.strmerge = content

    def parse(self, url):
        parts = url.split('$$$')
        for part in parts[1:]:
            key, value = part.split(':', 1)
            self.dict[key](value)
        return parts[0]

    def __css(self, content):
        if not content:
            return
        self.strcss = content

    def __json(self, content):
        if not content:
            return
        self.strjson = content

    def __get_page_list_by_engine(self, html, engine):
        """
        用tablecommon获取页面
        :param html:
        :return:
        """
        driver = engine(html)
        lst = driver.picker_content()
        res, msg = PageListChecker().check_result(lst)
        if res:
            return driver, lst, res, msg
        return None, [], False, 'false'

    def __get_page_list(self, html):
        """
        获取页面列表
        :param html:
        :return:
        """
        engines = [webgather_table, webgather_div]
        if self.strcss:
            engine = webgather_picker(html)
            lst = engine.picker_content(css=self.strcss, detailpageformat=self.strdetail_page_format)
            res, msg = PageListChecker().check_result(lst)
            return engine, lst, res, msg
        elif self.strjson:
            engine = webgather_json_picker(html)
            lst = engine.picker_content(json=self.strjson, detailpageformat=self.strdetail_page_format)
            res, msg = PageListChecker().check_result(lst)
            return engine, lst, res, msg
        else:
            for engine in engines:
                # driver = webgather_table(html)
                driver = engine(html)
                lst = driver.picker_content()
                res, msg = PageListChecker().check_result(lst)
                if res:
                    return driver, lst, res, msg
            return None, [], False, 'false'

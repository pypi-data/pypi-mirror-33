# -*- coding: utf-8 -*-
import unittest
from unittest import TestCase

from fetcher_manager import FetcherManager
from page_parse import PageParse


class TestFetcherManager(TestCase):

    def setUp(self):
        pass
        # self.base_url = 'http://139.196.106.157:5001/api/v1'
        # self.base_url = 'http://s01.basin.ali:5001/api/v1'
        # self.base_url = 'http://nd2.csp.ali:5001/api/v1'
        # self.base_url = 'http://10.211.55.2:5001/api/v1'

        # self.base_url = 'http://127.0.0.1:5001/api/v1'
        # self.base_url = 'http://10.142.54.150:5001/api/v1'
        # self.headers = {'content-type': 'application/json'}

    def tearDown(self):
        pass

    def test_url(self):
        """
        测试url
        :return:
        """
        url = 'http://www.bidding.csg.cn/zbgg/index.jhtml'
        html = FetcherManager().fetch_url(url)
        pageParse = PageParse()
        engine, lst, res, msg = pageParse.get_page_list(html, {})
        # for item in lst:
        #     print item
        print len(lst)
        self.assertGreater(len(lst), 1, u'获取列标数<1')

    def test_url_css(self):
        """
        测试 url,css
        :return:
        """
        dic = {
            'selecter': {
                'type': 'css',
                'struct': 'body > div.W1000.Center.Top8.AbsMiddle > div.W750.Right > div.BorderEEE.NoBorderTop.List1.Black14.Padding5'
            }
        }
        url = 'http://www.bidding.csg.cn/zbgg/index.jhtml'
        html = FetcherManager().fetch_url(url)
        pageParse = PageParse()
        engine, lst, res, msg = pageParse.get_page_list(html, dic)
        print len(lst)
        self.assertGreater(len(lst), 1, u'获取列标数<1')

    # def test_curl_json(self):
    #     """
    #     测试 url,json
    #     :return:
    #     """


    def test_curl_json(self):
        """
        测试curl
        :return:
        """
        curl = "curl 'http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do' -H 'Cookie: JSESSIONID=B4hHbr2TYcMCmwq85YQYZ5sQqd2pwxyBnynhxWq7sSvd7Mz25chH!-1154159727' -H 'Origin: http://www.ccgp-hunan.gov.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.9' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.ccgp-hunan.gov.cn/page/notice/more.jsp' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'pType=&prcmPrjName=&prcmItemCode=&prcmOrgName=&startDate=2018-05-21&endDate=2018-06-21&prcmPlanNo=&page=1&pageSize=18' --compressed"
        dic = {
            'selecter': {
                'type': 'json',
                'struct': 'rows>ORG_NAME'
            },
            'detailpage': {
                'detailpage': 'firstPageDetailPage',
                'param': 'firstRecordUrl',
            }
        }
        html = FetcherManager().fetch_curl(curl)
        pageParse = PageParse()
        engine, lst, res, msg = pageParse.get_page_list(html, dic)
        self.assertGreater(len(lst), 1, '获取列标数>0')
        for item in lst:
            print item


if __name__ == '__main__':
    unittest.main()

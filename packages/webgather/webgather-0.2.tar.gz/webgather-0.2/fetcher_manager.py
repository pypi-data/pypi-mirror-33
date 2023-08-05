# -*- coding: utf-8 -*-
import re

import requests
from utils import uncurl

from utils.response import rebuild_response

proxy = '10.211.55.3:8888'

# g_proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
g_proxies = {}


class FetcherManager(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        self.data = None
        self.strcss = ''
        self.method = 'get'
        self.strjson = ''
        self.strmerge = ''
        # self.first_detail_page = ''
        self.cookie_dict = {}
        self.strdetail_page_format = ''
        self.url = ''

        self.dict = {
            # 'curl': self.curl,
            # 'ajax': self.curl,

        }



    # def css(self, content):
    #     if not content:
    #         return
    #     self.strcss = content
    #
    # def json(self, content):
    #     if not content:
    #         return
    #     self.strjson = content

    # def curl(self, content):
    #     if not content:
    #         return
    #     pattent = r"( -H | --data | --data-binary )'(.*?)'"
    #     for item in re.findall(pattent, content['curl']):
    #         # print item[0]
    #         if item[0] == ' -H ':
    #             key, value = item[1].split(":", 1)
    #             self.headers.update({key: value.strip()})
    #         if item[0] == ' --data ' or item[0] == ' --data-binary ':
    #             self.data = item[1]
    #     if content.has_key('curl') and len(content['curl']) > 0:
    #         self.url = content['curl'].split(" ")[1].strip("'")

    def fetch_url(self, url):
        """
        爬取普通网页
        :param url:
        :return:
        """
        Response = self.__fetch_url(url)
        return Response.doc.html()

    def fetch_curl(self, curl_command):
        """
        爬取curl 命令格式 从 Chrome复制
        :param curl_command: curl 'https://ss0.bdstatic.com/k4oZeXSm1A5BphGlnYG/newmusic/suibiantingting.png' -H 'Referer: https://www.baidu.com/' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36' --compressed
        :return:
        """
        # return parsed_args.url, method, data_token, quoted_headers, cookie_dict

        self.url, self.method, self.data, self.headers, self.cookie_dict = uncurl.parse(curl_command)
        Response = self.__fetch_url(self.url)
        return Response.doc.html()

    def __fetch_url(self, url):
        if self.data:
            r = requests.post(url, headers=self.headers, data=self.data, proxies=g_proxies, verify=False, timeout=20)
        else:
            r = requests.get(url, headers=self.headers, proxies=g_proxies, verify=False, timeout=20)
        return rebuild_response(r)

    def parse_dict(self, dic):
        """
        {
        'url': 'http://www.baidu.com', 'name': 'name', 'ajax': {
            'curl': 'ajaxUrl',
            'method': 'get',
        },
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
        if self.url == '':
            self.url = dic['url']

    def simulate_url_prams(self, dic):
        self.parse_dict(dic)
        html = self.fetch_url(self.url)
        # engines = [webgather_table,webgather_div]
        # engine = None
        # lst = []
        return self.get_page_list(html)


if __name__ == '__main__':
    dic = {
        'url': 'http://www.bidding.csg.cn/zbgg/index.jhtml', 'name': 'name', 'ajax': {
            'curl': '',
            'method': 'get',
        },
        'selecter': {
            'type': 'selecter',
            'struct': 'selecterValue'
        },
        'detailpage': {
            'detailpage': 'firstPageDetailPage',
            'param': 'firstRecordUrl',
        }
    }

    # FetcherManager().simulate_url_prams(dic)
    # html = FetcherManager().fetch_curl(
    #     "curl 'https://ss0.bdstatic.com/k4oZeXSm1A5BphGlnYG/newmusic/lovesong.png' -H 'Referer: https://www.baidu.com/' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36' --compressed")
    html = FetcherManager().fetch_url('http://www.bidding.csg.cn/zbgg/index.jhtml')
    engine, lst, msg = FetcherManager().get_page_list(html)

    # engine, lst, msg = FetcherManager().simulate_url_prams(dic)
    # for item in lst:
    #     print item['title']
    # print msg
    # webgather_table("xx")

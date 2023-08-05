# -*- coding: utf-8 -*-
import codecs

import sys

from fetcher_manager import FetcherManager
from page_parse import PageParse

if __name__ == '__main__':
    # url = 'http://www.bidding.csg.cn/zbgg/index.jhtml'
    curl="curl 'http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do' -H 'Cookie: JSESSIONID=B4hHbr2TYcMCmwq85YQYZ5sQqd2pwxyBnynhxWq7sSvd7Mz25chH!-1154159727' -H 'Origin: http://www.ccgp-hunan.gov.cn' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: zh-CN,zh;q=0.9' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Accept: application/json, text/javascript, */*; q=0.01' -H 'Referer: http://www.ccgp-hunan.gov.cn/page/notice/more.jsp' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' --data 'pType=&prcmPrjName=&prcmItemCode=&prcmOrgName=&startDate=2018-05-21&endDate=2018-06-21&prcmPlanNo=&page=1&pageSize=18' --compressed"
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
    # html = FetcherManager().fetch_url(url)
    html = FetcherManager().fetch_curl(curl)
    # print html
    # sys.exit(1)
    # codecs.open('/tmp/1.txt','wb','utf-8').write(html)
    # html = codecs.open('/tmp/1.txt', 'rb', 'utf-8').read()
    # print 'ok'
    # sys.exit()
    pageParse = PageParse()
    engine, lst, res,msg = pageParse.get_page_list(html, dic)
    # engine, lst, msg = PageParse().get_page_list(html)
    for item in lst:
        print item

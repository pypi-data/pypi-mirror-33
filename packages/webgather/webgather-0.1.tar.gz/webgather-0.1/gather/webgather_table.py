#!/usr/bin/env python

import re
import sys
import urllib
from bs4 import BeautifulSoup

from webgather_base import webgather_base


class Item:
    def __init__(self, title, href, onclick, line_html):
        self.title = title
        self.href = href
        self.onclick = onclick
        self.line_html = line_html
        self.url = ""

    def Show(self):
        print "title: %s" % (self.title)
        print "href: %s" % (self.href)
        print "onclick: %s" % (self.onclick)
        print "url: %s" % (self.url)

    def toJson(self):
        return {'title': self.title,
                'url': self.href}

    def toStr(self):
        return '-=- %d -=- \n' \
               'title: %s \n' \
               'url: %s \n' % (self.index, self.title, self.href)


class webgather_table(webgather_base):
    def __init__(self, html):
        super(webgather_table, self).__init__(html)
        self.name = 'tablecommon'

    def generate_url(self, main_page_url, href, onclick):
        if main_page_url:
            proto, rest = urllib.splittype(main_page_url)
            host, _ = urllib.splithost(rest)
            domain_url = proto + "://" + host
            url_prefix = main_page_url[0:main_page_url.rfind('/')]
        else:
            url_prefix = ''
            domain_url = ''

        url = ''
        if len(href) > 0:
            if href[0] == '/':
                url = domain_url + href
            elif len(href) > 2 and href[0:2] == "./":
                url = url_prefix + href[1:len(href)]
            elif len(href) > 10 and href[0:10] == "javascript":
                regexp = re.compile(".*\(\'(\d+)\',\'(\d+)\'\)")
                result = re.findall(regexp, onclick)
                if len(result) > 0:
                    a1 = result[0][0]
                    a2 = result[0][1]
                    url = domain_url + "/html/project/" + a1 + "/" + a2 + ".html"
            else:
                url = url_prefix + "/" + href
        return url

    def get_likely_td(self, tr):
        likely_td = None
        max_len = 0
        for _, td in enumerate(tr.children):
            if td.name == 'td':
                text_len = len(str(td))
                if text_len > max_len:
                    likely_td = td
                    max_len = text_len
        return likely_td

    def get_title_from_string(self, str):
        regexp = re.compile("title=\"(.*?)\"")
        result = re.findall(regexp, str)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def get_title_from_anchor(self, str):
        title = self.get_title_from_string(str)
        if title is None:
            regexp = re.compile("<a (.*?)>(.*?)</a>")
            result = re.findall(regexp, str)
            if len(result) > 0:
                title = result[0][1]
        return title

    def get_href_from_string(self, str):
        regexp = re.compile("href=\"(.*?)\"")
        result = re.findall(regexp, str)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def get_onclick_from_string(self, str):
        regexp = re.compile(r'javascript.*\(.*?\)?"')
        result = re.findall(regexp, str)
        if len(result) > 0:
            return result[0]
        else:
            return ''

    def get_index_pag_main_list(self, html):

        blocks = []

        max_chars = 0
        suggest_index = -1

        block_index = 0
        soup = BeautifulSoup(html, "lxml")

        for ul in soup.select('ul'):
            items = []
            for _, li in enumerate(ul.children):
                # print str(li)[0:80]
                if li.name == 'li':
                    line_html = str(li)
                    # print line_html[0:80]

                    title, href, onclick = self.get_metadatas_from_line(line_html)
                    if not title is None:
                        items.append(Item(title, href, onclick, line_html))
                        # print title

            blocks.append(items)

            block_chars = sum([len(item.line_html) for item in items])
            print "ul[%d] %d items %d chars" % (block_index, len(items), block_chars)

            if block_chars > max_chars:
                suggest_index = block_index
                max_chars = block_chars
            block_index += 1

        return suggest_index, blocks

    def get_index_pag_main_table(self, html):

        blocks = []

        max_chars = 0
        suggest_index = -1

        block_index = 0
        soup = BeautifulSoup(html, "lxml")

        for table in soup.select('table'):
            items = []
            # for _, tr in enumerate(table.tbody.children):
            for _, tr in enumerate(table.contents):
                if tr.name == 'tr':
                    likely_td = self.get_likely_td(tr)
                    if not likely_td is None:
                        line_html = str(tr)
                        title, href, onclick = self.get_metadatas_from_line(line_html)
                        if not title is None:
                            items.append(Item(title, href, onclick, line_html))

            blocks.append(items)

            block_chars = sum([len(item.line_html) for item in items])
            print "tr[%d] %d items %d chars" % (block_index, len(items), block_chars)

            if block_chars > max_chars:
                suggest_index = block_index
                max_chars = block_chars
            block_index += 1

        return suggest_index, blocks

    def get_metadatas_from_line(self, line_html):
        title = self.get_title_from_anchor(line_html)
        href = ""
        onclick = ""
        if not title is None:
            # print("-------- title --------")
            # print(title)
            href = self.get_href_from_string(line_html)
            onclick = self.get_onclick_from_string(line_html)
        return title, href, onclick

    def get_max_chars_in_blocks(self, blocks):
        if len(blocks) > 0:
            return max([sum(len(item.line_html) for item in b) for b in blocks])
        else:
            return 0

    def get_max_items_in_blocks(self, blocks):
        if len(blocks) > 0:
            return max([len(b) for b in blocks])
        else:
            return 0

    def picker_content(self):
        # elements = self.etree(html)
        # doc = pq(elements)
        # doc.make_links_absolute(url)
        # html = doc.html()
        # fileid = self.savehtml(url, html)
        _, _, urlitems = self.get_index_page_main_block(self.html, self.url)
        urls = []
        for item in urlitems:
            urls.append(item.toJson())
        print urls
        return urls

    def get_index_page_main_block(self, html, url):
        list_suggest_index, list_blocks = self.get_index_pag_main_list(html)
        table_suggest_index, table_blocks = self.get_index_pag_main_table(html)

        list_max_chars = self.get_max_chars_in_blocks(list_blocks)
        list_max_items = self.get_max_items_in_blocks(list_blocks)
        table_max_chars = self.get_max_chars_in_blocks(table_blocks)
        table_max_items = self.get_max_items_in_blocks(table_blocks)

        print "list: suggest %d %d blocks max_items: %d max_chars: %d" % (
        list_suggest_index, len(list_blocks), list_max_items, list_max_chars)
        print "table: suggest %d %d blocks max_items: %d max_chars: %d" % (
        table_suggest_index, len(table_blocks), table_max_items, table_max_chars)

        suggest_block_type = "list"
        suggest_index = list_suggest_index
        blocks = list_blocks

        if table_max_chars > list_max_chars:
            suggest_block_type = "table"
            suggest_index = table_suggest_index
            blocks = table_blocks

        max_block_items = self.get_max_items_in_blocks(blocks)
        max_block_chars = self.get_max_chars_in_blocks(blocks)
        print
        print "==================="
        print "suggest: <%s> index %d  %d blocks max_items: %d max_chars: %d" % \
              (suggest_block_type, suggest_index, len(blocks), max_block_items, max_block_chars)
        urlitems = []
        if suggest_index >= 0:
            print("suggest_index:", suggest_index, len(blocks[suggest_index]))
            i = 0
            for item in blocks[suggest_index]:
                detail_url = self.generate_url(url, item.href, item.onclick)
                item.url = detail_url
                urlitems.append(item)
                # print "-=- %d -=-" % (i)
                # item.Show()
                # print("....................")
                # print
                # #print(line_html)
                # print("--------------------")
                i += 1

        return suggest_index, blocks, urlitems

    # def simulate_click_detail_page(self,driver):
    #     #p = "//a[@onclick=\"showProjectDetail('014002007','9900000000000055739');return false;\"]"
    #     p = "//a[@onclick=\"showProjectDetail('014002007','9900000000000055739');\"]"
    #     p1 = "//a[@onclick]"
    #
    #     anchor_detail = None
    #     try:
    #         anchor_detail = driver.find_element_by_xpath(p)
    #     except NoSuchElementException as msg:
    #         print "NoSuchElementException!\n%s" % (msg)
    #
    #     if not anchor_detail is None:
    #         title = anchor_detail.get_attribute("title")
    #         href = anchor_detail.get_attribute("href")
    #         onclick = anchor_detail.get_attribute("onclick")
    #         style = anchor_detail.get_attribute("style")
    #         text = anchor_detail.text
    #         print "title: %s" % (title)
    #         print "href: %s" % (href)
    #         print "onclick: %s" % (onclick)
    #         print "style: %s" % (style)
    #         print "text: %s" % (text)
    #
    #         p1 = "//a[@onclick=\\\"%s\\\"]" % (onclick)
    #         print p1
    #
    #         #script = "var clickEvent=document.createEvent('HTMLEvents'); clickEvent.initEvent('click',false,true); var eva=new XPathEvaluator(); var result=eva.evaluate(\"%s\",document.documentElement,null,XPathResult.ORDERED_NODE_TYPE,null); result.singleNodeValue.dispatchEvent(clickEvent);" % ("//a") #(p)
    #
    #         # single node
    #         #script = "var clickEvent=document.createEvent('HTMLEvents'); clickEvent.initEvent('click',false,true); var result = document.evaluate(\"%s\",document.documentElement,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null); result.singleNodeValue.dispatchEvent(clickEvent);" % (p1)
    #         script = "var clickEvent=document.createEvent('HTMLEvents'); clickEvent.initEvent('click',false,true); var result = document.evaluate(\"%s\",document.documentElement,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null); result.singleNodeValue.dispatchEvent(clickEvent);" % (p1)
    #
    #         # multi nodes
    #         #script = "var clickEvent=document.createEvent('HTMLEvents'); clickEvent.initEvent('click',false,true); var result = document.evaluate(\"%s\",document.documentElement,null,XPathResult.ORDERED_NODE_ITERATOR_TYPE,null); var node = result.iterateNext(); while(node){ node.dispatchEvent(clickEvent); node = node.iterateNext();}" % (p1)
    #
    #         #print script
    #         #driver.execute_script(script)
    #
    #         #run_script = onclick
    #         run_script = "var url = '/html/project/014002007/9900000000000055739.html'; window.open(url , '_blank');"
    #         print("run_script:", run_script)
    #         driver.execute_script(run_script)
    #
    #         #anchor_detail.click()
    #         driver.refresh()
    #         print "detail page url: %s" % (driver.current_url)


def main():
    # <ul>
    # url = 'http://www.ccgp.gov.cn/cggg/zygg/index.htm'
    # url = "http://www.bidding.csg.cn/zbgg/index.jhtml"
    # <table> onclick
    # url = "http://ecp.sgcc.com.cn/topic_project_list.jsp?columnName=topic10"
    # url = 'https://www.ft.com/companies/energy'
    url = 'http://www.bidding.csg.cn/zbgg/index.jhtml'
    if len(sys.argv) > 1:
        url = sys.argv[1]

    # service_args = []
    # service_args.append('--load-images=no')
    # service_args.append('--disk-cache=yes')
    # service_args.append('--ignore-ssl-error=true')
    # driver = webdriver.PhantomJS("phantomjs", service_args=service_args)
    # driver = webdriver.PhantomJS()
    # driver.get(url)
    # html = driver.page_source
    webgather = webgather_table()

    # fetch(url)
    for item in webgather.fetch_to_lst(url):
        print item
    print "Get html done."

    # simulate_click_detail_page(driver)

    # get_index_page_main_block(html, url)


if __name__ == '__main__':
    main()

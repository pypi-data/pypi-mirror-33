#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import time
from datetime import datetime

import dateutil
import requests
from atlproc import parse_article
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq

from webgather_base import webgather_base


class Item:

    def __init__(self):
        self.index = 0
        self.title = ''
        self.href = ''
        self.onclick = None
        self.line_html = ''
        # self.url = ''

    def Show(self):
        print '-=- %d -=-' % self.index
        print "title: %s" % (self.title)
        print "url: %s" % (self.href)

    def toJson(self):
        return {'title': self.title,
                'url': self.href}
    def toStr(self):
        return '-=- %d -=- \n' \
               'title: %s \n' \
               'url: %s \n' % (self.index, self.title, self.href)


class webgather_div(webgather_base):
    def __init__(self, html):
        super(webgather_div, self).__init__(html)
        self.name = 'divcommon'

    def get_title_from_string(self,str):
        regexp = re.compile("title=\"(.*?)\"")
        result = re.findall(regexp, str)
        if len(result) > 0:
            return result[0]
        else:
            return None


    index = -1


    def check_against_word_less(self,a_tag):
        try:
            if a_tag.attrs.has_key('title') and a_tag.text:
                title = a_tag.attrs['title'] if len(''.join(a_tag.attrs['title'].strip()).split(' ')) > len(
                    ''.join(a_tag.text.strip()).split(' ')) else a_tag.text
                return True if len(title) > 5 else False
            elif a_tag.text:
                if isinstance(a_tag.text, unicode):
                    return True if len(a_tag.text) > 15 else False
                else:
                    return True if len(''.join(a_tag.text.strip()).split(' ')) > 5 else False
            else:
                return False

            # if a_tag.attrs.has_key('title'):
            #     return True if len(''.join(a_tag.attrs['title'].strip()).split(' ')) > 5 else False
            # elif a_tag.text:
            #     return True if len(''.join(a_tag.text.strip()).split(' ')) > 5 else False
            # else:
            #     return False

        except Exception, e:
            print e.message
            print a_tag
            print a_tag.string

            return False


    def check_has_href(self,a_tag):
        return a_tag.attrs.has_key('href')


    def check_against(self,a_tag):
        res = self.check_has_href(a_tag)
        if not res: return False
        res = self.check_against_word_less(a_tag)
        if not res: return False

        return True


    def get_index_page_main_div_to_lst(self,html):
        lst = self.get_index_pag_main_div(html)
        urls = []
        for item in lst:
            urls.append(item.toJson())
        print urls
        return urls

        # schema = WebgatherSchemas()
        # print schema.deserialize(urls)
        # return lst


    def get_index_page_main_div_to_str(self,html):
        lst = self.get_index_pag_main_div(html)
        str = ''
        for item in lst:
            # item.Show()
            str += item.toStr()
        return str


    def get_index_pag_main_div(self,html):
        soup = BeautifulSoup(html, 'lxml')

        # source_filter = Commom.filter(soup)
        # source_filter = Header.filter(source_filter)
        # source_filter = Footer.filter(source_filter)
        source_filter = soup

        block_index = 0
        blocks = []
        max_acount = 0
        suggestindex = 0
        divs = source_filter.find_all('div')
        hits = ['news', 'container', 'group', 'content', 'webRssFeed', 'noticias', 'blog-featured', 'feature-wrap',
                'comm_bx', 'bloc1', 'section','sec_neirong']
        for index, div in enumerate(divs):
            if div.attrs.has_key('class'):
                div_class = '_'.join(div.attrs['class'])
                for hit in hits:
                    block_index += 1
                    blocks.append(div)
                    if div_class.lower().find(hit) != -1:
                        divlst = div.find_all('a')
                        # print 'acount %d' % len(divlst)
                        # for item in divlst:
                        #     print item
                        if max_acount < len(divlst):
                            max_acount = len(divlst)
                            suggestindex = block_index

        #     divlst = blocks[suggestindex].find_all('a')
        # print '=========================='
        if divs:
            urlitems = []
            if suggestindex>0:
                divlst = blocks[suggestindex].find_all('a')
                for i, a_tag in enumerate(divlst):
                    res = self.check_against(a_tag)
                    if res:
                        item = Item()
                        item.index = i
                        item.href = a_tag.attrs['href']
                        if a_tag.attrs.has_key('title'):
                            item.title = a_tag.text.strip() if len(a_tag.attrs['title']) < len(a_tag.text) else a_tag.attrs[
                                'title'].strip()
                        else:
                            item.title = a_tag.text.strip()
                        urlitems.append(item)

                return urlitems
        return []


    def get_index_page_main_block_to_lst(self,html, url):
        return self.get_index_page_main_div_to_lst(html)


    def get_index_page_main_block_to_str(self,html, url):
        return self.get_index_page_main_div_to_str(html)


    def fetch(self,url):
        r = requests.get(url)
        doc = pq(r.content)
        doc.make_links_absolute(url)
        html = doc.html()
        return self.get_index_page_main_block_to_str(html, url)

    def picker_content(self):

        # elements = self.etree(html)
        # doc = pq(elements)
        # doc.make_links_absolute(url)
        # html = doc.html()
        return self.get_index_page_main_block_to_lst(self.html, self.url)

    def fetch_to_lst(self, url, selecter):
        r = requests.get(url)
        doc = pq(r.content)
        doc.make_links_absolute(url)
        html = doc.html()
        return self.get_index_page_main_block_to_lst(html, url)


    def get_publish_date(self,r):

        publish_time = r.headers.get('Date', '')
        if isinstance(publish_time, int):
            pass
        elif isinstance(publish_time, datetime):
            publish_time = int(time.mktime(publish_time.timetuple()))
        else:
            try:
                publish_time = dateutil.parser.parse(publish_time)
                publish_time = int(time.mktime(publish_time.timetuple()))
            except:
                publish_time = 0

        return publish_time


    def fetch_content(self,url):
        r = requests.get(url)
        doc = pq(r.content)
        doc.make_links_absolute(url)
        html = doc.html()
        article = parse_article(html)
        return {
            'title': article.title,
            'publish_time': self.get_publish_date(r),
            'content': article.text,
            'html': r.content,
            'authors': article.authors
        }




def main():
    # <ul>
    # url = 'http://www.ccgp.gov.cn/cggg/zygg/index.htm'
    # url = "http://www.bidding.csg.cn/zbgg/index.jhtml"
    # <table> onclick
    # url = "http://ecp.sgcc.com.cn/topic_project_list.jsp?columnName=topic10"
    # url ='http://www.miit.gov.cn/n1146290/n1146402/n1146455/index.html'
    # url = 'http://fj.people.com.cn/GB/350390/350391/index.html'
    # url = 'http://localhost/2.html'
    # url = 'http://www.indaa.com.cn/dwjs/'
    # url= 'http://www.miit.gov.cn/n1146312/n1146904/n1648373/index.html'
    # url = 'https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Ausschreibungen/Ausschreibungen_node.html'
    # url = 'http://fjb.nea.gov.cn/news.aspx?id=89'
    # url = 'https://ec.europa.eu/energy/en'
    # url = 'http://tem.fi/en/current-issues'
    # url = 'http://www.bfe.admin.ch/energie/00588/00589/index.html?lang=fr'
    # url = 'http://www.bfe.admin.ch/energie/00588/00589/index.html?lang=fr'
    # url = 'http://www.nrcan.gc.ca/publications/1138#ey'
    # url = 'https://minenergo.gov.ru/press/min_news'
    # url = 'https://www.swissgrid.ch/swissgrid/en/home/current/media/media_releases.html'
    # url = 'http://www.energiavirasto.fi/en/web/energy-authority/news'

    # url = 'http://www.creg.be/fr/publications' # ok
    # url = 'http://www.energiavirasto.fi/en/web/energy-authority/news' # ok
    # url = 'http://www.sviluppoeconomico.gov.it/index.php/en/news' # ok
    # url = 'https://www.ecologique-solidaire.gouv.fr/presse?theme=%C3%89nergies' #ok
    # url = 'http://www.cre.fr/documents/presse' # ok

    # url = 'https://www.ofgem.gov.uk/news-blog/news-press-releases' # fail
    # url = 'http://www.mcit.gov.cy/mcit/mcit.nsf/mecit21_el/mecit21_el?OpenForm&Section=0' #fail
    # url ='http://www.mem.gov.ma/SitePages/DocTelecharger/CommuniquePresse2017.aspx#'
    # url = 'https://www.autorita.energia.it/it/inglese/annual_report/relaz_annuale.htm'
    # url = 'http://www.dgeg.gov.pt/'
    # url = 'http://www.minetad.gob.es/ES-ES/GABINETEPRENSA/NOTASPRENSA/Paginas/listadoNotasPrensa.aspx'
    # url ='https://www.elcom.admin.ch/elcom/fr/home/documentation/rapports-et-etudes.html'
    # url = 'http://www.bfe.admin.ch/energie/00588/00589/index.html?lang=fr'
    # url = 'http://www.energia.gob.cl/noticias'
    # url = 'http://ons.org.br/pt/paginas/imprensa/noticias'
    # url = 'http://www.enb.gov.hk/tc/whats_new.html'
    # url = 'https://www.doe.gov.ph/energist/'
    # url = 'https://www.psalm.gov.ph/newsroom/list/2017'
    # url = 'http://english.motie.go.kr/en/tp/energy/bbs/bbsList.do?bbs_cd_n=3&cate_n=3'
    # url = 'http://www.mcit.gov.cy/mcit/mcit.nsf/mecit21_el/mecit21_el?OpenForm&Section=0'
    # url = 'https://mewa.gov.sa/en/MediaCenter/News/Pages/home.aspx'
    # url = 'http://energy.gov.il/English/AboutTheOffice/NewsAndUpdates/Pages/default.aspx'
    # url = 'http://www.mem.gov.ma/SitePages/DocTelecharger/CommuniquePresse2017.aspx'
    # url = 'http://www.tunisieindustrie.gov.tn/actualites.html'
    # url = 'http://www.erc.go.ke/index.php?option=com_content&view=category&layout=blog&id=98&Itemid=579'
    # url = 'http://www.mireme.gov.mz/index.php?option=com_content&view=category&layout=blog&id=9&Itemid=101'
    # url = 'http://www.ypeka.gr/Default.aspx?tabid=367&language=en-US'
    # url = 'http://economie.fgov.be/en/modules/pressrelease/'
    # url = 'http://www.creg.be/fr/publications'
    # url = 'https://www.ofgem.gov.uk/news-blog/news-press-releases'

    # http://www.ypeka.gr/Default.aspx?tabid=367&language=en-US ./res/2018-01-25-16/1ac30d37fe6beddee2cdeb1955c2910c
    # url = 'https://www.ft.com/companies/energy'
    url = 'http://www.ypeka.gr/Default.aspx?tabid=367&language=en-US'
    if len(sys.argv) == 2:
        url = sys.argv[1]
    if len(sys.argv) == 3:
        url = sys.argv[1]
        savepath = sys.argv[2]
    webgather=webgather_div()
    webgather.fetch_to_lst(url)


if __name__ == '__main__':
    main()

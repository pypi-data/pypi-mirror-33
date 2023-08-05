#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from webgather_base import webgather_base, Item


class webgather_picker(webgather_base):
    def __init__(self, html):
        super(webgather_picker, self).__init__(html)
        self.name = 'pickercommon'

    def picker_content(self, **kwargs):
        doc = pq(self.html)
        urlitems = []
        selecter = kwargs.get('css', kwargs.get('json', None))
        if not selecter:
            return [], self.html
        for item in doc(selecter).items():
            # print item
            for index, each in enumerate(item('a[href^="http"]').items()):
                item = Item()
                item.index = index
                item.href = each.attr('href')
                item.title = each.text()
                urlitems.append(item.toJson())
        return urlitems


def main():
    pass
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
    # url = 'http://www.bidding.csg.cn/zbgg/index.jhtml'
    # if len(sys.argv) == 2:
    #     url = sys.argv[1]
    # if len(sys.argv) == 3:
    #     url = sys.argv[1]
    #     savepath = sys.argv[2]
    # webgather = webgather_picker()
    # webgather.fetch_to_lst(url)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


from webgather_base import Item, webgather_base


class webgather_json_picker(webgather_base):
    def __init__(self, html):
        super(webgather_json_picker, self).__init__(html)
        self.name = 'pickercommon'

    def picker_content(self, **kwargs):
        # dic = json.loads(content)
        # fileid = self.savehtml(url, content)
        dic = json.loads(self.html)
        selecters = kwargs['json'].replace(" ", "").split('>')

        def test(content, index, selects):
            if index == len(selects) - 1:
                return content
            return test(content[selects[index]], index + 1, selects)
            # for select in selects:
            #     return test(content[select], index+1,selecters[index:])

        urlitems = []
        for item in test(dic, 0, selecters):
            urlitem = Item()
            if kwargs.get('merge', ''):
                urlitem.href = kwargs['merge'].replace(r'(url)', str(item[selecters[-1]])).strip('"')
            elif kwargs.get('merge_detail_page_format', ''):
                urlitem.href = kwargs['merge_detail_page_format'] % str(item[selecters[-1]])
            elif kwargs.get('detailpageformat', ''):
                urlitem.href = kwargs['detailpageformat'] % str(item[selecters[-1]])
            else:
                urlitem.href = item[selecters[-1]]
            urlitem.title = 'json格式 不支持获取title'
            urlitems.append(urlitem.toJson())
        return urlitems


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
    # url = 'http://www.bidding.csg.cn/zbgg/index.jhtml'
    # if len(sys.argv) == 2:
    #     url = sys.argv[1]
    # if len(sys.argv) == 3:
    #     url = sys.argv[1]
    #     savepath = sys.argv[2]
    # webgather = webgather_json_picker()
    # webgather.fetch_to_lst(url)
    pass


if __name__ == '__main__':
    main()

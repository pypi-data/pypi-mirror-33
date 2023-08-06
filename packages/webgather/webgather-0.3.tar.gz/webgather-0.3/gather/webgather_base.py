# -*- coding: utf-8 -*-
import codecs
import os
import uuid
from bs4 import BeautifulSoup


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


class webgather_base(object):
    def __init__(self, html):
        self.html = html
        self.url = ''

    def savehtml(self):
        try:
            dist_folder = os.environ.get('UPLOAD_FOLDER', '/tmp/res/')
            if not os.path.exists(dist_folder):
                return ""

            soup = BeautifulSoup(self.html, "lxml")
            [x.extract() for x in soup.findAll(['script', 'style'])]
            fileid = str(uuid.uuid1()) + '.html'
            filepath = os.path.join(dist_folder, fileid)
            f = codecs.open(filepath, 'wb', 'utf-8')
            f.write(soup.prettify())
            f.close()
            print fileid
            return fileid
        except:
            return ""

# class webgather_base(object):
#     def __init__(self, headers, html, url):
#         self.html = html
#         self.headers = headers
#         self.name = ''
#         self.url = url
#
#         # elements = self.etree(html)
#         # self.doc = pq(elements)
#         # self.doc.make_links_absolute(url)
#         # self.html = self.doc.html()
#         #
#         # self.fileid = self.savehtml(self.url, self.html)
#
#         pass
#
#     def savehtml(self, url, html):
#         try:
#             dist_folder = os.environ.get('UPLOAD_FOLDER', '/tmp/res/')
#             if not os.path.exists(dist_folder):
#                 return ""
#
#             soup = BeautifulSoup(html, "lxml")
#             [x.extract() for x in soup.findAll(['script', 'style'])]
#             fileid = str(uuid.uuid1()) + '.html'
#             filepath = os.path.join(dist_folder, fileid)
#             f = codecs.open(filepath, 'wb', 'utf-8')
#             f.write(soup.prettify())
#             f.close()
#             print fileid
#             return fileid
#         except:
#             return ""

# @property
# def encoding(self):
#     """
#     encoding of Response.content.
#
#     if Response.encoding is None, encoding will be guessed
#     by header or content or chardet if available.
#     """
#     if hasattr(self, '_encoding'):
#         return self._encoding
#
#     # content is unicode
#     if isinstance(self.html, six.text_type):
#         return 'unicode'
#
#     # Try charset from content-type
#     encoding = get_encoding_from_headers(self.headers)
#     if encoding == 'ISO-8859-1':
#         encoding = None
#
#     # Try charset from content
#     if not encoding and get_encodings_from_content:
#         if six.PY3:
#             encoding = get_encodings_from_content(utils.pretty_unicode(self.html[:100]))
#         else:
#             encoding = get_encodings_from_content(self.html)
#         encoding = encoding and encoding[0] or None
#
#     # Fallback to auto-detected encoding.
#     if not encoding and chardet is not None:
#         encoding = chardet.detect(self.html)['encoding']
#
#     if encoding and encoding.lower() == 'gb2312':
#         encoding = 'gb18030'
#
#     self._encoding = encoding or 'utf-8'
#     return self._encoding
#
#
# def etree(self,html):
#     """Returns a lxml object of the response's content that can be selected by xpath"""
#     if not hasattr(self, '_elements'):
#         try:
#             parser = lxml.html.HTMLParser(encoding=self.encoding)
#             self._elements = lxml.html.fromstring(html, parser=parser)
#         except LookupError:
#             # lxml would raise LookupError when encoding not supported
#             # try fromstring without encoding instead.
#             # on windows, unicode is not availabe as encoding for lxml
#             self._elements = lxml.html.fromstring(html)
#     if isinstance(self._elements, lxml.etree._ElementTree):
#         self._elements = self._elements.getroot()
#     return self._elements

# -*- coding: utf-8 -*-
import json
import unittest
from unittest import TestCase
import codecs
import os
from page_parse import PageParse

test_folder = "./test_data"
if not os.path.exists(test_folder):
    test_folder = "./test/test_data"


class TestPageParse(TestCase):

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

    # 无条件跳过这条用例，不执行
    @unittest.skip('not run this case: test_get_page_single,手动测试')
    def test_get_page_single(self):

        # file_name = "./test_data/cb4f5e759fe84dc2f2067456aac97906.json"
        file_name = './test_data/6c7219b58e9cb3b5b462941423e2a741.json'
        f = codecs.open(file_name, 'rb', 'utf-8')
        dic = json.load(f)
        parse = PageParse()
        engine, lst, res, msg = parse.get_page_list(dic['html'], dic)
        print lst

    def test_get_page_list(self):
        """
        测试 获取网页列表
        :return:
        """
        # test_folder = "./test_data"
        # try:
        for file in os.listdir(test_folder):
            file_name = os.path.join(test_folder, file)
            if file == 'filter.json':
                continue
            f = codecs.open(file_name, 'rb', 'utf-8')
            dic = json.load(f)
            parse = PageParse()
            engine, lst, res, msg = parse.get_page_list(dic['html'], dic)
            self.assertFalse(len(lst) < 1, u"测试列表不通过,{}".format(file))

        print 'end'


if __name__ == '__main__':
    unittest.main()

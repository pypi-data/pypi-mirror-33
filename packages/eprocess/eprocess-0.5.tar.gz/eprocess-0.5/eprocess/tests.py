# -*- coding: utf-8 -*-

import unittest

from eprocess import eprocess, eprocessr, eprocessd, eprocessdr, test_data


class TestLib(unittest.TestCase):
    def setUp(self):
        self.data_list = list(range(1000))
        self.data_dict = {each: each for each in self.data_list}

    def test_success_split_with_10(self):
        result_expected = test_data.DATA_WITH_10
        data = eprocess(self.data_list)
        self.assertEqual(result_expected, list(data))

    def test_success_split_with_5(self):
        result_expected = test_data.DATA_WITH_5
        data = eprocess(self.data_list, n=5)
        self.assertEqual(result_expected, list(data))

    def test_success_split_with_5_and_callback(self):
        result_expected = test_data.DATA_WITH_5

        def test_callback(data):
            self.assertEqual(len(data), 5)

        data = eprocess(self.data_list, n=5, callback=test_callback)
        self.assertEqual(result_expected, list(data))

    def test_success_split_with_return(self):
        result_expected = test_data.DATA_WITH_PREFIX

        def test_callback(data):
            return ['prefix-{}'.format(each) for each in data]

        data = eprocessr(self.data_list, n=5, callback=test_callback)
        self.assertEqual(result_expected, list(data))

    def test_success_split_dict_with_10(self):
        result_expected = test_data.DATA_DICT_WITH_10
        data = eprocessd(self.data_dict)

        self.assertEqual(result_expected, list(data))

    def test_success_split_dict_with_5(self):
        result_expected = test_data.DATA_DICT_WITH_5
        data = eprocessd(self.data_dict, n=5)

        self.assertEqual(result_expected, list(data))

    def test_success_split_dict_with_5_and_callback(self):
        result_expected = test_data.DATA_DICT_WITH_5

        def test_callback(data):
            self.assertEqual(len(data), 5)

        data = eprocessd(self.data_dict, n=5, callback=test_callback)
        self.assertEqual(result_expected, list(data))

    def test_success_split_dict_with_return(self):
        result_expected = test_data.DATA_DICT_WITH_PREFIX

        def test_callback(data):
            return {i: 'prefix-{}'.format(i) for i in data}

        data = eprocessdr(self.data_dict, n=5, callback=test_callback)
        self.assertEqual(result_expected, list(data))


if __name__ == '__main__':
    unittest.main()

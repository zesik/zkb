# -*- coding: utf-8 -*-
"""
test.test_readers
~~~~~~~~~~~~~~~~~

This is the unit test file for readers.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import unittest
import io

from zkb.readers import *
from zkb.utils import *


class TestYamlReader(unittest.TestCase):
    def _create_stream_h_utf8(self):
        output = io.BytesIO()
        data = (u'encoding: utf-8\n'
                u'title: english 中文日本語言葉叶子\n'
                u'\n')
        output.write(data.encode('utf-8', 'replace'))
        return output

    def _create_stream_h_gb18030(self):
        output = io.BytesIO()
        data = (u'encoding: gb18030\n'
                u'title: 中文标题\n')
        output.write(data.encode('gb18030', 'replace'))
        return output

    def _create_stream_h_euc_jp(self):
        output = io.BytesIO()
        data = (u'encoding: euc-jp\n'
                u'title: 日本語言葉\n'
                u'\n')
        output.write(data.encode('euc-jp', 'replace'))
        return output

    def _create_stream_f_utf8(self):
        output = io.BytesIO()
        data = (u'title: 中文日本語言葉叶子\n'
                u'\n'
                u'コンテンツ。\n'
                u'テスト。文章。\n'
                u'\n'
                u'アーティカル。\n'
                u'--MORE--\n'
                u'詳しい内容。\n'
                u'--MORE--\n'
                u'詳しい内容。\n')
        output.write(data.encode('utf-8', 'replace'))
        return output

    def _create_stream_f_gb18030(self):
        output = io.BytesIO()
        data = (u'encoding: gb18030\n'
                u'title: 中文标题\n'
                u'\n'
                u'中文正文。\n'
                u'测试。文章。\n'
                u'\n'
                u'文章。\n'
                u'--MORE--\n'
                u'详细正文。\n')
        output.write(data.encode('gb18030', 'replace'))
        return output

    def _create_stream_f_euc_jp(self):
        output = io.BytesIO()
        data = (u'encoding: euc-jp\n'
                u'title: 日本語言葉\n'
                u'\n'
                u'コンテンツ。\n'
                u'テスト。文章。\n'
                u'\n'
                u'アーティカル。\n'
                u'--MORE--\n'
                u'詳しい内容。\n')
        output.write(data.encode('euc-jp', 'replace'))
        return output

    def _create_stream_h_unk(self):
        output = io.BytesIO()
        data = (u'encoding: fake-encoding\n'
                u'title: fake-encoding\n')
        output.write(data.encode('utf-8', 'replace'))
        return output

    def _create_stream_fm_utf8(self):
        output = io.BytesIO()
        data = (u'title: Title\n'
                u'more_separator: --CUSTOMIZED-MORE-SEPARATOR--\n'
                u'\n'
                u'Contents.\n'
                u'Article\n'
                u'\n'
                u'Article\n'
                u'--MORE--\n'
                u'Here should belong to abstract.\n'
                u'--CUSTOMIZED-MORE-SEPARATOR--\n'
                u'Here should belong to full article.\n')
        output.write(data.encode('utf-8', 'replace'))
        return output

    def _create_stream_fnm_utf8(self):
        output = io.BytesIO()
        data = (u'title: Title\n'
                u'more_separator: --CUSTOMIZED-MORE-SEPARATOR--\n'
                u'\n'
                u'Contents.\n'
                u'Article\n'
                u'\n'
                u'Article\n'
                u'--MORE--\n'
                u'Here should belong to full article.\n'
                u'--MORE--\n'
                u'Here should belong to full article.\n')
        output.write(data.encode('utf-8', 'replace'))
        return output

    def _destroy_buffers(self, streams):
        for stream in streams:
            stream.close()

    def _verify_headers(self, result):
        self.assertEqual(result[0][0]['encoding'], 'utf-8',
                         'encoding is not correctly read')
        self.assertEqual(result[1][0]['encoding'], 'gb18030',
                         'encoding is not correctly read')
        self.assertEqual(result[2][0]['encoding'], 'euc-jp',
                         'encoding is not correctly read')
        self.assertFalse('encoding' in result[3][0])
        self.assertEqual(result[4][0]['encoding'], 'gb18030',
                         'encoding is not correctly read')
        self.assertEqual(result[5][0]['encoding'], 'euc-jp',
                         'encoding is not correctly read')
        self.assertEqual(result[0][0]['title'], u'english 中文日本語言葉叶子',
                         'title is not correctly read')
        self.assertEqual(result[1][0]['title'], u'中文标题',
                         'title is not correctly read')
        self.assertEqual(result[2][0]['title'], u'日本語言葉',
                         'title is not correctly read')
        self.assertEqual(result[3][0]['title'], u'中文日本語言葉叶子',
                         'title is not correctly read')
        self.assertEqual(result[4][0]['title'], u'中文标题',
                         'title is not correctly read')
        self.assertEqual(result[5][0]['title'], u'日本語言葉',
                         'title is not correctly read')

    def test_read_unsupported_encoding(self):
        reader = YamlHeaderedContentReader()
        s = self._create_stream_h_unk()
        with self.assertRaises(UnknownEncodingError) as e:
            reader.read(s)
        self._destroy_buffers([s])
        self.assertEqual(e.exception.encoding, 'fake-encoding',
                         'encoding incorrect')

    def test_read_header_only(self):
        reader = YamlHeaderedContentReader()
        s = [self._create_stream_h_utf8(),
             self._create_stream_h_gb18030(),
             self._create_stream_h_euc_jp(),
             self._create_stream_f_utf8(),
             self._create_stream_f_gb18030(),
             self._create_stream_f_euc_jp()]
        result = [reader.read(s[0], False),
                  reader.read(s[1], False),
                  reader.read(s[2], False),
                  reader.read(s[3], False),
                  reader.read(s[4], False),
                  reader.read(s[5], False)]
        self._destroy_buffers(s)

        self._verify_headers(result)
        self.assertIsNone(result[0][1], 'content is not None')
        self.assertIsNone(result[1][1], 'content is not None')
        self.assertIsNone(result[2][1], 'content is not None')
        self.assertIsNone(result[3][1], 'content is not None')
        self.assertIsNone(result[4][1], 'content is not None')
        self.assertIsNone(result[5][1], 'content is not None')

    def test_read_entire_file(self):
        reader = YamlHeaderedContentReader()
        s = [self._create_stream_h_utf8(),
             self._create_stream_h_gb18030(),
             self._create_stream_h_euc_jp(),
             self._create_stream_f_utf8(),
             self._create_stream_f_gb18030(),
             self._create_stream_f_euc_jp(),
             self._create_stream_fm_utf8(),
             self._create_stream_fnm_utf8()]
        result = [reader.read(s[0]),
                  reader.read(s[1]),
                  reader.read(s[2]),
                  reader.read(s[3]),
                  reader.read(s[4]),
                  reader.read(s[5]),
                  reader.read(s[6]),
                  reader.read(s[7])]
        self._destroy_buffers(s)

        self._verify_headers(result)
        self.assertIsNotNone(result[0][2], 'content is None')
        self.assertIsNotNone(result[1][2], 'content is None')
        self.assertIsNotNone(result[2][2], 'content is None')
        self.assertIsNotNone(result[3][2], 'content is None')
        self.assertIsNotNone(result[4][2], 'content is None')
        self.assertIsNotNone(result[5][2], 'content is None')
        self.assertIsNotNone(result[6][2], 'content is None')
        self.assertIsNotNone(result[7][2], 'content is None')

        self.assertIsNone(result[0][1], 'abstract is not None')
        self.assertIsNone(result[1][1], 'abstract is not None')
        self.assertIsNone(result[2][1], 'abstract is not None')
        self.assertEqual(result[3][1], u'コンテンツ。\n'
                                       u'テスト。文章。\n'
                                       u'\n'
                                       u'アーティカル。')
        self.assertEqual(result[4][1], u'中文正文。\n'
                                       u'测试。文章。\n'
                                       u'\n'
                                       u'文章。')
        self.assertEqual(result[5][1], u'コンテンツ。\n'
                                       u'テスト。文章。\n'
                                       u'\n'
                                       u'アーティカル。')
        self.assertEqual(result[6][1], u'Contents.\n'
                                       u'Article\n'
                                       u'\n'
                                       u'Article\n'
                                       u'--MORE--\n'
                                       u'Here should belong to abstract.')
        self.assertIsNone(result[7][1], 'abstract is not None')

        self.assertEqual(result[0][2], '')
        self.assertEqual(result[1][2], '')
        self.assertEqual(result[2][2], '')
        self.assertEqual(result[3][2], u'コンテンツ。\n'
                                       u'テスト。文章。\n'
                                       u'\n'
                                       u'アーティカル。\n'
                                       u'詳しい内容。\n'
                                       u'--MORE--\n'
                                       u'詳しい内容。')
        self.assertEqual(result[4][2], u'中文正文。\n'
                                       u'测试。文章。\n'
                                       u'\n'
                                       u'文章。\n'
                                       u'详细正文。')
        self.assertEqual(result[5][2], u'コンテンツ。\n'
                                       u'テスト。文章。\n'
                                       u'\n'
                                       u'アーティカル。\n'
                                       u'詳しい内容。')
        self.assertEqual(result[6][2], u'Contents.\n'
                                       u'Article\n'
                                       u'\n'
                                       u'Article\n'
                                       u'--MORE--\n'
                                       u'Here should belong to abstract.\n'
                                       u'Here should belong to full article.')
        self.assertEqual(result[7][2], u'Contents.\n'
                                       u'Article\n'
                                       u'\n'
                                       u'Article\n'
                                       u'--MORE--\n'
                                       u'Here should belong to full article.\n'
                                       u'--MORE--\n'
                                       u'Here should belong to full article.')

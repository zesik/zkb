"""
test.test_builder
~~~~~~~~~~~~~~~~~

This is the unit test file for site builder.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import unittest
import datetime
import io

from zkb.builder import FileProcessor, SiteBuilder
from zkb.config import SiteConfig


class TestSiteBuilder(unittest.TestCase):
    class MockFileProcessor(FileProcessor):
        def get_article_files(self, dirname, ignored_dirs=None):
            return [('article1.md', 'article1', datetime.datetime(2002, 1, 5),
                     'yaml', None),
                    ('article2.md', 'article2', datetime.datetime(2002, 2, 1),
                     'yaml', None),
                    ('article2.md', 'article2', datetime.datetime(2002, 3, 1),
                     'yaml', None)]

        def read(self, filename):
            output = io.BytesIO()
            if filename == 'article1.md':
                data = (u'title: Test\n'
                        u'tag: tag1\n'
                        u'\nContent')
            elif filename == 'article2.md':
                data = (u'title: Test2\n'
                        u'tag: tag1, tag2\n'
                        u'\nContent')
            else:
                data = (u'title: Test3\n'
                        u'date: 2002/1/30\n'
                        u'tag: tag2, tag3\n'
                        u'\nContent')
            output.write(data.encode('utf-8', 'replace'))
            return output

        def write(self, filename, encoding, content):
            pass

        def write_stream(self, filename, stream):
            pass

        def copy_file(self, source, destination):
            pass

        def exists(self, file):
            return True

    class MockSiteBuilder(SiteBuilder):
        def _do_build(self):
            return self.config

    def test_site_builder(self):
        config = SiteConfig()
        config.site_builder = "test.test_builder/" \
                              "TestSiteBuilder.MockSiteBuilder"
        config = SiteBuilder.from_config(
            config, TestSiteBuilder.MockFileProcessor()).build()
        self.assertEqual(len(config.articles_by_date), 3,
                         'article count mismatch')



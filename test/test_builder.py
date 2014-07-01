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
                    ('article3.md', 'article3', datetime.datetime(2002, 3, 1),
                     'yaml', None),
                    ('about.md', 'about', datetime.datetime(2002, 3, 1),
                     'yaml', None),
                    ('404.html', '404', datetime.datetime(2002, 3, 1),
                     'yaml', None)]

        def read(self, filename):
            output = io.BytesIO()
            if filename == 'article1.md':
                data = (u'title: Test\n'
                        u'tags: tag1\n'
                        u'\nContent')
            elif filename == 'article2.md':
                data = (u'title: Test2\n'
                        u'tags: tag1, tag2\n'
                        u'\nContent')
            elif filename == 'article3.md':
                data = (u'title: Test3\n'
                        u'date: 2002-1-30 18:00:00\n'
                        u'tags: tag2, tag3\n'
                        u'\nContent')
            elif filename == 'about.md':
                data = (u'title: About\n'
                        u'article_type: about\n'
                        u'\nbout')
            elif filename == '404.html':
                data = (u'title: Not Found\n'
                        u'article_type: 404\n'
                        u'url: /404.html\n'
                        u'\nNot Found')
            else:
                data = ''
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
                         'there should be 3 articles in total')
        self.assertEqual(len(config.articles_by_tag), 3,
                         'there should be 3 tags in total')
        self.assertEqual(len(config.special_articles), 2,
                         'there should be 2 special articles')
        self.assertEqual(config.articles_by_date[0].title, 'Test2',
                         'title of the 1st article should be Test2')
        self.assertEqual(config.articles_by_date[1].title, 'Test3',
                         'title of the 2nd article should be Test3')
        self.assertEqual(config.articles_by_date[2].title, 'Test',
                         'title of the 3rd article should be Test')
        self.assertEqual(len(config.articles_by_tag['tag1']), 2,
                         'tag1 should have 2 articles')
        self.assertEqual(len(config.articles_by_tag['tag2']), 2,
                         'tag2 should have 2 articles')
        self.assertEqual(len(config.articles_by_tag['tag3']), 1,
                         'tag3 should have 1 article')
        self.assertEqual(config.articles_by_tag['tag1'][0].title, 'Test2',
                         'title of 1st article of tag1 should be Test2')
        self.assertEqual(config.articles_by_tag['tag1'][1].title, 'Test',
                         'title of 2nd article of tag1 should be Test')
        self.assertEqual(config.articles_by_tag['tag2'][0].title, 'Test2',
                         'title of 1st article of tag2 should be Test2')
        self.assertEqual(config.articles_by_tag['tag2'][1].title, 'Test3',
                         'title of 2nd article of tag2 should be Test3')
        self.assertEqual(config.articles_by_tag['tag3'][0].title, 'Test3',
                         'title of 1st article of tag3 should be Test3')
        self.assertEqual(config.special_articles['about'].title, 'About',
                         'title of about article should be About')
        self.assertEqual(config.special_articles['404'].title, 'Not Found',
                         'title of 404 article should be Not Found')

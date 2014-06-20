# -*- coding: utf-8 -*-
"""
zkb.config
~~~~~~~~~~

This module contains classes representing config file of the blog.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import inspect
import itertools
import yaml
import os
from time import strftime, localtime

from zkb.utils import DEFAULT_ENCODING
from zkb.utils import RequiredSettingIncorrectError


class ConfigItem(object):
    """Represents an configurable item."""
    _counter = itertools.count()
    NORMAL = 0
    PRIVATE = 1
    DYNAMIC = 2

    def __init__(self, default, doc, config_type):
        super(ConfigItem, self).__init__()
        self.order = next(ConfigItem._counter)
        self.default = default
        self.doc = doc
        self.type = config_type


class ConfigBase(object):
    def __init__(self):
        super(ConfigBase, self).__init__()

    @classmethod
    def default_config(cls):
        """Get a list of string representing a YAML formatted default values.

        :rtype: list of str
        """

        def _filter_normal_config(value):
            return isinstance(value, ConfigItem) \
                and value.type == ConfigItem.NORMAL

        out = []
        items = []
        for item in inspect.getmembers(cls, _filter_normal_config):
            items.append(item)
        items.sort(key=lambda x: x[1].order)
        for name, item in items:
            for line in item.doc.split('\n'):
                out.append('# %s\n' % line)
            out_dict = {name[1:]: item.default}
            out.append(yaml.dump(out_dict, default_flow_style=False))
        return out

    def update(self, config):
        """Update configuration with dictionary.

        :param config: configuration dictionary.
        :type config: dict
        """
        if config is not None:
            for key, value in config.iteritems():
                setattr(self, key, value)


class SiteConfig(ConfigBase):
    """Represents site config file."""

    _encoding = ConfigItem(
        DEFAULT_ENCODING,
        'Encoding of the config file.',
        ConfigItem.NORMAL)
    _url = ConfigItem(
        'example.com/blog/',
        'URL where the blog will be deployed, which starts with domain name '
        'and contains path. The string must end with \'/\'.',
        ConfigItem.NORMAL)
    _title = ConfigItem(
        'Blog Title',
        'Title of the blog.',
        ConfigItem.NORMAL)
    _subtitle = ConfigItem(
        'Blog Subtitle',
        'Subtitle of the blog.',
        ConfigItem.NORMAL)
    _article_dir = ConfigItem(
        '.',
        'Directory where all article sources are placed.',
        ConfigItem.PRIVATE)
    _output_dir = ConfigItem(
        '_site',
        'Directory where all generated files are placed.',
        ConfigItem.PRIVATE)
    _git_remote = ConfigItem(
        'http://example.com/blog.git',
        'Git remote repository where blog source is stored (on \'source\' '
        'branch) and blog is deployed (on \'master\' branch).',
        ConfigItem.NORMAL)
    _author = ConfigItem(
        'Author',
        'Name of the author. This setting can be overwritten in each article.',
        ConfigItem.NORMAL)
    _email = ConfigItem(
        'author@example.com',
        'Email address of the author. This setting can be overwritten in each '
        'article.',
        ConfigItem.NORMAL)
    _show_search_box = ConfigItem(
        True,
        'Whether a search box should be shown.',
        ConfigItem.NORMAL)
    _article_encoding = ConfigItem(
        DEFAULT_ENCODING,
        'Default encoding of article source files. This setting can be '
        'overwritten in each article.',
        ConfigItem.NORMAL)
    _enable_latex = ConfigItem(
        False,
        'Whether LaTeX support is enabled. This setting can be overwritten in '
        'each article.',
        ConfigItem.NORMAL)
    _enable_comments = ConfigItem(
        True,
        'Whether comments is enabled. This setting can be overwritten in each '
        'article. Comments utilize Disqus, so if Disqus short name is not '
        'provided, the comment function cannot be enabled.',
        ConfigItem.NORMAL)
    _date_format = ConfigItem(
        '%Y-%m-%d %H:%M:%S',
        'Format of date that specified in each article.',
        ConfigItem.NORMAL)
    _language = ConfigItem(
        'en',
        'Language of the blog and article.',
        ConfigItem.NORMAL)
    _copyright = ConfigItem(
        'Copyright ' + strftime("%Y", localtime()),
        'Copyright notice to be put at the bottom of every page.',
        ConfigItem.NORMAL)
    _page_size = ConfigItem(
        5,
        'Count of articles to be shown on each page.',
        ConfigItem.NORMAL)
    _site_builder = ConfigItem(
        {'name': 'DefaultSiteBuilder'},
        'Configuration of class to build the site.',
        ConfigItem.PRIVATE)
    _google_analytics = ConfigItem(
        '',
        'Google Analytics tracking ID. Google Analytics also needs domain '
        'name, which will be provided with configuration in \'url\'.',
        ConfigItem.NORMAL)
    _cnzz_statistics = ConfigItem(
        '',
        'CNZZ statistics ID.',
        ConfigItem.PRIVATE)
    _disqus_shortname = ConfigItem(
        '',
        'Disqus shortname of your blog.',
        ConfigItem.NORMAL)
    _domain = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _articles_by_date = ConfigItem(
        list(),
        None,
        ConfigItem.DYNAMIC)
    _articles_by_tag = ConfigItem(
        dict(),
        None,
        ConfigItem.DYNAMIC)
    _special_articles = ConfigItem(
        list(),
        None,
        ConfigItem.DYNAMIC)
    _about_url = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)

    def __init__(self, config=None):
        """Initialize the site config class.

        :param config: configuration dictionary.
        :type config: dict
        """
        super(SiteConfig, self).__init__()
        self.encoding = SiteConfig._encoding.default
        self.url = SiteConfig._url.default
        self.title = SiteConfig._title.default
        self.subtitle = SiteConfig._subtitle.default
        self.article_dir = SiteConfig._article_dir.default
        self.output_dir = SiteConfig._output_dir.default
        self.git_remote = SiteConfig._git_remote.default
        self.author = SiteConfig._author.default
        self.email = SiteConfig._email.default
        self.show_search_box = SiteConfig._show_search_box.default
        self.article_encoding = SiteConfig._article_encoding.default
        self.enable_latex = SiteConfig._enable_latex.default
        self.enable_comments = SiteConfig._enable_comments.default
        self.date_format = SiteConfig._date_format.default
        self.language = SiteConfig._language.default
        self.copyright = SiteConfig._copyright.default
        self.page_size = SiteConfig._page_size.default
        self.site_builder = SiteConfig._site_builder.default
        self.google_analytics = SiteConfig._google_analytics.default
        self.cnzz_statistics = SiteConfig._cnzz_statistics.default
        self.disqus_shortname = SiteConfig._disqus_shortname.default
        self.domain = SiteConfig._domain.default
        self.articles_by_date = SiteConfig._articles_by_date.default
        self.articles_by_tag = SiteConfig._articles_by_tag.default
        self.special_articles = SiteConfig._special_articles.default
        self.about_url = SiteConfig._about_url.default
        self.update(config)
        self._ensure_config()

    def _ensure_config(self):
        """Format some items of the config to make sure it can be properly
        handled in the future.
        """
        # Separate domain and path
        index = self.url.find('/')
        if index == -1:
            raise RequiredSettingIncorrectError('url')
        if not self.url.endswith('/'):
            self.url += '/'
        self.domain = self.url[:index]
        self.url = self.url[index:]
        # Add separator for directory.
        if not self.output_dir.endswith(os.sep):
            self.output_dir += os.sep



class ArticleConfig(ConfigBase):
    """Represents config for articles."""

    ABOUT_PAGE = 'about'

    _encoding = ConfigItem(
        DEFAULT_ENCODING,
        'Encoding of this article file.',
        ConfigItem.NORMAL)
    _title = ConfigItem(
        '',
        'Title of the article.',
        ConfigItem.NORMAL)
    _author = ConfigItem(
        '',
        'Author of the article.',
        ConfigItem.PRIVATE)
    _email = ConfigItem(
        '',
        'Email of article\'s author.',
        ConfigItem.PRIVATE)
    _draft = ConfigItem(
        False,
        'Whether the article is a draft and is not ready for publishing.',
        ConfigItem.PRIVATE)
    _slug = ConfigItem(
        '',
        'Slug title of the article.',
        ConfigItem.PRIVATE)
    _date = ConfigItem(
        '',
        'Date when the article published.',
        ConfigItem.NORMAL)
    _tags = ConfigItem(
        '',
        'Tags of the article.',
        ConfigItem.NORMAL)
    _language = ConfigItem(
        'en',
        'Language of the article.',
        ConfigItem.PRIVATE)
    _article_type = ConfigItem(
        '',
        'Type of the article.',
        ConfigItem.PRIVATE)
    _enable_comments = ConfigItem(
        True,
        'Whether comments are enabled in this article.',
        ConfigItem.NORMAL)
    _enable_latex = ConfigItem(
        False,
        'Whether LaTeX support is enabled in this article.',
        ConfigItem.NORMAL)
    _filename = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _header_type = ConfigItem(
        'yaml',
        None,
        ConfigItem.DYNAMIC)
    _content_type = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _content_source = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _content_html = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _destination_file = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _destination_url = ConfigItem(
        '',
        None,
        ConfigItem.DYNAMIC)
    _header_scripts = ConfigItem(
        list(),
        None,
        ConfigItem.DYNAMIC)
    _local_references = ConfigItem(
        dict(),
        None,
        ConfigItem.DYNAMIC)

    def __init__(self, site_config=None, config=None):
        """Initialize an article config.

        :param site_config: site configuration.
        :type site_config: SiteConfig
        :param config: configuration dictionary.
        :type config: dict
        """
        super(ArticleConfig, self).__init__()
        self.filename = ArticleConfig._filename.default
        self.header_type = ArticleConfig._header_type.default
        self.content_type = ArticleConfig._content_type.default
        self.encoding = ArticleConfig._encoding.default
        self.date = ArticleConfig._date.default
        self.language = ArticleConfig._language.default
        self.content_source = ArticleConfig._content_source.default
        self.content_html = ArticleConfig._content_html.default
        self.title = ArticleConfig._title.default
        self.author = ArticleConfig._author.default
        self.email = ArticleConfig._email.default
        self.draft = ArticleConfig._draft.default
        self.slug = ArticleConfig._slug.default
        self.tags = ArticleConfig._tags.default
        self.enable_comments = ArticleConfig._enable_comments.default
        self.enable_latex = ArticleConfig._enable_latex.default
        self.destination_file = ArticleConfig._destination_file.default
        self.destination_url = ArticleConfig._destination_url.default
        self.header_scripts = ArticleConfig._header_scripts.default
        self.local_references = ArticleConfig._local_references.default
        self.article_type = ArticleConfig._article_type.default
        if site_config is not None:
            self.encoding = site_config.article_encoding
            self.language = site_config.language
            self.author = site_config.author
            self.email = site_config.email
            self.enable_comments = site_config.enable_comments
            self.enable_latex = site_config.enable_latex
        self.update(config)

# -*- coding: utf-8 -*-
"""
zkb.builders
~~~~~~~~~~~~

Build content of the article, convert to source format to HTML format.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import datetime
import codecs
import os
import shutil
import types
from itertools import tee, islice, chain, izip

import pkg_resources
from slugify import slugify
from jinja2 import Environment, PackageLoader, FileSystemLoader, ChoiceLoader

from zkb.readers import HeaderedContentReader
from zkb.bodygenerators import BodyGenerator, SUPPORTED_GENERATOR_EXTENSIONS
from zkb.utils import UnknownBuilderError
from zkb.config import SiteConfig, ArticleConfig
from zkb.log import logger


_INDEX_PAGE = 'index.html'
_404_PAGE = '404.html'


class FileProcessor(object):
    _ARTICLE_HEADER_TYPE = 'yaml'

    """Actual handler of file operation.
    """

    def get_article_files(self, dirname, ignored_dirs=None):
        all_article_files = []
        if ignored_dirs is None:
            ignored_dirs = []
        else:
            ignored_dirs = [os.path.realpath(path) for path in ignored_dirs]
        for root, dirs, files in os.walk(dirname):
            real_path = os.path.realpath(root)
            should_ignore = False
            for ignored_dir in ignored_dirs:
                relative = os.path.relpath(ignored_dir, real_path)
                if relative == os.curdir or relative == os.pardir \
                        or relative.startswith(os.pardir + os.sep):
                    should_ignore = True
                    break
            if should_ignore:
                continue
            for filename in files:
                full_path = os.path.join(root, filename)
                extension = os.path.splitext(filename)[1].lower()
                if extension not in SUPPORTED_GENERATOR_EXTENSIONS:
                    continue
                item = (full_path,
                        os.path.splitext(filename)[0],
                        datetime.datetime.fromtimestamp(
                            os.path.getmtime(full_path)),
                        FileProcessor._ARTICLE_HEADER_TYPE,
                        None)
                all_article_files.append(item)
        return all_article_files

    def read(self, filename):
        logger.debug('Reading from \'%s\'...' % filename)
        return open(filename, 'r')

    def write(self, filename, encoding, content):
        logger.debug('Writing to \'%s\'...' % filename)
        dest_dir = os.path.dirname(filename)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with open(filename, 'w+') as f:
            f.write(content.encode(encoding))

    def write_stream(self, filename, stream):
        logger.debug('Writing to \'%s\' with stream...' % filename)
        dest_dir = os.path.dirname(filename)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with open(filename, 'wb+') as f:
            f.write(stream.read())

    def copy_file(self, source, destination):
        logger.debug('Copying \'%s\' to \'%s\'...' % (source, destination))
        dest_dir = os.path.dirname(destination)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy2(source, destination)

    def exists(self, file):
        logger.debug('Checking file \'%s\'...' % (file))
        return os.path.isfile(file)


class SiteBuilder(object):
    """This class (and its subclasses) handles the core logic of building the
    blog site. To build the site, create a builder with func:`from_config` with
    the site config.

    :param config: configuration of the blog site.
    :type config: SiteConfig
    :param fileproc: file processor.
    :type fileproc: FileProcessor
    """
    def __init__(self, config, fileproc=None):
        super(SiteBuilder, self).__init__()
        self.config = config
        if fileproc is None:
            self.fileproc = FileProcessor()
        else:
            self.fileproc = fileproc

    @classmethod
    def from_config(cls, config, fileproc=None):
        name = config.site_builder
        if type(name) not in types.StringTypes or len(name) == 0:
            name = DefaultSiteBuilder.__name__
        try:
            constructor = globals()[name]
        except KeyError:
            raise UnknownBuilderError(name)
        return constructor(config, fileproc)

    def build(self):
        """Main logic for building the site.
        """
        articles_by_date = []
        articles_by_tag = {}
        special_articles = {}
        for full_path, filename, mtime, header_type, content_type in \
                self.fileproc.get_article_files(
                        self.config.article_dir, [self.config.output_dir]):
            # Read article
            logger.info('Parsing \'%s\'...' % full_path)
            with self.fileproc.read(full_path) as stream:
                reader = HeaderedContentReader.from_type(header_type)
                header, abstract, body = reader.read(stream)
            article = ArticleConfig(self.config, header)
            # Ignore all draft articles
            if article.draft:
                continue
            article.source_file = full_path
            if len(article.title) == 0:
                article.title = filename
            article.content_source = body
            # Generate body
            if content_type is None:
                extension = os.path.splitext(full_path)[1].lower()
                generator = BodyGenerator.from_extension(extension)
            else:
                generator = BodyGenerator.from_type(content_type)
            if abstract is None:
                article.abstract = None
            else:
                article.abstract['html'], meta = generator.generate(
                    abstract, base=full_path, url=self.config.url)
                article.abstract.update(meta)
            article.full['html'], meta = generator.generate(
                body, base=full_path, url=self.config.url)
            article.full.update(meta)
            # Add date object
            if isinstance(article.date, datetime.date):
                article.date = datetime.datetime.combine(
                    article.date, datetime.time(0, 0))
            elif not isinstance(article.date, datetime.datetime):
                if len(article.date) == 0:
                    article.date = mtime
                else:
                    article.date = datetime.datetime.strptime(
                        article.date, self.config.date_format)
            # Add slug info
            if len(article.slug) == 0:
                article.slug = slugify(article.title)
            # Add tag info
            if not isinstance(article.tags, str):
                article.tags = str(article.tags)
            article.tags = filter(
                None, [tag.strip() for tag in article.tags.split(',')])
            # Special procedure for special pages.
            if not isinstance(article.article_type, str):
                article.article_type = str(article.article_type)
            if article.article_type == ArticleConfig.ABOUT_PAGE \
                    or article.article_type == ArticleConfig.NOT_FOUND_PAGE:
                article.tags = []
                special_articles[article.article_type] = article
                continue
            # Add article reference.
            articles_by_date.append(article)
            for tag in article.tags:
                if tag not in articles_by_tag:
                    articles_by_tag[tag] = []
                articles_by_tag[tag].append(article)
        articles_by_date.sort(key=lambda article: article.date, reverse=True)
        self.config.articles_by_date = articles_by_date
        self.config.articles_by_tag = articles_by_tag
        self.config.special_articles = special_articles
        return self._do_build()

    def _do_build(self):
        """Write output data for the blog.
        """
        pass


def _get_chunks(arr, chunk_size):
    chunks = [arr[start:start + chunk_size] for start in
              range(0, len(arr), chunk_size)]
    return chunks


def _get_prev_and_next(iterator):
    prevs, items, nexts = tee(iterator, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)


def _get_safe_tag_url(value):
    return ''.join([x if x.isalnum() else '_' for x in value])


class DefaultSiteBuilder(SiteBuilder):
    def __init__(self, config, fileproc=None):
        super(DefaultSiteBuilder, self).__init__(config, fileproc)
        self._load_resources()

    def _load_resources(self):
        def _format_date(value, date_format='medium'):
            if date_format == 'short':
                return value.strftime('%Y-%m-%d')
            elif date_format == 'medium':
                return '{0:%b} {0.day}, {0:%Y}'.format(value)
            elif date_format == 'year':
                return value.strftime('%Y')
            elif date_format == 'md':
                return '{0:%b} {0.day}'.format(value)

        def _rot13(value):
            return codecs.encode(value, 'rot_13')

        loader = ChoiceLoader([
            FileSystemLoader(self.config.template_dir),
            PackageLoader('zkb', 'templates/default')])
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        env.filters['date'] = _format_date
        env.filters['rot13'] = _rot13
        env.filters['safe_url'] = _get_safe_tag_url
        self.article_template = env.get_template('article.html')
        self.index_template = env.get_template('index.html')
        self.archive_template = env.get_template('archive.html')
        self.tags_templates = env.get_template('tags.html')
        resource_files = [
            'stylesheets/style.css',
            'stylesheets/codeblock.css',
            'images/header-1.jpg',
            'images/header-2.jpg']
        self._package_resources = []
        self._fs_resources = []
        for item in resource_files:
            if self.fileproc.exists(os.path.join(
                    self.config.template_dir, *item.split('/'))):
                self._fs_resources.append(item)
            else:
                self._package_resources.append(item)

    def _add_path_info(self):
        """Add info of path and output directory for each article.

        :param config: site configuration.
        :type config: SiteConfig
        """
        root_parts = filter(None, self.config.url.split('/'))
        # Add path info for special pages
        for article_type, article in self.config.special_articles.iteritems():
            if article_type == ArticleConfig.ABOUT_PAGE:
                article.url = self.config.url + ArticleConfig.ABOUT_PAGE + \
                    '/' + _INDEX_PAGE
                article.output_file = os.path.join(
                    self.config.output_dir,
                    *(root_parts + [ArticleConfig.ABOUT_PAGE, _INDEX_PAGE]))
                self.config.about_url = article.url
            elif article_type == ArticleConfig.NOT_FOUND_PAGE:
                if len(article.url) == 0:
                    article.url = self.config.url + _404_PAGE
                article.output_file = os.path.join(
                    self.config.output_dir,
                    *(root_parts + filter(None, article.url.split('/'))))
        # Add path info for articles
        for article in self.config.articles_by_date:
            path_parts = ['%d' % article.date.year,
                          '%02d' % article.date.month,
                          '%02d' % article.date.day,
                          article.slug]
            article.url = self.config.url + '/'.join(path_parts) + \
                '/' + _INDEX_PAGE
            article.output_file = os.path.join(
                self.config.output_dir,
                *(root_parts + path_parts + [_INDEX_PAGE]))

    def _build_special_pages(self):
        """Build special pages.

        :param config: site configuration.
        :type config: SiteConfig
        """
        for _, article in self.config.special_articles.iteritems():
            logger.info('Rendering \'%s\'...' % article.url)
            output = self.article_template.render({
                'site': self.config,
                'article': article,
                'header_scripts': article.full['header_scripts']
            })
            self.fileproc.write(
                article.output_file, self.config.encoding, output)

    def _build_article_pages(self):
        """Build article pages.

        :param config: site configuration.
        :type config: SiteConfig
        """
        for prev_article, article, next_article in \
                _get_prev_and_next(self.config.articles_by_date):
            logger.info('Rendering \'%s\'...' % article.url)
            output = self.article_template.render({
                'site': self.config,
                'article': article,
                'prev': prev_article,
                'next': next_article,
                'header_scripts': article.full['header_scripts']
            })
            self.fileproc.write(
                article.output_file, self.config.encoding, output)

    def _build_archive_pages(self):
        """Build archive pages.

        :param config: site configuration.
        :type config: SiteConfig
        """
        root_parts = filter(None, self.config.url.split('/'))
        tags = list(self.config.articles_by_tag.keys())
        tags.insert(0, '')
        for tag in tags:
            if len(tag) == 0:
                dest_file = os.path.join(
                    self.config.output_dir,
                    *(root_parts + ['archive', _INDEX_PAGE]))
                dest_url = self.config.url + 'archive/' + _INDEX_PAGE
            else:
                safe_dir = _get_safe_tag_url(tag)
                dest_file = os.path.join(
                    self.config.output_dir,
                    *(root_parts + ['tags', safe_dir, _INDEX_PAGE]))
                dest_url = self.config.url + 'tags/' + safe_dir + \
                    '/' + _INDEX_PAGE
            logger.info('Rendering \'%s\'...' % dest_url)
            output = self.archive_template.render({
                'site': self.config,
                'tag': tag
            })
            self.fileproc.write(dest_file, self.config.encoding, output)

    def _build_tags_page(self):
        """Build tags page.

        :param config: site configuration.
        :type config: SiteConfig
        """
        root_parts = filter(None, self.config.url.split('/'))
        dest_file = os.path.join(self.config.output_dir,
                                 *(root_parts + ['tags', _INDEX_PAGE]))
        dest_url = self.config.url + 'tags/' + _INDEX_PAGE
        logger.info('Rendering \'%s\'...' % dest_url)
        output = self.tags_templates.render({
            'site': self.config,
        })
        self.fileproc.write(
            dest_file, self.config.encoding, output)

    def _build_index_pages(self):
        """Build index pages.

        :param config: site configuration.
        :type config: SiteConfig
        """
        root_parts = filter(None, self.config.url.split('/'))
        chunks = _get_chunks(self.config.articles_by_date,
                             self.config.page_size)
        for index, chunk in enumerate(chunks):
            if index == 0:
                dest_file = os.path.join(self.config.output_dir,
                                         *(root_parts + [_INDEX_PAGE]))
                dest_url = self.config.url + _INDEX_PAGE
            else:
                dest_file = os.path.join(
                    self.config.output_dir,
                    *(root_parts + ['page', str(index + 1), _INDEX_PAGE]))
                dest_url = self.config.url + 'page/' + str(index + 1) + \
                    '/' + _INDEX_PAGE
            if index == 0:
                prev_url = ''
            elif index == 1:
                prev_url = self.config.url
            else:
                prev_url = self.config.url + '/'.join(['page', str(index)])
            if index == len(chunks) - 1:
                next_url = ''
            else:
                next_url = self.config.url + '/'.join(['page', str(index + 2)])
            header_scripts = set()
            for article in chunk:
                if article.abstract is not None:
                    data_to_insert = article.abstract['header_scripts']
                else:
                    data_to_insert = article.full['header_scripts']
                header_scripts.update(data_to_insert)
            logger.info('Rendering \'%s\'...' % dest_url)
            output = self.index_template.render({
                'site': self.config,
                'articles': chunk,
                'prev_url': prev_url,
                'next_url': next_url,
                'header_scripts': header_scripts
            })
            self.fileproc.write(dest_file, self.config.encoding, output)

    def _copy_resources(self):
        """Copy resource files used in articles.

        :param config: site configuration.
        :type config: SiteConfig
        """
        resources = {}
        for _, article in self.config.special_articles.iteritems():
            resources.update(article.full['local_references'])
        for article in self.config.articles_by_date:
            resources.update(article.full['local_references'])
        for source, dest in resources.iteritems():
            dest_file = os.path.join(self.config.output_dir, *dest)
            url = self.config.url + '/'.join(*dest)
            logger.info('Writing resource \'%s\'...' % url)
            self.fileproc.copy_file(source, dest_file)

    def _copy_template_resources(self):
        """Copy resource files.

        :param config: site configuration.
        :type config: SiteConfig
        """
        root_parts = filter(None, self.config.url.split('/'))
        dest_dir = os.path.join(self.config.output_dir, *root_parts)
        for filename in self._fs_resources:
            logger.info('Writing resource \'%s\'...' %
                        (self.config.url + filename))
            self.fileproc.copy_file(
                os.path.join(self.config.template_dir, *filename.split('/')),
                os.path.join(dest_dir, *filename.split('/')))
        for filename in self._package_resources:
            logger.info('Writing resource \'%s\'...' %
                        (self.config.url + filename))
            stream = pkg_resources.resource_stream(
                'zkb', 'templates/default/' + filename)
            dest_filename = os.path.join(dest_dir, *filename.split('/'))
            self.fileproc.write_stream(dest_filename, stream)

    def _do_build(self):
        self._add_path_info()
        self._build_special_pages()
        self._build_article_pages()
        self._build_archive_pages()
        self._build_tags_page()
        self._build_index_pages()
        self._copy_resources()
        self._copy_template_resources()
        return 0

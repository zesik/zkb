# -*- coding: utf-8 -*-
"""
zkb.bodygenerators
~~~~~~~~~~~~~~~~~~

Converter from payload of input file to body content of output.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import re
import os
import hashlib

from markdown import Markdown
from markdown.inlinepatterns import LinkPattern
from markdown.inlinepatterns import ReferencePattern
from markdown.inlinepatterns import ImagePattern
from markdown.inlinepatterns import ImageReferencePattern
from markdown.inlinepatterns import LINK_RE
from markdown.inlinepatterns import REFERENCE_RE
from markdown.inlinepatterns import IMAGE_LINK_RE
from markdown.inlinepatterns import IMAGE_REFERENCE_RE
from markdown.inlinepatterns import SHORT_REF_RE

from zkb.log import logger
from zkb.mdext.blockformatter import BlockHtmlFormatterExtension
from zkb.mdext.blockformatter import CODE_HIGHLIGHT_CLASS
from zkb.mdext.codeblock import CodeBlockHtmlFormatter
from zkb.mdext.latexblock import LatexBlockHtmlFormatter


_REMOTE_LINK_PATTERN = re.compile(r'(\w+:)?//.+')
_BLOCK_SIZE = 65536


class RelocatingImagePattern(ImagePattern):
    """Extension of Markdown image pattern to record local references of
    images and replace them with correct file path.
    """

    def __init__(self, pattern, md_instance, relocator):
        super(RelocatingImagePattern, self).__init__(pattern, md_instance)
        self.relocator = relocator

    def handleMatch(self, m):
        el = super(RelocatingImagePattern, self).handleMatch(m)
        # Check 'src' for local files.
        src = el.attrib.get('src')
        target = self.relocator.relocate(src)
        if target is not None:
            el.attrib['src'] = target
        return el


class RelocatingImageReferencePattern(ImageReferencePattern):
    """Extension of Markdown image reference pattern to record local references
    of images.

    .. note:: Links that do not start with 'http://', 'ftp://', etc. are
    considered as local references. That is, relative links are also considered
    as local reference because we cannot separated them from links to local
    files.
    """

    def __init__(self, pattern, md_instance, relocator):
        super(RelocatingImageReferencePattern, self).__init__(
            pattern, md_instance)
        self.relocator = relocator

    def makeTag(self, href, title, text):
        el = super(RelocatingImageReferencePattern, self).makeTag(
            href, title, text)
        # Check 'src' for local files.
        src = el.attrib.get('src')
        target = self.relocator.relocate(src)
        if target is not None:
            el.attrib['src'] = target
        return el


class RelocatingLinkPattern(LinkPattern):
    """Extension of Markdown link pattern to record local references of files.

    .. note:: Links that do not start with 'http://', 'ftp://', etc. are
    considered as local references. That is, relative links are also considered
    as local reference because we cannot separated them from links to local
    files.
    """

    def __init__(self, pattern, md_instance, relocator):
        super(RelocatingLinkPattern, self).__init__(pattern, md_instance)
        self.relocator = relocator

    def handleMatch(self, m):
        el = super(RelocatingLinkPattern, self).handleMatch(m)
        # Check 'src' for local files.
        src = el.attrib.get('href')
        target = self.relocator.relocate(src)
        if target is not None:
            el.attrib['href'] = target
        return el


class RelocatingReferencePattern(ReferencePattern):
    """Extension of Markdown reference pattern to record local references of
    files.

    .. note:: Links that do not start with 'http://', 'ftp://', etc. are
    considered as local references. That is, relative links are also considered
    as local reference because we cannot separated them from links to local
    files.
    """

    def __init__(self, pattern, md_instance, relocator):
        super(RelocatingReferencePattern, self).__init__(pattern, md_instance)
        self.relocator = relocator

    def makeTag(self, href, title, text):
        el = super(RelocatingReferencePattern, self).makeTag(href, title, text)
        # Check 'src' for local files.
        src = el.attrib.get('href')
        target = self.relocator.relocate(src)
        if target is not None:
            el.attrib['href'] = target
        return el


class ResourceRelocator(object):
    """Relocate resources to a specific directory."""

    def __init__(self, base, prefix='resources', url_prefix=None):
        super(ResourceRelocator, self).__init__()
        self.resources = {}
        if os.path.isfile(base):
            self.base_dir = os.path.dirname(os.path.abspath(base))
        else:
            self.base_dir = os.path.abspath(base)
        self.prefix = prefix
        self.url_prefix = url_prefix

    def _should_relocate(self, src):
        """Check whether a reference should be relocated.

        :param src: reference source.
        :type src: str
        :rtype: bool
        """
        return (not _REMOTE_LINK_PATTERN.match(src)) and os.path.isfile(src)

    def _get_hash(self, filename):
        """Get SHA1 hash of a file.

        :param filename: file name.
        :type filename: str
        :rtype: str
        """
        hasher = hashlib.sha1()
        try:
            with open(filename, 'rb') as stream:
                buf = stream.read(_BLOCK_SIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = stream.read(_BLOCK_SIZE)
            return hasher.hexdigest()
        except IOError as e:
            logger.debug('Error while hashing file: %s' % e.strerror)
        return None

    def _get_relocate_dir(self, filename):
        """Relocate a local file into specific directory.

        :param filename: file name.
        :type filename: str
        :return: list
        """
        file_hash = self._get_hash(filename)
        if file_hash is not None:
            out = [self.prefix,
                   file_hash[0:2],
                   file_hash[2:4],
                   file_hash[4:],
                   os.path.basename(filename)]
            if self.url_prefix is not None and len(self.url_prefix) > 0:
                out.insert(0, self.url_prefix)
            return out
        return None

    def relocate(self, src):
        """Relocate a resource path for generated site.

        :param src: original resource path.
        :type src: str
        :return: relocated resource path.
        :rtype: str
        """

        def _to_url(array):
            return '/' + '/'.join(array)

        if not self._should_relocate(src):
            return None
        filename = os.path.join(self.base_dir, src)
        if filename in self.resources:
            return _to_url(self.resources[filename])
        target = self._get_relocate_dir(filename)
        if target is not None:
            self.resources[filename] = target
            return _to_url(target)
        return None


class BodyGenerator(object):
    """Base generator class for creating main content of the article from body
    of the article file.
    """

    def __init__(self):
        super(BodyGenerator, self).__init__()

    @classmethod
    def from_extension(cls, extension, **kwargs):
        """Create a body generator based on file extension.

        :param extension: file extension.
        :type extension: str
        :return: an instance of one child class of BodyGenerator, or None if
            the extension cannot be recognized.
        :rtype: BodyGenerator
        """
        extension = extension.lower()
        if extension in _GENERATOR_EXTENSIONS:
            return BodyGenerator.from_type(
                _GENERATOR_EXTENSIONS[extension], **kwargs)
        return None

    @classmethod
    def from_type(cls, generator_type, **kwargs):
        """Create a body generator based on generator type.

        :param generator_type: type of the generator.
        :type generator_type: str
        :return: an instance of one child class of BodyGenerator, or None if
            the body generator type cannot be recognized.
        :rtype: BodyGenerator
        """
        generator_type = generator_type.lower()
        if generator_type in _BODY_GENERATORS:
            constructor = globals()[_BODY_GENERATORS[generator_type]]
            return constructor(**kwargs)
        return None

    def generate(self, body, **options):
        """Generate the content from body of the payload of a file.

        :param body: payload content.
        :type body: str
        :return: a tuple of two elements, generated body and metadata
            dictionary, respectively.
        :rtype: tuple
        """
        pass


class MarkdownBodyGenerator(BodyGenerator):
    """Generator for generating body content from Markdown payload.
    """

    def generate(self, body, **options):
        """Override to generate content from Markdown payload.

        :param body: payload content.
        :type body: str
        :return: a tuple of two elements, generated body and metadata
            dictionary, respectively.
        :rtype: tuple
        """
        ext = BlockHtmlFormatterExtension({
            'code': CodeBlockHtmlFormatter(css_class=CODE_HIGHLIGHT_CLASS),
            'latex': LatexBlockHtmlFormatter()
        })
        md = Markdown(output_format='html5', extensions=[ext])
        if 'relocator' in options:
            relocator = options['relocator']
        elif 'url' in options:
            relocator = ResourceRelocator(options['base'],
                                          url_prefix=options['url'][1:-1])
        else:
            relocator = ResourceRelocator(options['base'])
        recorded_patterns = {
            'reference': RelocatingReferencePattern(
                REFERENCE_RE, md, relocator),
            'link': RelocatingLinkPattern(LINK_RE, md, relocator),
            'image_link': RelocatingImagePattern(IMAGE_LINK_RE, md, relocator),
            'image_reference': RelocatingImageReferencePattern(
                IMAGE_REFERENCE_RE, md, relocator),
            'short_reference': RelocatingReferencePattern(
                SHORT_REF_RE, md, relocator),
        }
        for pattern, instance in recorded_patterns.iteritems():
            md.inlinePatterns[pattern] = instance
        output = md.convert(body)
        meta = ext.get_requisites()
        meta['local_references'] = relocator.resources
        return output, meta


class HtmlBodyGenerator(BodyGenerator):
    """Generator for generating body content from HTML payload.
    """

    def generate(self, body, **options):
        """Override to generate content from Markdown payload.

        :param body: payload content.
        :type body: str
        :return: a tuple of two elements, generated body and metadata
            dictionary, respectively.
        :rtype: tuple
        """
        return body, {}


_GENERATOR_EXTENSIONS = {
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.html': 'html',
    '.htm': 'html'
}

_BODY_GENERATORS = {
    'markdown': MarkdownBodyGenerator.__name__,
    'html': HtmlBodyGenerator.__name__
}


SUPPORTED_GENERATOR_EXTENSIONS = _GENERATOR_EXTENSIONS.keys()

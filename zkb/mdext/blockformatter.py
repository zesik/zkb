# -*- coding: utf-8 -*-
"""
zkb.mdext.blockformatter
~~~~~~~~~~~~~~~~~~~~~~~~

HTML formatter for customizing code blocks in Markdown source.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import re

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension


#: Regular expression for matching blocks, also used for extracting block type
#   and header.
_BLOCK_HEADER = re.compile(r'''
    (?:^::+)                        # 2 or more colons
    (?P<type>[\w+-]*)               # The language
    \s*                             # Arbitrary whitespace
    (?P<header>.*)                  # Header configurations
    ''', re.VERBOSE)

#: Name of CSS class that is used for code blocks.
CODE_HIGHLIGHT_CLASS = 'code-highlight'


class BlockHtmlFormatter(object):
    """Base class of block formatter that customizing Markdown code block to
    HTML format.

    A block is an extension of Markdown code block. If first line of a code
    block starts with ``::`` (double colon), the code block is recognized as a
    *block* and will be processed with corresponding block formatter.

    Block comes with different types, and type of block is specified after
    ``::``. For example, a LaTeX block may start with ``::latex``. Type of the
    block can be registered with a dictionary (key is type, value is block
    formatter subclass instance) when initializing
    :class:`BlockHtmlFormatterExtension`. If type of a block is not registered,
    the block will not be processed with any formatter.

    Each block can also have a header which comes after a block type for
    specifying settings of this block. Header will be passed to :func:`format`
    method when formatting the block.
    """

    def __init__(self):
        super(BlockHtmlFormatter, self).__init__()

    def get_tag(self):
        """Returns the tag the block formatter should yield.

        :return: HTML tag of the formatted block.
        :rtype: str
        """
        pass

    def format(self, header, block):
        """Formats the block.

        :param header: block header.
        :type header: str
        :param block: block content.
        :type block: str
        :return: formatted HTML content of the block.
        :rtype: str
        """
        pass

    def get_requisites(self):
        """Get additional required contents to be inserted into the HTML page,
        such as scripts and CSS definitions.

        :return: a dictionary of additional data to be inserted.
        :rtype: dict
        """
        pass


class BlockHtmlFormatterTreeprocessor(Treeprocessor):
    """HTML block formatter tree processor for Python markdown extension.

    :param md: markdown instance.
    :param formatters: block formatters.
    :type formatters: dict
    """

    def __init__(self, md, formatters):
        super(BlockHtmlFormatterTreeprocessor, self).__init__(md)
        self.formatters = formatters

    def run(self, root):
        """Override base class's method to find, format blocks and update the
        htmlStash.
        """
        blocks = root.getiterator('pre')
        for block in blocks:
            children = block.getchildren()
            if len(children) == 1 and children[0].tag == 'code':
                lines = children[0].text.rstrip('\n').split('\n')
                if len(lines) > 1:
                    h = _BLOCK_HEADER.search(lines[0])
                    if h is not None:
                        block_type = h.group('type')
                        header = h.group('header')
                        if block_type in self.formatters:
                            formatter = self.formatters[block_type]
                            result = formatter.format(header,
                                                      '\n'.join(lines[1:]))
                            if result is not None:
                                placeholder = self.markdown.htmlStash.store(
                                    result, safe=True)
                                block.clear()
                                block.tag = formatter.get_tag()
                                block.text = placeholder
                                continue
                # This block is a code block, but we could not highlight it
                placeholder = '\n'.join(lines)
                block.clear()
                block.text = '<pre><code>' + placeholder + '</code></pre>'
                block.tag = 'figure'
                block.set('class', '%s' % CODE_HIGHLIGHT_CLASS)


class BlockHtmlFormatterExtension(Extension):
    """Extension of Python Markdown for formatting HTML blocks.

    :param formatters: formatters to register. Key is block type, and value is
        subclass of BlockHtmlFormatter. When find a block of type that exists
        in this dictionary, corresponding instance will be used to format the
        block.
    :type formatters: dict
    """

    def __init__(self, formatters):
        super(BlockHtmlFormatterExtension, self).__init__({})
        filtered = {}
        for key in formatters:
            value = formatters[key]
            if isinstance(value, BlockHtmlFormatter):
                filtered[key] = value
        self.formatters = filtered

    def extendMarkdown(self, md, md_globals):
        """Overriding method for extending Python Markdown.
        """
        formatter = BlockHtmlFormatterTreeprocessor(md, self.formatters)
        md.treeprocessors.add('blockformatter', formatter, '<inline')
        md.registerExtension(self)

    def get_requisites(self):
        """Get the requisites for all formatters.

        :return: Requisites for all formatters.
        :rtype: dict
        """
        requisites = {}
        for _, formatter in self.formatters.iteritems():
            current_requisites = formatter.get_requisites()
            if not current_requisites:
                continue
            for key, req in current_requisites.iteritems():
                if key not in requisites:
                    requisites[key] = []
                requisites[key].extend(req)
        return requisites

# -*- coding: utf-8 -*-
"""
zkb.mdext.codeblock
~~~~~~~~~~~~~~~~~~~

HTML formatter for customizing code blocks in Markdown source.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
:Acknowledgement:
    Part of code in this file derived from Pygments project,
    licensed under BSD.

    Copyright 2006-2013 by the Pygments team.
"""

import re
import StringIO

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.special import TextLexer
from pygments.formatters.html import HtmlFormatter

from zkb.mdext.blockformatter import BlockHtmlFormatter


#: Regular expression for matching code block headers, also used for extracting
# source code language and other formatting options.
_HEADER_PATTERN = re.compile(r'''
    (lang:(?P<lang>[\w+-]+))?           # Optional language
    \s*                                 # Arbitrary whitespace
    (start:(?P<start>[0-9]+))?          # Optional line start number
    \s*
    (mark:(?P<mark>[0-9]+(-[0-9]+)?(,[0-9]+(-[0-9]+)?)*))?  # Optional marking
    \s*
    (linenos:(?P<linenos>true|false))?  # Optional show/hide line no. setting.
    ''', re.VERBOSE)


class CodeBlockPygmentsHtmlFormatter(HtmlFormatter):
    """Extension of Pygments HTML formatter for custom formatting of the code.

    Many methods are overridden to modify class name and enhance highlight
    behavior.
    """

    def __init__(self, **options):
        super(CodeBlockPygmentsHtmlFormatter, self).__init__(**options)
        self.noclasses = False  # Force using a class in our implementation

    def _get_highlight_class(self, lineno):
        if lineno in self.hl_lines:
            extra = ' marked'
            if lineno - 1 not in self.hl_lines:
                # This line starts a highlight
                extra += ' start'
            if lineno + 1 not in self.hl_lines:
                # This line ends a highlight
                extra += ' end'
        else:
            extra = ''
        return extra

    def _highlight_lines(self, tokensource):
        """Highlighted the lines specified in the `hl_lines` option by
        post-processing the token stream coming from `_format_lines`.
        """
        for i, (t, value) in enumerate(tokensource):
            if t != 1:
                yield t, value
            yield 1, ('<div class="line%s">%s</div>' %
                      (self._get_highlight_class(i + self.linenostart), value))

    def _wrap_tablelinenos(self, inner):
        dummyoutfile = StringIO.StringIO()
        lncount = 0
        for t, line in inner:
            if t:
                lncount += 1
            dummyoutfile.write(line)

        fl = self.linenostart
        mw = len(str(lncount + fl - 1))
        sp = self.linenospecial
        st = self.linenostep
        la = self.lineanchors
        aln = self.anchorlinenos
        if sp:
            lines = []
            for i in range(fl, fl + lncount):
                hl = self._get_highlight_class(i)
                if i % st == 0:
                    if i % sp == 0:
                        if aln:
                            lines.append('<div class="line-number special%s">'
                                         '<a href="#%s-%d">%*d</a>\n'
                                         '</div>' % (hl, la, i, mw, i))
                        else:
                            lines.append('<div class="line-number special%s">'
                                         '%*d\n</div>' % (hl, mw, i))
                    else:
                        if aln:
                            lines.append('<div class="line-number%s">'
                                         '<a href="#%s-%d">%*d</a>\n'
                                         '</div>' % (hl, la, i, mw, i))
                        else:
                            lines.append('<div class="line-number%s">'
                                         '%*d\n</div>' % (hl, mw, i))
                else:
                    lines.append('<div class="line-number%s">\n</div>' % hl)
            ls = ''.join(lines)
        else:
            lines = []
            for i in range(fl, fl + lncount):
                hl = self._get_highlight_class(i)
                if i % st == 0:
                    if aln:
                        lines.append('<div class="line-number%s">'
                                     '<a href="#%s-%d">%*d</a>\n'
                                     '</div>' % (hl, la, i, mw, i))
                    else:
                        lines.append('<div class="line-number%s">%*d\n'
                                     '</div>' % (hl, mw, i))
                else:
                    lines.append('<div class="line-number%s">\n</div>' % hl)
            ls = ''.join(lines)

        # in case you wonder about the seemingly redundant <div> here: since
        # the content in the other cell also is wrapped in a div, some browsers
        # in some configurations seem to mess up the formatting...
        yield 0, ('<figure class="%s"><table>' % self.cssclass +
                  '<tr><td class="line-numbers"><div><pre>' +
                  ls + '</pre></div></td><td class="code">')
        yield 0, dummyoutfile.getvalue()
        yield 0, '</td></tr></table></figure>'

    def _wrap_div(self, inner):
        yield 0, ('<div>')
        for tup in inner:
            yield tup
        yield 0, '</div>\n'

    def _wrap_figure(self, inner):
        yield 0, ('<figure class="%s">' % self.cssclass)
        for tup in inner:
            yield tup
        yield 0, '</figure>\n'

    def format_unencoded(self, tokensource, outfile):
        source = self._format_lines(tokensource)
        if self.hl_lines:
            source = self._highlight_lines(source)
        if not self.nowrap:
            if self.linenos == 2:
                source = self._wrap_inlinelinenos(source)
            if self.lineanchors:
                source = self._wrap_lineanchors(source)
            if self.linespans:
                source = self._wrap_linespans(source)
            source = self.wrap(source, outfile)
            if self.linenos == 1:
                source = self._wrap_tablelinenos(source)
            elif self.linenos == 0:
                source = self._wrap_figure(source)
            if self.full:
                source = self._wrap_full(source, outfile)

        for t, piece in source:
            outfile.write(piece)


class CodeBlockHtmlFormatter(BlockHtmlFormatter):
    """HTML formatter for formatting LaTeX code blocks.

    :param linenos: True if line number should be added by default. This value
        will be overridden by value specified in block header.
    :type linenos: bool
    :param guess_lang: True if language of source code should be guessed when
        no language specified in block header.
    :type guess_lang: bool
    :param css_class: CSS class name of code blocks.
    :type css_class: str
    """

    def __init__(self, linenos=True, guess_lang=False, css_class="codeblock"):
        super(CodeBlockHtmlFormatter, self).__init__()
        self.linenos = linenos
        self.guess_lang = guess_lang
        self.css_class = css_class

    def get_tag(self):
        return "p"

    def format(self, header, block):
        lang, line_start, hl_lines, linenos = self._parse_header(header)
        lexer = None
        try:
            lexer = get_lexer_by_name(lang)
        except ValueError:
            try:
                if self.guess_lang:
                    lexer = guess_lexer(block)
            except ValueError:
                pass
        if lexer is None:
            lexer = TextLexer()
        formatter = CodeBlockPygmentsHtmlFormatter(linenos=linenos,
                                                   cssclass=self.css_class,
                                                   hl_lines=hl_lines,
                                                   linenostart=line_start)
        return highlight(block, lexer, formatter)

    def get_requisites(self):
        return None

    def _parse_header(self, header):
        """Parse the header of a code block to get settings for current block.

        Format of a header is:
        ``[lang:language] [start:#] [mark:#,#-#] [linenos:false]``

        - ``lang:language``: specify the language of the source code.
        - ``start:#``: specify the line number of the first line in the code
          block.
        - ``mark:#,#-#``: specify lines that should be highlighted. You can
          specify with either a single line or lines in a range.
        - ``linenos:false``: specify this if you do not want to show line
          numbers.

        :param header: header of the block.
        :type header: str
        :return: A tuple of four elements, respectively these are:

            - a string indicating the language of the code block;
            - a integer indicating the initial line number;
            - a list of integers indicating lines which should be highlighted;
            - a bool indicating whether the line number should be displayed.
        :rtype: tuple
        """
        m = _HEADER_PATTERN.search(header)
        language = ''
        line_start = 1
        hl_lines = []
        linenos = self.linenos
        if m:
            if m.group('lang'):
                language = m.group('lang').lower()
            if m.group('start'):
                try:
                    line_start = int(m.group('start'))
                except ValueError:
                    pass
            if m.group('mark'):
                marks = set()
                for item in m.group('mark').split(','):
                    try:
                        entry = item.split('-')
                        if len(entry) == 1:
                            marks.add(int(entry[0]))
                        elif len(entry) == 2:
                            marks |= set(range(int(entry[0]),
                                               int(entry[1]) + 1))
                    except ValueError:
                        pass
                hl_lines = list(marks)
            if m.group('linenos'):
                if m.group('linenos') == 'true':
                    linenos = True
                else:
                    linenos = False
        return language, line_start, hl_lines, linenos

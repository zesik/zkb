# -*- coding: utf-8 -*-
"""
test.test_code_formatter
~~~~~~~~~~~~~~~~~~~~~~~~

This is the unit test file for source code formatter.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import unittest

import markdown

from zkb.mdext import BlockHtmlFormatterExtension
from zkb.mdext import CodeBlockHtmlFormatter


class TestCodeFormatter(unittest.TestCase):
    def _create_extension(self):
        return BlockHtmlFormatterExtension({
            'code': CodeBlockHtmlFormatter()
        })

    def test_code_formatting(self):
        body = ('Test basic code block\n\n'
                '    ::code\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><table><tr>'
                          '<td class="line-numbers"><div><pre>'
                          '<div class="line-number">1\n'
                          '</div><div class="line-number">2\n'
                          '</div><div class="line-number">3\n'
                          '</div><div class="line-number">4\n'
                          '</div><div class="line-number">5\n'
                          '</div><div class="line-number">6\n'
                          '</div></pre></div></td><td class="code"><div><pre>'
                          'class TestCodeFormatter(unittest.TestCase):\n\n'
                          '    def _create_extension(self):\n'
                          '        return BlockHtmlFormatterExtension({\n    '
                          '        &#39;code&#39;: CodeBlockHtmlFormatter()\n'
                          '        })\n'
                          '</pre></div>\n'
                          '</td></tr></table></figure>'),
                         'source code output not match.')

    def test_code_formatting_nolineno(self):
        body = ('Test basic code block\n\n'
                '    ::code linenos:false\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><div><pre>'
                          'class TestCodeFormatter(unittest.TestCase):\n'
                          '\n'
                          '    def _create_extension(self):\n'
                          '        return BlockHtmlFormatterExtension({\n '
                          '           &#39;code&#39;: CodeBlockHtmlFormatter()'
                          '\n        })\n'
                          '</pre></div>\n</figure>'),
                         'source code output not match.')

    def test_code_formatting_lang(self):
        body = ('Test basic code block\n\n'
                '    ::code lang:python\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])

        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><table>'
                          '<tr><td class="line-numbers"><div>'
                          '<pre><div class="line-number">1\n'
                          '</div><div class="line-number">2\n'
                          '</div><div class="line-number">3\n'
                          '</div><div class="line-number">4\n'
                          '</div><div class="line-number">5\n'
                          '</div><div class="line-number">6\n'
                          '</div></pre></div></td><td class="code"><div><pre>'
                          '<span class="k">class</span> '
                          '<span class="nc">TestCodeFormatter</span>'
                          '<span class="p">(</span>'
                          '<span class="n">unittest</span>'
                          '<span class="o">.</span>'
                          '<span class="n">TestCase</span>'
                          '<span class="p">):</span>\n\n'
                          '    <span class="k">def</span> '
                          '<span class="nf">_create_extension</span>'
                          '<span class="p">(</span>'
                          '<span class="bp">self</span>'
                          '<span class="p">):</span>\n'
                          '        <span class="k">return</span> '
                          '<span class="n">BlockHtmlFormatterExtension</span>'
                          '<span class="p">({</span>\n'
                          '            <span class="s">&#39;code&#39;</span>'
                          '<span class="p">:</span> '
                          '<span class="n">CodeBlockHtmlFormatter</span>'
                          '<span class="p">()</span>\n'
                          '        <span class="p">})</span>\n'
                          '</pre></div>\n'
                          '</td></tr></table></figure>'),
                         'source code output not match.')

    def test_code_formatting_lang_nolinenos(self):
        body = ('Test basic code block\n\n'
                '    ::code lang:python linenos:false\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><div><pre>'
                          '<span class="k">class</span> '
                          '<span class="nc">TestCodeFormatter</span>'
                          '<span class="p">(</span>'
                          '<span class="n">unittest</span>'
                          '<span class="o">.</span>'
                          '<span class="n">TestCase</span>'
                          '<span class="p">):</span>\n\n'
                          '    <span class="k">def</span> '
                          '<span class="nf">_create_extension</span>'
                          '<span class="p">(</span>'
                          '<span class="bp">self</span>'
                          '<span class="p">):</span>\n'
                          '        <span class="k">return</span> '
                          '<span class="n">BlockHtmlFormatterExtension</span>'
                          '<span class="p">({</span>\n'
                          '            <span class="s">&#39;code&#39;</span>'
                          '<span class="p">:</span> '
                          '<span class="n">CodeBlockHtmlFormatter</span>'
                          '<span class="p">()</span>\n'
                          '        <span class="p">})</span>\n'
                          '</pre></div>\n'
                          '</figure>'),
                         'source code output not match.')

    def test_code_formatting_lang_linestart(self):
        body = ('Test basic code block\n\n'
                '    ::code lang:python start:30\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><table><tr>'
                          '<td class="line-numbers"><div><pre>'
                          '<div class="line-number">30\n'
                          '</div><div class="line-number">31\n'
                          '</div><div class="line-number">32\n'
                          '</div><div class="line-number">33\n'
                          '</div><div class="line-number">34\n'
                          '</div><div class="line-number">35\n'
                          '</div></pre></div></td><td class="code">'
                          '<div><pre>'
                          '<span class="k">class</span> <span class="nc">'
                          'TestCodeFormatter</span><span class="p">'
                          '(</span><span class="n">unittest</span>'
                          '<span class="o">.</span>'
                          '<span class="n">TestCase</span>'
                          '<span class="p">):</span>\n'
                          '\n'
                          '    <span class="k">def</span> '
                          '<span class="nf">_create_extension</span>'
                          '<span class="p">(</span>'
                          '<span class="bp">self</span>'
                          '<span class="p">):</span>\n'
                          '        <span class="k">return</span> '
                          '<span class="n">BlockHtmlFormatterExtension</span>'
                          '<span class="p">({</span>\n'
                          '            <span class="s">&#39;code&#39;</span>'
                          '<span class="p">:</span> '
                          '<span class="n">CodeBlockHtmlFormatter</span>'
                          '<span class="p">()</span>\n'
                          '        <span class="p">})</span>\n'
                          '</pre></div>\n'
                          '</td></tr></table></figure>'),
                         'source code output not match.')

    def test_code_formatting_lang_linestart_mark(self):
        body = ('Test basic code block\n\n'
                '    ::code lang:python start:30 mark:32,34-36\n'
                '    import unittest\n\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><table><tr>'
                          '<td class="line-numbers"><div>'
                          '<pre><div class="line-number">30\n'
                          '</div><div class="line-number">31\n'
                          '</div><div class="line-number marked start end">32'
                          '\n</div><div class="line-number">33\n'
                          '</div><div class="line-number marked start">34\n'
                          '</div><div class="line-number marked">35\n'
                          '</div><div class="line-number marked end">36\n'
                          '</div><div class="line-number">37\n'
                          '</div></pre></div></td><td class="code"><div><pre>'
                          '<div class="line"><span class="kn">import</span> '
                          '<span class="nn">unittest</span>\n'
                          '</div><div class="line">\n'
                          '</div><div class="line marked start end">'
                          '<span class="k">class</span> '
                          '<span class="nc">TestCodeFormatter</span>'
                          '<span class="p">(</span>'
                          '<span class="n">unittest</span>'
                          '<span class="o">.</span>'
                          '<span class="n">TestCase</span>'
                          '<span class="p">):</span>\n'
                          '</div><div class="line">\n'
                          '</div><div class="line marked start">'
                          '    <span class="k">def</span>'
                          ' <span class="nf">_create_extension</span>'
                          '<span class="p">(</span>'
                          '<span class="bp">self</span>'
                          '<span class="p">):</span>\n'
                          '</div><div class="line marked">'
                          '        <span class="k">return</span>'
                          ' <span class="n">BlockHtmlFormatterExtension</span>'
                          '<span class="p">({</span>\n'
                          '</div><div class="line marked end">'
                          '            <span class="s">&#39;code&#39;</span>'
                          '<span class="p">:</span>'
                          ' <span class="n">CodeBlockHtmlFormatter</span>'
                          '<span class="p">()</span>\n'
                          '</div><div class="line">'
                          '        <span class="p">})</span>\n'
                          '</div></pre></div>\n'
                          '</td></tr></table></figure>'),
                         'source code output not match.')

    def test_code_formatting_lang_linestart_mark_nolinenos(self):
        body = ('Test basic code block\n\n'
                '    ::code lang:python start:30 mark:32,34-36 linenos:false\n'
                '    import unittest\n\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="codeblock"><div><pre>'
                          '<div class="line"><span class="kn">import</span> '
                          '<span class="nn">unittest</span>\n'
                          '</div><div class="line">\n'
                          '</div><div class="line marked start end">'
                          '<span class="k">class</span> '
                          '<span class="nc">TestCodeFormatter</span>'
                          '<span class="p">(</span>'
                          '<span class="n">unittest</span>'
                          '<span class="o">.</span>'
                          '<span class="n">TestCase</span>'
                          '<span class="p">):</span>\n'
                          '</div><div class="line">\n'
                          '</div><div class="line marked start">'
                          '    <span class="k">def</span> '
                          '<span class="nf">_create_extension</span>'
                          '<span class="p">(</span>'
                          '<span class="bp">self</span>'
                          '<span class="p">):</span>\n'
                          '</div><div class="line marked">'
                          '        <span class="k">return</span> '
                          '<span class="n">BlockHtmlFormatterExtension</span>'
                          '<span class="p">({</span>\n'
                          '</div><div class="line marked end">'
                          '            <span class="s">&#39;code&#39;</span>'
                          '<span class="p">:</span> '
                          '<span class="n">CodeBlockHtmlFormatter</span>'
                          '<span class="p">()</span>\n'
                          '</div><div class="line">'
                          '        <span class="p">})</span>\n'
                          '</div></pre></div>\n'
                          '</figure>'),
                         'source code output not match.')

    def test_unformatted_code(self):
        body = ('Test basic code block\n\n'
                '    class TestCodeFormatter(unittest.TestCase):\n\n'
                '        def _create_extension(self):\n'
                '            return BlockHtmlFormatterExtension({\n'
                '                \'code\': CodeBlockHtmlFormatter()\n'
                '            })')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test basic code block</p>\n'
                          '<figure class="code-highlight"><pre>'
                          '<code>class TestCodeFormatter(unittest.TestCase):\n'
                          '\n    def _create_extension(self):\n'
                          '        return BlockHtmlFormatterExtension({\n'
                          '            \'code\': CodeBlockHtmlFormatter()\n'
                          '        })</code></pre></figure>'),
                         'source code output not match.')

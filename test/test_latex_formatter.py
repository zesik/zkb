# -*- coding: utf-8 -*-
"""
test.test_latex_formatter
~~~~~~~~~~~~~~~~~~~~~~~~~

This is the unit test file for LaTeX formatter.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import unittest

import markdown

from zkb.mdext import BlockHtmlFormatterExtension
from zkb.mdext import LatexBlockHtmlFormatter


class TestLatexFormatter(unittest.TestCase):
    def _create_extension(self):
        return BlockHtmlFormatterExtension({
            'latex': LatexBlockHtmlFormatter()
        })

    def test_latex_formatting(self):
        body = ('Test LaTeX block\n\n'
                '    ::latex\n'
                '    \\begin{aligned}'
                '\\dot{x} & = \\sigma(y-x) \\\\'
                '\\dot{y} & = \\rho x - y - xz \\\\'
                '\\dot{z} & = -\\beta z + xy'
                '\\end{aligned}')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         ('<p>Test LaTeX block</p>\n'
                          '<p>\\[\\begin{aligned}'
                          '\\dot{x} & = \\sigma(y-x) \\\\'
                          '\\dot{y} & = \\rho x - y - xz \\\\'
                          '\\dot{z} & = -\\beta z + xy'
                          '\\end{aligned}\\]</p>'),
                         'latex output not match.')

    def test_inline_latex_formatting(self):
        body = 'Test inline $$\\LaTeX$$ block'
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         '<p>Test inline $$\\LaTeX$$ block</p>',
                         'latex output not match.')

    def test_latex_formatting_unicode(self):
        body = (u'测试 LaTeX 格式化\n\n'
                u'    ::latex\n'
                u'    \\begin{aligned}'
                u'\\dot{x} & = \\sigma(y-x) \\\\'
                u'\\dot{y} & = \\rho x - y - xz \\\\'
                u'\\dot{z} & = -\\beta z + xy'
                u'\\end{aligned}')
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[self._create_extension()])
        self.assertEqual(result,
                         (u'<p>测试 LaTeX 格式化</p>\n'
                          u'<p>\\[\\begin{aligned}'
                          u'\\dot{x} & = \\sigma(y-x) \\\\'
                          u'\\dot{y} & = \\rho x - y - xz \\\\'
                          u'\\dot{z} & = -\\beta z + xy'
                          u'\\end{aligned}\\]</p>'),
                         'latex output not match.')

    def test_no_requisites(self):
        body = 'Test no latex'
        ext = self._create_extension()
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[ext])
        self.assertEqual(result,
                         '<p>Test no latex</p>',
                         'latex output not match')
        self.assertIsNotNone(ext.get_requisites())
        self.assertEqual(len(ext.get_requisites()), 0, 'requisites not match')

    def test_has_requisites(self):
        body = ('Test LaTeX block\n\n'
                '    ::latex\n'
                '    \\begin{aligned}'
                '\\dot{x} & = \\sigma(y-x) \\\\'
                '\\dot{y} & = \\rho x - y - xz \\\\'
                '\\dot{z} & = -\\beta z + xy'
                '\\end{aligned}')
        ext = self._create_extension()
        result = markdown.markdown(body,
                                   output_format='html5',
                                   extensions=[ext])
        self.assertEqual(result,
                         ('<p>Test LaTeX block</p>\n'
                          '<p>\\[\\begin{aligned}'
                          '\\dot{x} & = \\sigma(y-x) \\\\'
                          '\\dot{y} & = \\rho x - y - xz \\\\'
                          '\\dot{z} & = -\\beta z + xy'
                          '\\end{aligned}\\]</p>'),
                         'latex output not match.')
        self.assertIsNotNone(ext.get_requisites())
        self.assertEqual(len(ext.get_requisites()), 1, 'requisites not match')
        self.assertEqual(len(ext.get_requisites()['header_scripts']), 2,
                         'requisites not match')

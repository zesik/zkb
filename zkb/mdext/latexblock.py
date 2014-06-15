# -*- coding: utf-8 -*-
"""
zkb.mdext.latexblock
~~~~~~~~~~~~~~~~~~~~

HTML formatter for customizing LaTeX code blocks in Markdown source.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

from zkb.mdext.blockformatter import BlockHtmlFormatter


class LatexBlockHtmlFormatter(BlockHtmlFormatter):
    """HTML formatter for formatting LaTeX code blocks.
    """

    def __init__(self):
        super(LatexBlockHtmlFormatter, self).__init__()
        self.active = False

    def get_tag(self):
        return 'p'

    def format(self, header, block):
        self.active = True
        return '\\[' + block + '\\]'

    def get_requisites(self):
        if not self.active:
            return None
        return {
            'header_scripts': [
                '<script type="text/x-mathjax-config">MathJax.Hub.Config({'
                'tex2jax: {inlineMath: [["$$","$$"]], '
                'displayMath: [["\\\\[", "\\\\]"]], preview: []}'
                '});</script>',
                '<script type="text/javascript" '
                'src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?'
                'config=TeX-AMS-MML_HTMLorMML"></script>'
            ]
        }
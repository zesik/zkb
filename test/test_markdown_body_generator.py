# -*- coding: utf-8 -*-
"""
test.test_markdown_body_generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the unit test file for Markdown.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import sys
import os
import unittest
import hashlib

from zkb.bodygenerators import MarkdownBodyGenerator


class TestMarkdownBodyGenerator(unittest.TestCase):
    def get_relocator(self):
        from zkb.bodygenerators import ResourceRelocator
        from zkb.bodygenerators import _REMOTE_LINK_PATTERN

        class Relocator(ResourceRelocator):
            def _should_relocate(self, filename):
                return not _REMOTE_LINK_PATTERN.match(filename)

            def _get_hash(self, filename):
                m = hashlib.sha1()
                m.update(filename)
                return m.hexdigest()

        return Relocator(self.get_base_path())

    def get_base_path(self):
        if sys.platform == 'win32':
            return 'C:\\Test_input\\article'
        else:
            return '/home/test/input/article'

    def get_filenames(self):
        if sys.platform == 'win32':
            return ('files\\sample.zip',
                    'files\\image.png',
                    'C:\\files\\sample2.zip',
                    'C:\\Test_input\\article\\files\\sample.zip')
        else:
            return ('files/sample.zip',
                    'files/image.png',
                    '/files/sample2.zip',
                    '/home/test/input/article/files/sample.zip')

    def get_hash(self):
        return tuple([
            hashlib.sha1(os.path.join(self.get_base_path(), x)).hexdigest()
            for x in self.get_filenames()])

    def test_external_inline_link(self):
        gen = MarkdownBodyGenerator()
        result, req = gen.generate('An [example link](http://example.com/)',
                                   relocator=self.get_relocator())
        self.assertEqual(result,
                         '<p>An <a href="http://example.com/">example link'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 0,
                         'local ref incorrect.')

    def test_external_inline_image_link(self):
        gen = MarkdownBodyGenerator()
        result, req = gen.generate('An ![example image]'
                                   '(http://example.com/image.png)',
                                   relocator=self.get_relocator())
        self.assertEqual(result,
                         '<p>An <img alt="example image" '
                         'src="http://example.com/image.png"></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 0,
                         'local ref incorrect.')

    def test_external_ref_link(self):
        gen = MarkdownBodyGenerator()
        result, req = gen.generate('An [example link][1]\n\n'
                                   '[1]: http://example.com/',
                                   relocator=self.get_relocator())
        self.assertEqual(result,
                         '<p>An <a href="http://example.com/">example link'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 0,
                         'local ref incorrect.')

    def test_external_ref_image(self):
        gen = MarkdownBodyGenerator()
        result, req = gen.generate('An ![example image][1]\n\n'
                                   '[1]: http://example.com/image.png',
                                   relocator=self.get_relocator())
        self.assertEqual(result,
                         '<p>An <img alt="example image" '
                         'src="http://example.com/image.png"></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 0,
                         'local ref incorrect.')

    def test_external_short_ref_link(self):
        gen = MarkdownBodyGenerator()
        result, req = gen.generate('An [example link]\n\n'
                                   '[example link]: http://example.com/',
                                   relocator=self.get_relocator())
        self.assertEqual(result,
                         '<p>An <a href="http://example.com/">example link'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 0,
                         'local ref incorrect.')

    def test_local_inline_link(self):
        gen = MarkdownBodyGenerator()
        filename, _, _, _ = self.get_filenames()
        digest, _, _, _ = self.get_hash()
        relocator = self.get_relocator()
        abs_infile = os.path.join(relocator.base_dir, filename)
        out = ['resources', digest[0:2], digest[2:4], digest[4:], 'sample.zip']
        result, req = gen.generate('An [local file link](' + filename + ')',
                                   relocator=relocator)
        self.assertEqual(result,
                         '<p>An <a href="/' + '/'.join(out) +
                         '">local file link'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 1,
                         'local ref incorrect.')
        self.assertEqual(req['local_references'][abs_infile],
                         out, 'local ref incorrect.')

    def test_local_inline_image_link(self):
        gen = MarkdownBodyGenerator()
        _, filename, _, _ = self.get_filenames()
        _, digest, _, _ = self.get_hash()
        relocator = self.get_relocator()
        abs_infile = os.path.join(relocator.base_dir, filename)
        out = ['resources', digest[0:2], digest[2:4], digest[4:], 'image.png']
        result, req = gen.generate('An ![local image](' + filename + ')',
                                   relocator=relocator)
        self.assertEqual(result,
                         '<p>An <img alt="local image" '
                         'src="/' + '/'.join(out) + '"></p>',
                         'markdown output mismatch')
        self.assertEqual(req['local_references'][abs_infile],
                         out, 'local ref incorrect.')

    def test_local_ref_link(self):
        gen = MarkdownBodyGenerator()
        filename, _, _, _ = self.get_filenames()
        digest, _, _, _ = self.get_hash()
        relocator = self.get_relocator()
        abs_infile = os.path.join(relocator.base_dir, filename)
        out = ['resources', digest[0:2], digest[2:4], digest[4:], 'sample.zip']
        result, req = gen.generate('An [local file link][1]\n\n'
                                   '[1]: ' + filename,
                                   relocator=relocator)
        self.assertEqual(result,
                         '<p>An <a href="/' + '/'.join(out) +
                         '">local file link'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 1,
                         'local ref incorrect.')
        self.assertEqual(req['local_references'][abs_infile],
                         out, 'local ref incorrect.')

    def test_local_ref_image_link(self):
        gen = MarkdownBodyGenerator()
        _, filename, _, _ = self.get_filenames()
        _, digest, _, _ = self.get_hash()
        relocator = self.get_relocator()
        abs_infile = os.path.join(relocator.base_dir, filename)
        out = ['resources', digest[0:2], digest[2:4], digest[4:], 'image.png']
        result, req = gen.generate('An ![local image][1]\n\n'
                                   '[1]: ' + filename,
                                   relocator=relocator)
        self.assertEqual(result,
                         '<p>An <img alt="local image" '
                         'src="/' + '/'.join(out) + '"></p>',
                         'markdown output mismatch')
        self.assertEqual(req['local_references'][abs_infile],
                         out, 'local ref incorrect.')

    def test_local_short_ref_link(self):
        gen = MarkdownBodyGenerator()
        filename, _, _, _ = self.get_filenames()
        digest, _, _, _ = self.get_hash()
        relocator = self.get_relocator()
        abs_infile = os.path.join(relocator.base_dir, filename)
        out = ['resources', digest[0:2], digest[2:4], digest[4:], 'sample.zip']
        result, req = gen.generate('An [local file link]\n\n'
                                   '[local file link]: ' + filename,
                                   relocator=relocator)
        self.assertEqual(result,
                         '<p>An <a href="/' + '/'.join(out) +
                         '">local file link'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 1,
                         'local ref incorrect.')
        self.assertEqual(req['local_references'][abs_infile],
                         out, 'local ref incorrect.')

    def test_multiple_local_ref_link(self):
        gen = MarkdownBodyGenerator()
        relocator = self.get_relocator()
        file1, _, file2, file3 = self.get_filenames()
        digest1, _, digest2, digest3 = self.get_hash()
        abs_infile1 = os.path.join(relocator.base_dir, file1)
        abs_infile2 = os.path.join(relocator.base_dir, file2)
        out1 = ['resources', digest1[0:2], digest1[2:4], digest1[4:],
                'sample.zip']
        out2 = ['resources', digest2[0:2], digest2[2:4], digest2[4:],
                'sample2.zip']
        out3 = ['resources', digest3[0:2], digest3[2:4], digest3[4:],
                'sample.zip']
        result, req = gen.generate('An [local file link](' + file1 + ')\n\n' +
                                   'Another [file](' + file2 + ')\n\n' +
                                   'Same [file](' + file1 + ')\n\n' +
                                   'Same [filename](' + file3 + ')',
                                   relocator=relocator)
        self.assertEqual(result,
                         '<p>An <a href="/' + '/'.join(out1) +
                         '">local file link'
                         '</a></p>\n'
                         '<p>Another <a href="/' + '/'.join(out2) +
                         '">file'
                         '</a></p>\n'
                         '<p>Same <a href="/' + '/'.join(out1) +
                         '">file'
                         '</a></p>\n'
                         '<p>Same <a href="/' + '/'.join(out3) +
                         '">filename'
                         '</a></p>',
                         'markdown output mismatch')
        self.assertEqual(len(req['local_references']), 2,
                         'local ref incorrect.')
        self.assertEqual(req['local_references'][abs_infile1],
                         out1, 'local ref incorrect.')
        self.assertEqual(req['local_references'][abs_infile2],
                         out2, 'local ref incorrect.')

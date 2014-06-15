# -*- coding: utf-8 -*-
"""
run-tests.py
~~~~~~~~~~~~

This is the script for running all tests of ZKB.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import unittest

if __name__ == '__main__':
    all_tests = unittest.TestLoader().discover('test', pattern='*.py')
    unittest.TextTestRunner().run(all_tests)

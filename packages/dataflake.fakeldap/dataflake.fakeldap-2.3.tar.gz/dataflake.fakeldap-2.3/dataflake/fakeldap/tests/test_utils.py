# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import six
import unittest


class HashPwdTests(unittest.TestCase):

    def test_hash_pwd(self):
        from dataflake.fakeldap.utils import hash_pwd
        pwd = hash_pwd('secret')
        self.assertTrue(isinstance(pwd, six.binary_type))
        self.assertTrue(pwd.startswith(b'{SHA}'))

    def test_hash_unicode_pwd(self):
        from dataflake.fakeldap.utils import hash_pwd
        pwd = hash_pwd(u'bjørn')
        self.assertTrue(isinstance(pwd, six.binary_type))
        self.assertTrue(pwd.startswith(b'{SHA}'))


class ConstraintUtilTests(unittest.TestCase):

    def test_to_utf8(self):
        from dataflake.fakeldap.utils import utf8_string

        @utf8_string('test')
        def _fn_with_opt_args(test='string'):
            return True

        self.assertTrue(_fn_with_opt_args())

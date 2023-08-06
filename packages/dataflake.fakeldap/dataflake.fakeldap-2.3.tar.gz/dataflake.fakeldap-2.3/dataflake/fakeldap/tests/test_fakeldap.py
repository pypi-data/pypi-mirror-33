##############################################################################
#
# Copyright (c) 2008-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from dataflake.fakeldap.tests.base import FakeLDAPTests


class FakeLDAPBasicTests(FakeLDAPTests):

    def test_defaults(self):
        conn = self._makeOne()
        self.assertFalse(conn.start_tls_called)
        self.assertFalse(conn.args)
        self.assertFalse(conn.kwargs)
        self.assertFalse(conn.options)
        self.assertFalse(conn._last_bind)

    def test_saving_args(self):
        conn = self._makeOne('arg1', 'arg2', arg3='foo', arg4='bar')
        self.assertEqual(conn.args, ('arg1', 'arg2'))
        self.assertEqual(conn.kwargs, {'arg3': 'foo', 'arg4': 'bar'})

    def test_set_option(self):
        conn = self._makeOne()
        conn.set_option('foo', 'bar')
        conn.set_option(1, 2)
        self.assertEqual(conn.options, {'foo': 'bar', 1: 2})

    def test_start_tls(self):
        conn = self._makeOne()
        conn.start_tls_s()
        self.assertTrue(conn.start_tls_called)

    def test_result(self):
        conn = self._makeOne()
        self.assertEqual(conn.result(),
                         ('partial',
                          [('partial result', {b'dn': b'partial result'})]))

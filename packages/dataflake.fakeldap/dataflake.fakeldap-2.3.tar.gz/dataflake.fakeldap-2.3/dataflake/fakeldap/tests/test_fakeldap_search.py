# -*- coding: utf-8 -*-
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
from dataflake.fakeldap.utils import to_utf8


class FakeLDAPSearchTests(FakeLDAPTests):

    def test_search_specific(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('thirdfoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

    def test_search_specific_leadingspace(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('thirdfoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn= foo)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

    def test_search_specific_trailingspace(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('thirdfoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo )')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

    def test_search_specific_leadingtrailingspace(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('thirdfoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn= foo )')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

    def test_search_nonspecific(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('bar')
        self._addUser('baz')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(objectClass=*)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 3)
        # Note: searches for all results and not scope BASE will return
        # RDNs instead of full DNs
        self.assertEqual(set(dn_values),
                         set([b'cn=foo', b'cn=bar', b'cn=baz']))

    def test_search_nonspecific_scope_base(self):
        import ldap
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        res = conn.search_s(user_dn, scope=ldap.SCOPE_BASE,
                            query=b'(objectClass=*)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

    def test_search_specific_scope_base(self):
        import ldap
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        res = conn.search_s(user_dn, scope=ldap.SCOPE_BASE,
                            query=b'(&(objectClass=person)(cn=foo))')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

    def test_search_full_wildcard(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('threefoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=*)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 3)
        self.assertEqual(set(dn_values),
                         set([b'cn=foo,ou=users,dc=localhost',
                              b'cn=footwo,ou=users,dc=localhost',
                              b'cn=threefoo,ou=users,dc=localhost']))

    def test_search_startswithendswith_wildcard(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('onefootwo')
        self._addUser('threefoo')
        self._addUser('bar')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=*foo*)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 3)
        self.assertEqual(set(dn_values),
                         set([b'cn=foo,ou=users,dc=localhost',
                              b'cn=onefootwo,ou=users,dc=localhost',
                              b'cn=threefoo,ou=users,dc=localhost']))

    def test_search_endswith_wildcard(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('threefoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=*foo)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 2)
        self.assertEqual(set(dn_values),
                         set([b'cn=foo,ou=users,dc=localhost',
                              b'cn=threefoo,ou=users,dc=localhost']))

    def test_search_startswith_wildcard(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('footwo')
        self._addUser('threefoo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo*)')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 2)
        self.assertEqual(set(dn_values),
                         set([b'cn=foo,ou=users,dc=localhost',
                              b'cn=footwo,ou=users,dc=localhost']))

    def test_search_anded_filter(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('bar')
        self._addUser('baz')

        query_success = b'(&(cn=foo)(objectClass=person))'
        res = conn.search_s(b'ou=users,dc=localhost', query=query_success)
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 1)
        self.assertEqual(dn_values, [b'cn=foo,ou=users,dc=localhost'])

        query_failure = b'(&(cn=foo)(objectClass=inetOrgPerson))'
        self.assertFalse(conn.search_s(b'ou=users,dc=localhost',
                         query=query_failure))

    def test_search_ored_filter(self):
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('bar')
        self._addUser('baz')

        res = conn.search_s(b'ou=users,dc=localhost',
                            query=b'(|(cn=foo)(cn=bar))')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 2)
        self.assertEqual(set(dn_values),
                         set([b'cn=foo,ou=users,dc=localhost',
                              b'cn=bar,ou=users,dc=localhost']))

    def test_search_invalid_base(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.search_s,
                          b'o=base', query=b'(objectClass=*)')

    def test_search_by_mail(self):
        conn = self._makeOne()
        self._addUser('foo', mail='foo@foo.com')
        self._addUser('bar', mail='bar@bar.com')
        self._addUser('baz', mail='baz@baz.com')

        res = conn.search_s(b'ou=users,dc=localhost',
                            query=b'(|(mail=foo@foo.com)(mail=bar@bar.com))')
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 2)
        self.assertEqual(set(dn_values),
                         set([b'cn=foo,ou=users,dc=localhost',
                              b'cn=bar,ou=users,dc=localhost']))

    def test_search_by_utf8(self):
        conn = self._makeOne()
        utf8_foo = to_utf8(u'f\xf8\xf8')
        utf8_bar = to_utf8(u'b\xe5r')
        self._addUser(utf8_foo)
        self._addUser(utf8_bar)
        self._addUser('baz')

        res = conn.search_s(b'ou=users,dc=localhost',
                            query=b'(|(cn=%s)(cn=%s))' % (utf8_foo, utf8_bar))
        dn_values = [dn for (dn, attr_dict) in res]
        self.assertEqual(len(dn_values), 2)
        self.assertEqual(set(dn_values),
                         set([b'cn=%s,ou=users,dc=localhost' % utf8_foo,
                              b'cn=%s,ou=users,dc=localhost' % utf8_bar]))

    def test_return_all_attributes(self):
        conn = self._makeOne()
        self._addUser('foo', mail='foo@foo.com')

        res = conn.search_s(b'ou=users,dc=localhost',
                            query=b'(cn=foo)', attrs=None)
        self.assertEqual(len(res), 1)
        dn, attr_dict = res[0]
        self.assertEqual(dn, b'cn=foo,ou=users,dc=localhost')
        self.assertTrue(b'cn' in attr_dict)
        self.assertTrue(b'mail' in attr_dict)
        self.assertTrue(b'userPassword' in attr_dict)
        self.assertTrue(b'objectClass' in attr_dict)

    def test_return_filtered_attributes(self):
        conn = self._makeOne()
        self._addUser('foo', mail='foo@foo.com')

        res = conn.search_s(b'ou=users,dc=localhost',
                            query=b'(cn=foo)', attrs=[b'cn', b'mail'])
        self.assertEqual(len(res), 1)
        dn, attr_dict = res[0]
        self.assertEqual(dn, b'cn=foo,ou=users,dc=localhost')
        self.assertTrue(b'cn' in attr_dict)
        self.assertTrue(b'mail' in attr_dict)
        self.assertFalse(b'userPassword' in attr_dict)
        self.assertFalse(b'objectClass' in attr_dict)

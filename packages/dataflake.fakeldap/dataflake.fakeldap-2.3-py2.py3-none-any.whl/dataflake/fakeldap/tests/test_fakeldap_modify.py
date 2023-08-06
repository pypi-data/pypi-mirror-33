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


class FakeLDAPModifyTests(FakeLDAPTests):

    def test_modify_wrongbase(self):
        import ldap
        conn = self._makeOne()
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.modify_s,
                          b'cn=foo,o=base', [])

    def test_modify_wrongrecord(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.modify_s,
                          b'cn=bar,ou=users,dc=localhost', [])

    def test_modify_success(self):
        import copy
        from ldap.modlist import modifyModlist
        conn = self._makeOne()
        self._addUser('foo')

        foo = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        old_values = foo[0][1]
        self.assertEqual(old_values[b'objectClass'], [b'top', b'person'])
        self.assertFalse(old_values.get(b'mail'))
        new_values = copy.deepcopy(old_values)
        new_values[b'objectClass'] = [b'top', b'inetOrgPerson']
        new_values[b'mail'] = [b'foo@email.com']

        modlist = modifyModlist(old_values, new_values)
        conn.modify_s(b'cn=foo,ou=users,dc=localhost', modlist)
        foo = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        self.assertEqual(foo[0][1][b'objectClass'],
                         [b'top', b'inetOrgPerson'])
        self.assertEqual(foo[0][1][b'mail'], [b'foo@email.com'])

    def test_modify_replace(self):
        import ldap

        conn = self._makeOne()
        self._addUser('foo', mail='foo@bar.com')

        foo = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        old_values = foo[0][1]
        self.assertEqual(old_values[b'mail'], [b'foo@bar.com'])

        modlist = [(ldap.MOD_REPLACE, b'mail', [b'foo@email.com'])]
        conn.modify_s(b'cn=foo,ou=users,dc=localhost', modlist)
        foo = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        self.assertEqual(foo[0][1][b'mail'], [b'foo@email.com'])

    def test_modify_add(self):
        import ldap

        conn = self._makeOne()
        self._addUser('foo', mail='foo@bar.com')

        foo = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        old_values = foo[0][1]
        self.assertEqual(old_values[b'mail'], [b'foo@bar.com'])

        modlist = [(ldap.MOD_ADD, b'mail', [b'foo@email.com'])]
        conn.modify_s(b'cn=foo,ou=users,dc=localhost', modlist)
        foo = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        self.assertEqual(set(foo[0][1][b'mail']),
                         set([b'foo@email.com', b'foo@bar.com']))

    def test_modrdn_wrongbase(self):
        import ldap
        conn = self._makeOne()
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.modrdn_s,
                          b'cn=foo,o=base', b'cn=bar')

    def test_modrdn_wrongrecord(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.modrdn_s,
                          b'cn=bar,ou=users,dc=localhost', b'cn=baz')

    def test_modrdn_existing_clash(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')
        self._addUser('bar')

        self.assertRaises(ldap.ALREADY_EXISTS, conn.modrdn_s,
                          b'cn=foo,ou=users,dc=localhost', b'cn=bar')

    def test_modrdn_success(self):
        import ldap
        conn = self._makeOne()
        self._addUser('foo')

        foo = conn.search_s(b'cn=foo,ou=users,dc=localhost',
                            scope=ldap.SCOPE_BASE, query=b'(objectClass=*)')
        self.assertTrue(foo)
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.search_s,
                          b'cn=bar,ou=users,dc=localhost',
                          scope=ldap.SCOPE_BASE, query=b'(objectClass=*)')

        conn.modrdn_s(b'cn=foo,ou=users,dc=localhost', b'cn=bar')
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.search_s,
                          b'cn=foo,ou=users,dc=localhost',
                          scope=ldap.SCOPE_BASE, query=b'(objectClass=*)')
        bar = conn.search_s(b'cn=bar,ou=users,dc=localhost',
                            scope=ldap.SCOPE_BASE, query=b'(objectClass=*)')
        self.assertTrue(bar)

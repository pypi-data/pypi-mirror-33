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


class FakeLDAPBindTests(FakeLDAPTests):

    def test_bind_empty_pwd(self):
        conn = self._makeOne()

        # special case for empty password (???)
        self.assertTrue(conn.simple_bind_s(b'cn=Anybody', ''))
        self.assertEqual(conn._last_bind[1], (b'cn=Anybody', ''))

    def test_bind_manager(self):
        conn = self._makeOne()

        # special case for logging in as "Manager"
        self.assertTrue(conn.simple_bind_s(b'cn=Manager', 'whatever'))
        self.assertEqual(conn._last_bind[1], (b'cn=Manager', 'whatever'))

    def test_bind_success(self):
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        # Login with correct credentials
        self.assertTrue(conn.simple_bind_s(user_dn, password))
        self.assertEqual(conn._last_bind[1], (user_dn, password))

    def test_bind_wrong_pwd(self):
        import ldap
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        # Login with bad credentials
        self.assertRaises(ldap.INVALID_CREDENTIALS, conn.simple_bind_s,
                          user_dn, 'INVALID PASSWORD')

    def test_bind_no_password_in_record(self):
        import ldap
        conn = self._makeOne()

        # Users with empty passwords cannot log in
        user2 = [(b'cn', ['user2'])]
        conn.add_s(b'cn=user2,ou=users,dc=localhost', user2)
        self.assertRaises(ldap.INVALID_CREDENTIALS, conn.simple_bind_s,
                          b'cn=user2,ou=users,dc=localhost', 'ANY PASSWORD')

    def test_bind_no_such_user(self):
        import ldap
        conn = self._makeOne()

        # Users with empty passwords cannot log in
        user2 = [(b'cn', ['user2'])]
        conn.add_s(b'cn=user2,ou=users,dc=localhost', user2)
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.simple_bind_s,
                          b'cn=user1,ou=users,dc=localhost', 'ANY PASSWORD')

    def test_unbind_clears_last_bind(self):
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        self.assertTrue(conn.simple_bind_s(user_dn, password))
        self.assertEqual(conn._last_bind[1], (user_dn, password))

        conn.unbind()
        self.assertEqual(conn._last_bind, None)

    def test_unbind_s_clears_last_bind(self):
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        self.assertTrue(conn.simple_bind_s(user_dn, password))
        self.assertEqual(conn._last_bind[1], (user_dn, password))

        conn.unbind_s()
        self.assertEqual(conn._last_bind, None)


class HashedPasswordTests(FakeLDAPTests):

    def test_connection_is_hashed(self):
        conn = self._makeOne()
        self.assertEqual(conn.hash_password, True)

    def test_password_is_hashed(self):
        from dataflake.fakeldap.utils import hash_pwd
        conn = self._makeOne()
        self._addUser('foo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        pwd = res[0][1][b'userPassword'][0]
        self.assertEqual(pwd, hash_pwd('foo_secret'))

    def test_bind_success(self):
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        # Login with correct credentials
        self.assertTrue(conn.simple_bind_s(user_dn, password))
        self.assertEqual(conn._last_bind[1], (user_dn, password))

    def test_bind_wrong_pwd(self):
        import ldap
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        # Login with bad credentials
        self.assertRaises(ldap.INVALID_CREDENTIALS, conn.simple_bind_s,
                          user_dn, 'INVALID PASSWORD')


class ClearTextPasswordTests(FakeLDAPTests):

    def _getTargetClass(self):
        from dataflake.fakeldap import FakeLDAPConnection

        class ClearTextConnection(FakeLDAPConnection):
            """ A FakeLDAPConnection with password hashing disabled
            """
            hash_password = False

        return ClearTextConnection

    def test_connection_is_clear_text(self):
        conn = self._makeOne()
        self.assertEqual(conn.hash_password, False)

    def test_password_is_clear_text(self):
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        res = conn.search_s(b'ou=users,dc=localhost', query=b'(cn=foo)')
        pwd = res[0][1][b'userPassword'][0]
        self.assertEqual(pwd, 'foo_secret')

    def test_bind_success(self):
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        # Login with correct credentials
        self.assertEqual(user_dn, b'cn=foo,ou=users,dc=localhost')
        self.assertEqual(password, 'foo_secret')
        self.assertTrue(conn.simple_bind_s(user_dn, password))
        self.assertEqual(conn._last_bind[1], (user_dn, password))

    def test_bind_wrong_pwd(self):
        import ldap
        conn = self._makeOne()
        user_dn, password = self._addUser('foo')

        # Login with bad credentials
        self.assertRaises(ldap.INVALID_CREDENTIALS, conn.simple_bind_s,
                          user_dn, 'INVALID PASSWORD')

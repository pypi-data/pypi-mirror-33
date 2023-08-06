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
""" unit tests base classes
"""

import unittest

from dataflake.fakeldap.utils import to_utf8


class FakeLDAPTests(unittest.TestCase):

    def setUp(self):
        from dataflake.fakeldap import TREE
        self.db = TREE
        self.db.addTreeItems(b'ou=users,dc=localhost')
        self.db.addTreeItems(b'ou=groups,dc=localhost')

    def tearDown(self):
        self.db.clear()

    def _getTargetClass(self):
        from dataflake.fakeldap import FakeLDAPConnection
        return FakeLDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _addUser(self, name, mail=None):
        from dataflake.fakeldap.utils import hash_pwd
        conn = self._makeOne()
        utf8_name = to_utf8(name)
        user_dn = b'cn=%s,ou=users,dc=localhost' % utf8_name
        user_pwd = '%s_secret' % name

        if conn.hash_password:
            pwd = hash_pwd(user_pwd)
        else:
            pwd = user_pwd

        user = [(b'cn', [utf8_name]), (b'userPassword', [pwd]),
                (b'objectClass', [b'top', b'person'])]
        if mail is not None:
            user.append((b'mail', [to_utf8(mail)]))

        conn.add_s(user_dn, user)
        return (user_dn, user_pwd)

    def _addGroup(self, name, members=None):
        name = to_utf8(name)
        conn = self._makeOne()
        group_dn = b'cn=%s,ou=groups,dc=localhost' % name

        group = [(b'cn', [name]), (b'objectClass', [b'top', b'group'])]
        if members is not None:
            members = [b'cn=%s,ou=users,dc=localhost' % to_utf8(x)
                       for x in members]
            group.append((conn.member_attr, members))

        conn.add_s(group_dn, group)
        return group_dn

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
""" test_connection_delete: Tests for the LDAPConnection delete method
"""

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import UNENCODED_LATIN1


class ConnectionDeleteTests(LDAPConnectionTests):

    def test_delete_noauthentication(self):
        self._addRecord('cn=foo,dc=localhost')
        conn = self._makeSimple()
        conn.delete('cn=foo,dc=localhost')
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, b'')
        self.assertEqual(bindpwd, b'')

    def test_delete_authentication(self):
        self._addRecord('cn=foo,dc=localhost')
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             api_encoding='iso-8859-1')
        bind_dn = u'cn=%s,dc=localhost' % UNENCODED_LATIN1
        bind_dn_apiencoded = bind_dn.encode('iso-8859-1')
        bind_dn_serverencoded = bind_dn.encode('UTF-8')
        self._addRecord(bind_dn_serverencoded, userPassword='foo')
        conn.delete('cn=foo,dc=localhost', bind_dn=bind_dn_apiencoded,
                    bind_pwd='foo')
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, bind_dn_serverencoded)
        self.assertEqual(bindpwd, b'foo')

    def test_delete(self):
        self._addRecord('cn=foo,dc=localhost')
        conn = self._makeSimple()
        results = conn.search('dc=localhost', '(cn=foo)')
        self.assertEqual(results['results'], [{'dn': b'cn=foo'}])

        conn.delete('cn=foo,dc=localhost')
        results = conn.search('dc=localhost', '(cn=foo)')
        self.assertFalse(results['results'])

    def test_delete_readonly(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             read_only=True)
        self.assertRaises(RuntimeError, conn.delete, 'cn=foo')

    def test_delete_referral(self):
        import ldap
        self._addRecord('cn=foo,dc=localhost')
        exc_arg = {'info': 'please go to ldap://otherhost:1389'}
        conn, ldap_connection = self._makeRaising('delete_s', ldap.REFERRAL,
                                                  exc_arg)
        conn.delete('cn=foo,dc=localhost')
        self.assertEqual(ldap_connection.conn_string, 'ldap://otherhost:1389')
        self.assertEqual(ldap_connection.args, (b'cn=foo,dc=localhost',))

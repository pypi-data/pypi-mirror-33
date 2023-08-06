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
""" test_connection_connect: Tests for the LDAPConnection connect method
"""

from dataflake.fakeldap.utils import hash_pwd

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import UNENCODED_LATIN1


class ConnectionConnectTests(LDAPConnectionTests):

    def test_connect_initial_defaults(self):
        import ldap
        conn = self._makeSimple()
        connection = conn.connect()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, b'')
        self.assertEqual(bindpwd, b'')
        self.assertFalse(getattr(connection, 'timeout', False))
        self.assertEqual(connection.options.get(ldap.OPT_REFERRALS),
                         ldap.DEREF_NEVER)
        self.assertFalse(ldap.OPT_NETWORK_TIMEOUT in connection.options)
        self.assertFalse(connection.start_tls_called)

    def test_connect_initial_bind_dn_not_None(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             api_encoding='iso-8859-1')
        bind_dn = u'cn=%s,dc=localhost' % UNENCODED_LATIN1
        bind_dn_apiencoded = bind_dn.encode('iso8859-1')
        bind_dn_serverencoded = bind_dn.encode('UTF-8')
        self._addRecord(bind_dn_serverencoded, userPassword='')
        connection = conn.connect(bind_dn_apiencoded, '')
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, bind_dn_serverencoded)
        self.assertEqual(bindpwd, b'')

    def test_connect_non_initial(self):
        conn = self._makeSimple()
        self._addRecord('cn=foo,dc=localhost', userPassword='pass')

        connection = conn.connect('cn=foo,dc=localhost', 'pass')
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, b'cn=foo,dc=localhost')

        connection = conn.connect(None, 'pass')
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, conn.bind_dn)

    def test_connect_optimeout_specified(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory, op_timeout=99)
        connection = conn.connect()
        self.assertEqual(connection.timeout, 99)

    def test_connect_conntimeout_specified(self):
        import ldap
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             conn_timeout=99)
        connection = conn.connect()
        self.assertEqual(connection.options.get(ldap.OPT_NETWORK_TIMEOUT), 99)

    def test_connect_ldap_starttls(self):
        conn = self._makeOne('host', 636, 'ldaptls', self._factory)
        connection = conn.connect()
        self.assertTrue(connection.start_tls_called)

    def test_connect_noserver_raises(self):
        conn = self._makeSimple()
        conn.removeServer('host', '636', 'ldap')
        self.assertRaises(RuntimeError, conn.connect)

    def test_connect_ldaperror_raises(self):
        import ldap
        conn, ldap_connection = self._makeRaising('start_tls_s',
                                                  ldap.SERVER_DOWN)
        self.assertRaises(ldap.SERVER_DOWN, conn.connect)

    def test_connect_cannot_set_referrals(self):
        import ldap
        conn, ldap_connection = self._makeRaising('set_option', ldap.LDAPError)
        connection = conn.connect()
        self.assertFalse(ldap.OPT_REFERRALS in connection.options)

    def test_disconnect_clears_connection_cache(self):
        conn = self._makeSimple()

        attrs = {'userPassword': hash_pwd('pass')}
        conn.insert('dc=localhost', 'cn=foo', attrs=attrs)

        response = conn.search('dc=localhost', fltr='(cn=foo)',
                               bind_dn='cn=foo,dc=localhost', bind_pwd='pass')
        self.assertEqual(response['size'], 1)

        connection = conn._getConnection()
        self.assertNotEqual(connection, None)
        self.assertEqual(connection._last_bind[1],
                         (b'cn=foo,dc=localhost', b'pass'))

        conn.disconnect()
        self.assertEqual(conn._getConnection(), None)

    def test_disconnect_unbinds_connection(self):
        conn = self._makeSimple()

        attrs = {'userPassword': hash_pwd('pass')}
        conn.insert('dc=localhost', 'cn=foo', attrs=attrs)

        response = conn.search('dc=localhost', fltr='(cn=foo)',
                               bind_dn='cn=foo,dc=localhost', bind_pwd='pass')
        self.assertEqual(response['size'], 1)

        connection = conn._getConnection()
        self.assertNotEqual(connection, None)
        self.assertEqual(connection._last_bind[1],
                         (b'cn=foo,dc=localhost', b'pass'))

        conn.disconnect()
        self.assertEqual(connection._last_bind, None)

    def test_rebind_with_same_password(self):
        conn = self._makeSimple()

        attrs = {'userPassword': hash_pwd('pass')}
        conn.insert('dc=localhost', 'cn=foo', attrs=attrs,
                    bind_dn='cn=Manager,dc=localhost', bind_pwd='pass')
        connection = conn._getConnection()
        self.assertEqual(connection._last_bind[1],
                         (b'cn=Manager,dc=localhost', b'pass'))

        conn.search('dc=localhost', fltr='(cn=foo)',
                    bind_dn='cn=foo,dc=localhost', bind_pwd='pass')
        connection = conn._getConnection()
        self.assertEqual(connection._last_bind[1],
                         (b'cn=foo,dc=localhost', b'pass'))

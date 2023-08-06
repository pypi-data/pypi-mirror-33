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
""" test_utils: Tests for the utils utility functions
"""

import unittest

from dataflake.ldapconnection.utils import escape_dn


class UtilsTest(unittest.TestCase):

    def test_escape_dn(self):
        # http://www.dataflake.org/tracker/issue_00623
        dn = 'cn="Joe Miller, Sr.", ou="odds+sods <1>", dc="host;new"'
        dn_clean = b'cn=Joe Miller\\, Sr.,ou=odds\\+sods \\<1\\>,dc=host\\;new'
        self.assertEqual(escape_dn(dn), dn_clean)

        self.assertEqual(escape_dn(None), None)

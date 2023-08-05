#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2012-2013 Antoine Beaupré <anarcat@orangeseeds.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Library of test tools that can be reused across different test suites.
"""

import locale
import os.path
import pkg_resources
import signal
import sys
import time
import unittest

class AlarmException(IOError):
    pass

def handle_alarm(signum, frame):
    raise AlarmException('timeout in %s' % frame.f_code.co_name)

class TestTimeLimit(unittest.TestCase):
    """a test with a timeout"""

    # in seconds
    timeout = 3

    def setUp(self):
        signal.signal(signal.SIGALRM, handle_alarm)
        signal.setitimer(signal.ITIMER_REAL, self.timeout)

    def tearDown(self):
        signal.alarm(0)

class TestTimeLimitSelfTest(TestTimeLimit):

    # 10ms
    timeout = 0.01

    def test_signal(self):
        with self.assertRaises(AlarmException):
            time.sleep(1)


def find_test_file(name):
    try:
        pkg = pkg_resources.Requirement.parse("monkeysign")
        path = os.path.join('monkeysign', 'tests', 'files', name)
        return pkg_resources.resource_filename(pkg, path)
    except pkg_resources.DistributionNotFound:
        return os.path.join(os.path.dirname(__file__), 'files', name)


class TestTestFile(unittest.TestCase):
    def test_test_file(self):
        p = find_test_file('testfile.txt')
        self.assertTrue(os.path.exists(p))


def skipUnlessUnicodeLocale():
    try:
        u"é".encode(sys.stdout.encoding or locale.getpreferredencoding(True))
    except UnicodeEncodeError:
        return unittest.skip('test requires unicode locale')
    else:
        return lambda func: func


def skipIfDatePassed(date, fmt='%Y-%m-%dT%H:%M:%S%Z'):
    # date is in ISO-8601 format by default
    # XXX: should be auto-generated from the key material, or we
    # should be able to use gpg --faked-system-time but that doesn't
    # work in 1.x
    if time.gmtime() >= time.strptime(date, fmt):
        return unittest.skip('date %s is in the past' % date)
    else:
        return lambda func: func


def skipUnlessNetwork():
    """add a knob to disable network tests

    to disable network tests, use PYTEST_USENETWORK=no. by default, it
    is assumed there is network access.

    this is mainly to deal with Debian packages that are built in
    network-less chroots. unfortunately, there is no standard
    environment in dpkg-buildpackage or ./debian/rules binary that we
    can rely on to disable tests, so we revert to a custom variable
    that can hopefully make it up to the pybuild toolchain

    I looked at DEB_BUILD_OPTIONS=network, but that is not standard
    and only mentionned once here:

    https://lists.debian.org/debian-devel/2009/09/msg00992.html

    DEB_BUILD_OPTIONS is also not set by default, so it's not a good
    way to detect Debian package builds

    pbuilder uses USENETWORK=no/yes, schroot uses UNSHARE_NET, but
    those are not standard either, see:

    https://github.com/spotify/dh-virtualenv/issues/77
    https://github.com/codelibre-net/schroot/blob/2e3d015a759d2b5106e851af34c8d5974d84f18e/lib/schroot/chroot/facet/unshare.cc
    """

    if ('PYTEST_USENETWORK' in os.environ
       and 'no' in os.environ.get('PYTEST_USENETWORK', '')):
        return unittest.skip('network tests disabled (PYTEST_USENETWORK=no)')
    else:
        return lambda func: func


if __name__ == '__main__':
    unittest.main()

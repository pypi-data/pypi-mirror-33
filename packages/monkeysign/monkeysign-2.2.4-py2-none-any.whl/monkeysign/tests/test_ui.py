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
Test suite for the basic user interface class.
"""

from email.header import Header
import locale
import unittest
import os
import pkg_resources
from pkg_resources import ResolutionError
import sys
import re
from StringIO import StringIO
import tempfile
try:
    from unittest.mock import Mock
except ImportError:
    try:
        from mock import Mock
    except:
        Mock = False

def which2(cmd):
    """naive implementation of which for Python 2"""
    path = os.environ.get("PATH", os.defpath)
    if not path:
        return None
    path = path.split(os.pathsep)
    for dir in path:
        name = os.path.join(dir, cmd)
        if os.path.exists(name):
            return name
    return None

try:
    from shutil import which  # only in py3
except ImportError:
    which = which2

sys.path.insert(0, os.path.dirname(__file__) + '/..')

from monkeysign.ui import MonkeysignUi, EmailFactory, MonkeysignArgumentParser
from monkeysign.gpg import TempKeyring, GpgRuntimeError

import test_lib
# optimized because called often
from test_lib import find_test_file, skipIfDatePassed, skipUnlessNetwork


class CliBaseTest(unittest.TestCase):
    def setUp(self):
        self.argv = sys.argv
        sys.argv = [ 'monkeysign', '--no-mail' ]

    def execute(self):
        '''execute the monkeysign script directly

        there are two ways to do this without subprocess:

        1. execfile(somepath), which we use when we run from the
        source tree directly

        2. run_script, which we use when we are installed through setup.py
        '''
        directory, basename = os.path.split(self.argv[0])
        path, directory = os.path.split(os.path.realpath(directory))
        if directory == 'scripts' or basename == 'setup.py':
            # default to run from source dir. this is necessary for
            # ./scripts/monkeysign --test and ./setup.py test
            execfile(os.path.dirname(__file__) + '/../../scripts/monkeysign')
        else:
            try:
                pkg = pkg_resources.get_distribution('monkeysign')
                pkg.run_script('monkeysign', globals())
            except pkg_resources.ResolutionError:
                # package exists, but script not in distribution
                # this happens when wheel is installed by pip
                execfile(which('monkeysign'))

    def write_to_callback(self, stdin, callback):
        r, w = os.pipe()
        pid = os.fork()
        if pid:
            # parent
            os.close(w)
            os.dup2(r, 0) # make stdin read from the child
            oldstdout = sys.stdout
            sys.stdout = open('/dev/null', 'w') # silence output
            callback(self)
            sys.stdout = oldstdout
        else:
            # child
            os.close(r)
            w = os.fdopen(w, 'w')
            w.write(stdin) # say whatever is needed to msign-cli
            w.flush()
            os._exit(0)

    def tearDown(self):
        sys.argv = self.argv


@unittest.skipUnless(Mock, 'mock library missing')
class CliTestCase(CliBaseTest):
    def setUp(self):
        CliBaseTest.setUp(self)

        def sysinfo():
            return []

        ui = Mock()
        ui.sysinfo = MonkeysignUi.sysinfo
        ui.epilog = '%s'
        ui.usage = ''
        self.parser = MonkeysignArgumentParser(ui)

    def test_call_usage(self):
        stderrbak = sys.stderr
        with open('/dev/null', 'a') as sys.stderr:
            with self.assertRaises(SystemExit):
                self.execute()
        sys.stderr = stderrbak

    def test_call_version(self):
        """test to see if we output monkeysign and gpg versions"""
        sys.argv = ['monkeysign', '--version']
        stderrbak = sys.stderr
        sys.stderr = StringIO()
        with self.assertRaises(SystemExit):
            self.execute()
        self.assertIn('Monkeysign: ', sys.stderr.getvalue())
        self.assertIn('GnuPG: ', sys.stderr.getvalue())
        sys.stderr = stderrbak

    def test_configs(self):
        """test configuration file support"""
        config1 = tempfile.NamedTemporaryFile()
        config2 = tempfile.NamedTemporaryFile()
        config1.write('user=foo')
        config2.write('user=bar')
        config1.flush()
        config2.flush()
        self.parser.configs = [config1.name, config2.name]
        args = self.parser.parse_args()
        self.assertEqual(args.user, 'foo', 'first config wins')
        args = self.parser.parse_args(['--user', 'quux'])
        self.assertEqual(args.user, 'quux', 'commandline wins')

    def test_write_configs(self):
        """test how we can write config files"""
        args = self.parser.parse_args(['--local', '--smtpserver', 'localhost', '--tls', 'foo'])
        # first test parts of save_config()
        lines = self.parser.args_to_config(args)
        out = StringIO()
        self.parser.write_config(lines, out)
        out = out.getvalue()
        self.assertIn('smtpserver=localhost', out)
        self.assertIn('local', out)
        self.assertIn('tls', out)
        self.assertNotIn('foo', out)
        config = tempfile.NamedTemporaryFile()
        # then save_config() itself
        self.assertTrue(self.parser.save_config(args, config, close=False))
        config.flush()
        args = self.parser.parse_args(['@'+config.name])
        self.assertEqual(args.smtpserver, 'localhost')
        self.assertTrue(args.tls)
        self.assertTrue(args.local)


@skipIfDatePassed('2017-06-01T00:00:00UTC')
class CliTestDialog(CliBaseTest):
    def setUp(self):
        CliBaseTest.setUp(self)
        self.gpg = TempKeyring()
        os.environ['GNUPGHOME'] = self.gpg.homedir
        self.assertTrue(self.gpg.import_data(open(find_test_file('7B75921E.asc')).read()))
        self.assertTrue(self.gpg.import_data(open(find_test_file('96F47C6A.asc')).read()))
        self.assertTrue(self.gpg.import_data(open(find_test_file('96F47C6A-secret.asc')).read()))

        sys.argv += [ '-u', '96F47C6A', '--', '7B75921E' ]

    @test_lib.skipUnlessUnicodeLocale()
    def test_sign_fake_keyring(self):
        """test if we can sign a key on a fake keyring"""
        def callback(self):
            self.execute()
        self.write_to_callback("y\ny\n", callback) # just say yes

    @test_lib.skipUnlessUnicodeLocale()
    def test_sign_one_uid(self):
        """test if we can sign only one keyid"""
        def callback(self):
            self.execute()
        self.write_to_callback("n\n1\ny\n", callback) # just say yes

    @test_lib.skipUnlessUnicodeLocale()
    def test_two_empty_responses(self):
        """test what happens when we answer nothing twice

this tests for bug #716675"""
        def callback(self):
            with self.assertRaises(EOFError):
                self.execute()
        self.write_to_callback("\n\n", callback) # say 'default' twice


@skipIfDatePassed('2017-06-01T00:00:00UTC')
class CliTestSpacedFingerprint(CliTestDialog):
    def setUp(self):
        CliTestDialog.setUp(self)
        sys.argv.pop() # remove the uid from parent class
        sys.argv += '8DC9 01CE 6414 6C04 8AD5  0FBB 7921 5252 7B75 921E'.split()

class BaseTestCase(unittest.TestCase):
    pattern = None
    args = []

    def setUp(self):
        self.args = [ '--no-mail' ] + self.args + [ x for x in sys.argv[1:] if x.startswith('-') ]
        if self.pattern is not None:
            self.args += [ self.pattern ]
        # do not read system-wide configs in tests
        MonkeysignArgumentParser.configs = []
        self.ui = MonkeysignUi(self.args)
        self.ui.keyring = TempKeyring()
        self.ui.prepare() # needed because we changed the base keyring

class BasicTests(BaseTestCase):
    pattern = '7B75921E'

    def setUp(self):
        BaseTestCase.setUp(self)
        self.homedir = self.ui.tmpkeyring.homedir

    def test_cleanup(self):
        del self.ui
        self.assertFalse(os.path.exists(self.homedir))


@skipIfDatePassed('2017-06-01T00:00:00UTC')
class SigningTests(BaseTestCase):
    pattern = '7B75921E'

    def setUp(self):
        """setup a basic keyring capable of signing a local key"""
        BaseTestCase.setUp(self)
        self.assertTrue(self.ui.keyring.import_data(open(find_test_file('7B75921E.asc')).read()))
        self.assertTrue(self.ui.tmpkeyring.import_data(open(find_test_file('96F47C6A.asc')).read()))
        self.assertTrue(self.ui.keyring.import_data(open(find_test_file('96F47C6A.asc')).read()))
        self.assertTrue(self.ui.keyring.import_data(open(find_test_file('96F47C6A-secret.asc')).read()))

    def test_find_key(self):
        """test if we can extract the key locally

this duplicates tests from the gpg code, but is necessary to test later functions"""
        self.ui.find_key()

    def test_copy_secrets(self):
        """test if we can copy secrets between the two keyrings

this duplicates tests from the gpg code, but is necessary to test later functions"""
        self.test_find_key()
        self.ui.copy_secrets()
        self.assertTrue(self.ui.keyring.get_keys(None, True, False))
        self.assertGreaterEqual(len(self.ui.keyring.get_keys(None, True, False)), 1)
        self.assertGreaterEqual(len(self.ui.keyring.get_keys(None, True, True)), 1)

    def test_sign_key(self):
        """test if we can sign the keys non-interactively"""
        self.test_copy_secrets()
        self.ui.sign_key()
        self.assertGreaterEqual(len(self.ui.signed_keys), 1)

    def test_sign_own_key(self):
        """Test that signing a user's own key fails"""
        self.ui.pattern = '96F47C6A'
        self.test_copy_secrets()
        self.ui.sign_key()
        self.assertEquals(len(self.ui.signed_keys), 0)
        self.ui.pattern = '7B75921E'

    def test_gpg_conf(self):
        """test if gpg.conf default-key works"""
        # this fails with GnuPG 2.1
        with open(os.path.join(self.ui.keyring.homedir, 'gpg.conf'), 'w') as f:
            f.write('default-key 3F94240C918E63590B04152E86E4E70A96F47C6A')
        # needed because we created a new gpg.conf
        self.ui.prepare()
        self.assertTrue(os.path.exists(os.path.join(self.ui.tmpkeyring.homedir, 'gpg.conf')))
        self.test_copy_secrets()
        self.ui.tmpkeyring.context.call_command(['list-secret-keys'])
        self.assertIn('3F94240C918E63590B04152E86E4E70A96F47C6A',
                      self.ui.tmpkeyring.context.stdout,
                      'tmpkeyring can see private keys')
        self.ui.sign_key()
        self.ui.tmpkeyring.context.call_command(['list-sigs', '7B75921E'])
        # this is the primary test key, it should have signed this
        self.assertIn('sig:::1:86E4E70A96F47C6A:',
                      self.ui.tmpkeyring.context.stdout)

    def test_multiple_secrets(self):
        """test if we pick the right key define in gpg.conf"""
        # configure gpg to use the second test key as a default key
        with open(os.path.join(self.ui.keyring.homedir, 'gpg.conf'), 'w') as f:
            f.write('default-key 323F39BD')
        self.ui.prepare()
        self.test_copy_secrets()
        self.ui.keyring.import_data(open(find_test_file('323F39BD.asc')).read())
        self.ui.keyring.import_data(open(find_test_file('323F39BD-secret.asc')).read())
        self.test_copy_secrets()
        self.ui.sign_key()
        self.ui.tmpkeyring.context.call_command(['list-sigs', '7B75921E'])
        # this is the primary test key, it shouldn't have signed this
        self.assertNotIn('sig:::1:86E4E70A96F47C6A:',
                         self.ui.tmpkeyring.context.stdout)
        # try to find a revoked uid that is signed
        for uid in self.ui.tmpkeyring.context.stdout.split('uid:'):
            if 'rev:' in uid:
                self.assertNotIn('sig:::1:A31E75E4323F39BD', uid)

    def test_create_mail_multiple(self):
        """test if exported keys contain the right uid"""
        self.test_sign_key()

        for fpr, key in self.ui.signed_keys.items():
            oldmsg = None
            for uid in key.uids.values():
                msg = EmailFactory(self.ui.tmpkeyring.export_data(fpr), fpr, uid.uid, 'unittests@localhost', 'devnull@localhost')
                if oldmsg is not None:
                    self.assertNotEqual(oldmsg.as_string(), msg.as_string())
                    self.assertNotEqual(oldmsg.create_mail_from_block().as_string(),
                                        msg.create_mail_from_block().as_string())
                    self.assertNotEqual(oldmsg.tmpkeyring.export_data(fpr),
                                        msg.tmpkeyring.export_data(fpr))
                oldmsg = msg
            self.assertIsNot(oldmsg, None)

    def test_export_key(self):
        """see if we export a properly encrypted key set"""
        messages = []
        # collect messages instead of warning the user
        self.ui.warn = messages.append
        self.test_sign_key()
        self.ui.export_key()
        self.assertIsNone(self.ui.export_key(), 'sends mail?')
        paste = messages.pop()
        self.assertNotIn('BEGIN PGP PUBLIC KEY BLOCK', paste,
                         'message not encrypted')
        self.assertIn('BEGIN PGP MESSAGE', paste, 'message not encrypted')
        self.assertNotIn('MIME-Version', paste,
                         'message to paste has weird MIME headers')

    def test_sendmail(self):
        """see if we can generate a proper commandline to send email"""
        self.test_sign_key()
        messages = []
        # collect messages instead of warning the user
        self.ui.warn = messages.append
        self.ui.options.nomail = False
        self.ui.options.user = 'unittests@localhost'
        self.ui.options.to = 'devnull@localhost'
        self.ui.options.mta = "dd status=none of='" + \
                              self.ui.keyring.homedir + "/%(to)s'"
        self.assertTrue(self.ui.export_key(), 'fails to send mail')
        filename = '%s/%s' % (self.ui.keyring.homedir, self.ui.options.to)
        self.assertGreater(os.path.getsize(filename), 0,
                           'mail properly created')
        self.assertIn('sent message to %s with dd' % self.ui.options.to,
                      messages.pop(),
                      'missing information to user')
        self.ui.options.to = 'devnull; touch bad'
        self.assertTrue(self.ui.export_key(),
                        'fails to send email to weird address')
        self.assertFalse(os.path.exists('bad'),
                         'vulnerable to command injection')

    def test_mua(self):
        self.test_sign_key()
        messages = []
        # collect messages instead of warning the user
        self.ui.warn = messages.append
        self.ui.options.nomail = False
        self.ui.options.user = 'unittests@localhost'
        self.ui.options.to = 'devnull@localhost'
        self.ui.options.mua = 'python ' + os.path.join(os.path.dirname(__file__),
                                           'mua-writer.py') \
            + " --to %(to)s --subject %(subject)s --body %(body)s" \
            + " --attach %(attach)s"
        self.assertTrue(self.ui.export_key(), 'fails to send mail')
        outputfile = self.ui.mailer_output.rstrip()
        self.assertTrue(os.path.exists(outputfile), 'file %s exists' % outputfile)
        with open(outputfile) as email:
            contents = email.read()
            self.assertIn('MIME', contents)
            self.assertIn(self.ui.options.to, contents)
            self.assertIn(self.ui.options.user, contents)
            try:
                subject = Header(EmailFactory.subject.encode('ascii')).encode()
            except UnicodeEncodeError:
                subject = Header(EmailFactory.subject, 'UTF-8').encode()
            self.assertIn(subject, contents)
            self.assertIn(EmailFactory.body, contents)
        os.unlink(outputfile)


@skipIfDatePassed('2017-06-01T00:00:00UTC')
class EmailFactoryTest(BaseTestCase):
    pattern = '7B75921E'

    def setUp(self):
        """setup a basic keyring capable of signing a local key"""
        BaseTestCase.setUp(self)
        self.assertTrue(self.ui.tmpkeyring.import_data(open(find_test_file('7B75921E.asc')).read()))
        self.assertTrue(self.ui.tmpkeyring.import_data(open(find_test_file('96F47C6A.asc')).read()))
        self.assertTrue(self.ui.tmpkeyring.import_data(open(find_test_file('96F47C6A-secret.asc')).read()))

        self.email = EmailFactory(self.ui.tmpkeyring.export_data(self.pattern), self.pattern, 'Antoine Beaupré <anarcat@orangeseeds.org>', 'nobody@example.com', 'nobody@example.com')

    def test_cleanup_uids(self):
        """test if we can properly remove irrelevant UIDs"""
        for fpr, key in self.email.tmpkeyring.get_keys('7B75921E').iteritems():
            for u, uid in key.uids.iteritems():
                self.assertEqual(self.email.recipient, uid.uid)

    def test_mail_key(self):
        """test if we can generate a mail with a key inside"""
        message = self.email.create_mail_from_block()
        match = re.compile("""Content-Type: multipart/mixed; boundary="===============[0-9]*=="
MIME-Version: 1.0

--===============[0-9]*==
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: quoted-printable

%s
--===============[0-9]*==
Content-Type: application/pgp-keys; name="signed-7B75921E.asc"
MIME-Version: 1.0
Content-Disposition: attachment; filename="signed-7B75921E.asc"
Content-Transfer-Encoding: 7bit
Content-Description: =\?utf-8\?q\?signed_OpenPGP_Key_7B75921E.*

-----BEGIN PGP PUBLIC KEY BLOCK-----
.*
-----END PGP PUBLIC KEY BLOCK-----

--===============[0-9]*==--""" % (self.email.body), re.DOTALL)
        self.assertRegexpMatches(message.as_string(), match)
        return message

    def test_wrap_crypted_mail(self):
        match = re.compile("""Content-Type: multipart/encrypted; protocol="application/pgp-encrypted";
 boundary="===============%s=="
MIME-Version: 1.0
Subject: .*
From: nobody@example.com
To: nobody@example.com

This is a multi-part message in OpenPGP/MIME format...
--===============%s==
Content-Type: application/pgp-encrypted; filename="signedkey.msg"
MIME-Version: 1.0
Content-Disposition: attachment; filename="signedkey.msg"

Version: 1
--===============%s==
Content-Type: application/octet-stream; filename="msg.asc"
MIME-Version: 1.0
Content-Disposition: inline; filename="msg.asc"
Content-Transfer-Encoding: 7bit

-----BEGIN PGP MESSAGE-----
.*
-----END PGP MESSAGE-----

--===============%s==--""" % tuple(['[0-9]*'] * 4), re.DOTALL)
        self.assertRegexpMatches(self.email.as_string(), match)

    def test_weird_from(self):
        """make sure we don't end up with spaces in our email address"""
        self.email = EmailFactory(self.ui.tmpkeyring.export_data(self.pattern), self.pattern, 'Antoine Beaupré <anarcat@orangeseeds.org>', 'Antoine Beaupré (home address) <anarcat@anarcat.ath.cx>', 'nobody@example.com')
        match = re.compile("""From: (([^ ]* )|("[^"]*" ))?<[^> ]*>$""", re.DOTALL | re.MULTILINE)
        self.assertRegexpMatches(self.email.as_string(), match)

class FakeKeyringTests(BaseTestCase):
    args = []
    pattern = '96F47C6A'

    def setUp(self):
        """we setup a fake keyring with the public key to sign and add our private keys"""
        BaseTestCase.setUp(self)
        self.ui.keyring.import_data(open(find_test_file('96F47C6A.asc')).read())

    def test_find_key(self):
        """test if we can find a key on the local keyring"""
        self.ui.find_key()


@skipUnlessNetwork()
class NonExistentKeyTests(BaseTestCase, test_lib.TestTimeLimit):
    """test behavior with a key that can't be found"""

    args = []
    # odds that a key with all zeros as fpr are low, unless something happens between PGP and bitcoins...
    pattern = '0000000000000000000000000000000000000000'

    def test_find_key(self):
        """find_key() should exit if the key can't be found on keyservers or local keyring"""
        try:
            with self.assertRaises(SystemExit):
                self.ui.find_key()
        except test_lib.AlarmException:
            raise unittest.case._ExpectedFailure(sys.exc_info())


@skipUnlessNetwork()
class KeyserverTests(BaseTestCase):
    args = ['--keyserver', 'pool.sks-keyservers.net']
    pattern = '7B75921E'

    def test_find_key(self):
        """this should find the key on the keyservers"""
        self.ui.find_key()


if __name__ == '__main__':
    unittest.main()

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
Native Python / GPG API

This API was written to replace the GPGME bindings because the GPGME
API has a few problems:

 1. it is arcane and difficult to grasp
 2. it is very closely bound to the internal GPG data and commandline
    structures, which are quite confusing
 3. GPGME doesn't actually talk to a GPG library, but interacts with
    GPG through the commandline
 4. GPGME developers are not willing to extend GPGME to cover private
    key material management and consider this is outside the scope of
    the project.

The latter two points are especially problematic for this project, and
I have therefore started working on a replacement.

Operations are performed mostly through the Keyring or KeyringTmp
class (if you do not want to access your regular keyring but an empty
temporary one).

This is how you can access keys, which are represented by the
OpenPGPkey datastructure, but which will not look in your keyring or
on the keyservers itself without the Keyring class.

It seems that I have missed a similar project that's been around for
quite a while (2008-2012):

https://code.google.com/p/python-gnupg/

The above project has a lot of similarities with this implementation,
but is better because:

 1. it actually parses most status outputs from GPG, in a clean way
 2. uses threads so it doesn't block
 3. supports streams
 4. supports verification, key generation and deletion
 5. has a cleaner and more complete test suite

However, the implementation here has:

 1. key signing support
 2. a cleaner API

Error handling is somewhat inconsistent here. Some functions rely on
exceptions, other on boolean return values. We prefer exceptions as it
allows us to propagate error messages to the UI, but make sure to
generate a RuntimeError, and not a ProtocolError, which are unreadable
to the user.
"""

import errno
import os, tempfile, shutil, subprocess, re
from datetime import datetime

from StringIO import StringIO

import monkeysign.translation

class Context():
    """Python wrapper for GnuPG

    This wrapper allows for a simpler interface than GPGME or PyME to
    GPG, and bypasses completely GPGME to interoperate directly with
    GPG as a process.

    It uses the gpg-agent to prompt for passphrases and communicates
    with GPG over the stdin for commnads (--command-fd) and stdout for
    status (--status-fd).
    """

    # the gpg binary to call
    gpg_binary = 'gpg'

    # a list of key => value commandline options
    #
    # to pass a flag without options, use None as the value
    options = { 'status-fd': 2,
                'command-fd': 0,
                'no-tty': None,
                'quiet': None,
                'batch': None,
                'use-agent': None,
                'with-colons': None,
                'with-fingerprint': None,
                'fixed-list-mode': None,
                'no-verbose': None,
                'list-options': 'show-sig-subpackets,show-uid-validity,show-unusable-uids,show-unusable-subkeys,show-keyring,show-sig-expire',
                }

    # whether to paste output here and there
    # if not false, needs to be a file descriptor
    debug = False

    def __init__(self):
        self.options = dict(Context.options) # copy

    def set_option(self, option, value = None):
        """set an option to pass to gpg

        this adds the given 'option' commandline argument with the
        value 'value'. to pass a flag without an argument, use 'None'
        for value
        """
        self.options[option] = value

    def unset_option(self, option):
        """remove an option from the gpg commandline"""
        if option in self.options:
            del self.options[option]
        else:
            return False

    def build_command(self, command):
        """internal helper to build a proper gpg commandline

        this will add relevant arguments around the gpg binary.

        like the options arguments, the command is expected to be a
        regular gpg command with the -- stripped. the -- are added
        before being called. this is to make the code more readable,
        and eventually support other backends that actually make more
        sense.

        this uses build_command to create a commandline out of the
        'options' dictionary, and appends the provided command at the
        end. this is because order of certain options matter in gpg,
        where some options (like --recv-keys) are expected to be at
        the end.

        it is here that the options dictionary is converted into a
        list. the command argument is expected to be a list of
        arguments that can be converted to strings. if it is not a
        list, it is cast into a list."""
        options = []
        for left, right in self.options.iteritems():
            options += ['--' + left]
            if right is not None:
                options += [str(right)]
        if type(command) is str:
            command = [command]
        if len(command) > 0 and command[0][0:2] != '--':
            command[0] = '--' + command[0]
        return [self.gpg_binary] + options + command

    def call_command(self, command, stdin=None):
        """internal wrapper to call a GPG commandline

        this will call the command generated by build_command() and
        setup a regular pipe to the subcommand.

        this assumes that we have the status-fd on stdout and
        command-fd on stdin, but could really be used in any other
        way.

        we pass the stdin argument in the standard input of gpg and we
        keep the output in the stdout and stderr array. the exit code
        is in the returncode variable.

        we can optionnally watch for a confirmation pattern on the
        statusfd.
        """
        proc = subprocess.Popen(self.build_command(command),  # nosec
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (self.stdout, self.stderr) = proc.communicate(stdin)
        self.returncode = proc.returncode
        if self.debug:
            print >>self.debug, 'command:', self.build_command(command)
            print >>self.debug, 'ret:', self.returncode, 'stdout:', self.stdout, 'stderr:', self.stderr
        return proc.returncode == 0

    def seek_pattern(self, fd, pattern):
        """iterate over file descriptor until certain pattern is found

        fd is a file descriptor
        pattern a string describing a regular expression to match

        this will skip lines not matching pattern until the pattern is
        found. it will raise an IOError if the pattern is not found
        and EOF is reached.

        this may hang for streams that do not send EOF or are waiting
        for input.
        """
        line = fd.readline()
        match = re.search(pattern, line)
        while line and not match:
            if self.debug: print >>self.debug, "skipped:", line,
            line = fd.readline()
            match = re.search(pattern, line)
        if match:
            if self.debug: print >>self.debug, "FOUND:", line,
            return match
        else:
            raise GpgProtocolError(self.returncode, _("could not find pattern '%s' in input, last skipped '%s'") % (pattern, line))

    def seek(self, fd, pattern):
        """look for a specific GNUPG status line in the output

        this is a stub for seek_pattern()
        """
        return self.seek_pattern(fd, '^\[GNUPG:\] ' + pattern)

    def expect_pattern(self, fd, pattern):
        """make sure the next line matches the provided pattern

        in contrast with seek_pattern(), this will *not* skip
        non-matching lines and instead raise an exception if such a
        line is found.

        this therefore looks only at the next line, but may also hang
        like seek_pattern()

        if the beginning of the line matches a pattern which is
        being ignored, it will skip it and look at the next line
        """
        line = fd.readline()
        ignored = ('[GNUPG:] KEYEXPIRED', '[GNUPG:] SIGEXPIRED', '[GNUPG:] KEY_CONSIDERED', 'gpg: ')

        while line and line.startswith(ignored):
            if self.debug: print >>self.debug, "IGNORED:", line,
            line = fd.readline()

        match = re.search(pattern, line)

        if self.debug:
            if match: print >>self.debug, "FOUND:", line,
            else: print >>self.debug, "SKIPPED:", line,
        if not match:
            raise GpgProtocolError(self.returncode, 'expected "%s", found "%s"' % (pattern, line))
        return match

    def expect(self, fd, pattern):
        """look for a specific GNUPG status on the next line of output

        this is a stub for expect()
        """
        return self.expect_pattern(fd, '^\[GNUPG:\] ' + pattern)

    def write(self, fd, message):
        """write the specified message to gnupg, usually on stdout

        but really, the pipes are often setup outside of here so the
        fd is hardcoded here
        """
        if self.debug:
            print >>self.debug, "WROTE:", message
        print >>fd, message

    def version(self):
        """return the version of the GPG binary"""
        self.call_command(['version'])
        m = re.search('gpg \(GnuPG\) (\d+.\d+(?:.\d+)*)', self.stdout)
        return m.group(1)

class Keyring():
    """Keyring functionalities.

    This allows various operations (e.g. listing, signing, exporting
    data) on a keyring.

    Concretely, we talk about a "keyring", but we really mean a set of
    public and private keyrings and their trust databases. In
    practice, this is the equivalent of the GNUPGHOME or --homedir in
    GPG, and in fact this is implemented by setting a specific homedir
    to tell GPG to operate on a specific keyring.

    We actually use the --homedir parameter to gpg to set the keyring
    we operate upon.
    """

    # the context this keyring is associated with
    context = None

    def __init__(self, homedir=None):
        """constructor for the gpg context

        this mostly sets options, and allows passing in a different
        homedir, that will be added to the option right here and
        there.

        by default, we do not create or destroy the keyring, although
        later function calls on the object may modify the keyring (or
        other keyrings, if the homedir option is modified.
        """
        self.context = Context()
        if homedir is not None:
            self.context.set_option('homedir', homedir)
        else:
            homedir = os.path.join(os.path.expanduser("~"), '.gnupg')
            if 'GNUPGHOME' in os.environ:
                homedir = os.environ['GNUPGHOME']
        self.homedir = homedir

    def get_agent_socket(self):
        """get the location of the gpg-agent socket for this keyring"""
        try:
            command = ['gpgconf', '--homedir', self.homedir,
                       '--list-dirs', 'agent-socket']
            # silence errors
            conf = subprocess.check_output(command,
                                           stderr=subprocess.PIPE).rstrip()
        # if we can't find gpgconf at all, assume the agent is in the
        # homedir
        except OSError as e:
            if e.errno == errno.ENOENT:
                conf = self.homedir + '/S.gpg-agent'
        # GnuPG before 2.1.13 doesn't suport --homedir and will exit
        # with an error. assume the agent is in the homedir in that
        # case as well
        except subprocess.CalledProcessError as e:
            conf = self.homedir + '/S.gpg-agent'
        return conf.rstrip()

    def import_data(self, data):
        """Import OpenPGP data blocks into the keyring.

        This takes actual OpenPGP data, ascii-armored or not, gpg will
        gladly take it. This can be signatures, public, private keys,
        etc.

        You may need to set import-flags to import non-exportable
        signatures, however.
        """
        self.context.call_command(['import'], data)
        fd = StringIO(self.context.stderr)
        try:
            self.context.seek(fd, 'IMPORT_OK')
            self.context.seek(fd, 'IMPORT_RES')
        except GpgProtocolError:
            return False
        return True

    def export_data(self, fpr = None, secret = False):
        """Export OpenPGP data blocks from the keyring.

        This exports actual OpenPGP data, by default in binary format,
        but can also be exported asci-armored by setting the 'armor'
        option."""
        self.context.set_option('armor')
        if secret: command = ['export-secret-keys']
        else: command = ['export']
        if fpr: command += [fpr]
        self.context.call_command(command)
        return self.context.stdout

    def verify_file(self, sigfile, filename):
        self.context.call_command(['verify', sigfile, filename])
        fd = StringIO(self.context.stderr)
        try:
            self.context.seek(fd, 'VALIDSIG')
        except GpgProtocolError:
            raise GpgRuntimeError(self.context.returncode, _('verifying file %s failed: %s.') % (filename, self.context.stderr.decode('utf-8')))
        return True

    def fetch_keys(self, fpr, keyserver = None):
        """Download keys from a keyserver into the local keyring

        This expects a fingerprint (or a at least a key id).

        Returns true if the command succeeded.
        """
        if keyserver is not None:
            self.context.set_option('keyserver', keyserver)
        self.context.call_command(['recv-keys', fpr])
        return self.context.returncode == 0

    def get_keys(self, pattern=None, secret=False, public=True, keys=None):
        """load keys matching a specific patterns

        this uses the (rather poor) list-keys API to load keys
        information
        """
        if keys is None:
            keys = {}
        if secret:
            command = ['list-secret-keys']
            if pattern: command += [pattern]
            self.context.call_command(command)
            if self.context.returncode == 0:
                needle = 'sec:'
                for keydata in self.context.stdout.split(needle):
                    if not keydata: continue
                    keydata = needle + keydata
                    key = OpenPGPkey(keydata)
                    # check if we already have that key, in which case we
                    # add to it instead of adding a new key
                    if key.fpr in keys:
                        keys[key.fpr].parse_gpg_list(self.context.stdout)
                        del key
                    else:
                        keys[key.fpr] = key
            elif self.context.returncode == 2:
                return None
            else:
                raise GpgProtocolError(self.context.returncode, _('unexpected GPG exit code in list-keys: %d') % self.context.returncode)
        if public:
            command = ['list-keys']
            if pattern: command += [pattern]
            self.context.call_command(command)
            if self.context.returncode == 0:
                # discard trustdb data, first line of output
                self.context.stdout = "\n".join(self.context.stdout.split("\n")[1:])
                for keydata in self.context.stdout.split("pub:"):
                    if not keydata: continue
                    keydata = "pub:" + keydata
                    key = OpenPGPkey(keydata)
                    # check if we already have that key, in which case we
                    # add to it instead of adding a new key
                    if key.fpr in keys:
                        keys[key.fpr].parse_gpg_list(self.context.stdout)
                        del key
                    else:
                        keys[key.fpr] = key
            elif self.context.returncode == 2:
                return None
            else:
                raise GpgProtocolError(self.context.returncode, _('unexpected GPG exit code in list-keys: %d') % self.context.returncode)
        if secret:
            # workaround for bug in GPG < 2.1 where revocation
            # information is not correctly populated in
            # --list-secret-keys --with-colons
            for fpr, key in keys.items():
                if key.get_trust() == 'empty':
                    self.get_keys(fpr, secret=False, public=True, keys=keys)
        return keys

    def encrypt_data(self, data, recipient):
        """encrypt data using asymetric encryption

        returns the encrypted data or raise a GpgRuntimeError if it fails
        """
        self.context.call_command(['recipient', recipient, '--encrypt'], data)
        if self.context.returncode == 0:
            return self.context.stdout
        else:
            raise GpgRuntimeError(self.context.returncode, _('encryption to %s failed: %s.') % (recipient, self.context.stderr.split("\n")[-2]))

    def decrypt_data(self, data):
        """decrypt data using asymetric encryption

        returns the plaintext data or raise a GpgRuntimeError if it failed.
        """
        self.context.call_command(['--decrypt'], data)
        if self.context.returncode == 0:
            return self.context.stdout
        else:
            raise GpgRuntimeError(self.context.returncode, _('decryption failed: %s') % self.context.stderr.split("\n")[-2])

    def del_uid(self, fingerprint, pattern):
        command = self.context.build_command(['edit-key', fingerprint])
        if self.context.debug:
            print >>self.context.debug, 'command:', command
        proc = subprocess.Popen(command,  # nosec
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        # start copy-paste from sign_key()
        self.context.expect(proc.stderr, 'GET_LINE keyedit.prompt')
        while True:
            m = self.context.seek_pattern(proc.stdout, '^uid:.::::::::([^:]*):::[^:]*:(\d+),[^:]*:')
            if m and m.group(1) == pattern:
                index = int(m.group(2))
                break
        self.context.write(proc.stdin, str(index))
        self.context.expect(proc.stderr, 'GOT_IT')
        self.context.expect(proc.stderr, 'GET_LINE keyedit.prompt')
        # end of copy-paste from sign_key()
        self.context.write(proc.stdin, 'deluid')
        self.context.expect(proc.stderr, 'GOT_IT')
        self.context.expect(proc.stderr, 'GET_BOOL keyedit.remove.uid.okay')
        self.context.write(proc.stdin, 'y')
        self.context.expect(proc.stderr, 'GOT_IT')
        self.context.expect(proc.stderr, 'GET_LINE keyedit.prompt')
        self.context.write(proc.stdin, 'save')
        self.context.expect(proc.stderr, 'GOT_IT')
        return proc.wait() == 0

    def sign_key(self, pattern, signall = False, local = False):
        """sign a OpenPGP public key

        By default it looks up and signs a specific uid, but it can
        also sign all uids in one shot thanks to GPG's optimization on
        that.

        The pattern here should be a full user id if we sign a
        specific key (default) or any pattern (fingerprint, keyid,
        partial user id) that GPG will accept if we sign all uids.

        @todo that this currently block if the pattern specifies an
        incomplete UID and we do not sign all keys.
        """

        # we iterate over the keys matching the provided
        # keyid, but we should really load those uids from the
        # output of --sign-key
        command = self.context.build_command([['sign-key',
                                               'lsign-key'][local], pattern])
        if self.context.debug:
            print >>self.context.debug, 'command:', command
        proc = subprocess.Popen(command,  # nosec
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        # if there are multiple uids to sign, we'll get this point, and a whole other interface
        try:
            multiuid = self.context.expect(proc.stderr, 'GET_BOOL keyedit.sign_all.okay')
        except GpgProtocolError as e:
            if 'sign_uid.okay' in str(e):
                multiuid = False
            else:
                raise GpgRuntimeError(self.context.returncode, _('cannot select uid for signing: %s') % e.found().decode('utf-8'))
        if multiuid:
            if signall: # special case, sign all keys
                self.context.write(proc.stdin, "y")
                self.context.expect(proc.stderr, 'GOT_IT')
                # confirm signature
                try:
                    self.context.expect(proc.stderr, 'GET_BOOL sign_uid.okay')
                except GpgProtocolError as e:
                    if 'ALREADY_SIGNED' in str(e) or 'sign_uid.dupe_okay' in str(e):
                        raise GpgRuntimeError(self.context.returncode, _('you already signed that key'))
                    else:
                        # propagate gpg error message up
                        raise GpgRuntimeError(self.context.returncode, _('unable to confirm key signing: %s') % e.found().decode('utf-8'))
                self.context.write(proc.stdin, 'y')
                self.context.expect(proc.stderr, 'GOT_IT')
                # expect the passphrase confirmation
                # we seek because i have seen a USERID_HINT <keyid> <uid> in some cases
                try:
                    self.context.seek(proc.stderr, 'GOOD_PASSPHRASE')
                except GpgProtocolError:
                    # GnuPG 2.1 stopped outputing GOOD_PASSPHRASE, so try our luck at just waiting for output
                    self.context.returncode = proc.wait()
                    if self.context.returncode == 0:
                        return True
                    else:
                        raise GpgRuntimeError(self.context.returncode, _('unable to prompt for passphrase, is gpg-agent running?'))
                return proc.wait() == 0

            # don't sign all uids
            self.context.write(proc.stdin, "n")
            self.context.expect(proc.stderr, 'GOT_IT')
            # select the uid
            self.context.expect(proc.stderr, 'GET_LINE keyedit.prompt')
            while True:
                # XXX: this will hang if the pattern requested is not found, we need a better way!
                m = self.context.seek_pattern(proc.stdout, '^uid:.::::::::([^:]*):::[^:]*:(\d+),[^:]*:')
                if m and m.group(1) == pattern:
                    index = int(m.group(2))
                    break
            self.context.write(proc.stdin, str(index))
            self.context.expect(proc.stderr, 'GOT_IT')
            # sign the selected uid
            self.context.seek(proc.stderr, 'GET_LINE keyedit.prompt')
            self.context.write(proc.stdin, "sign")
            self.context.expect(proc.stderr, 'GOT_IT')
            # confirm signature
            try:
                self.context.expect(proc.stderr, 'GET_BOOL sign_uid.okay')
            except GpgProtocolError as e:
                # propagate gpg error message up
                raise GpgRuntimeError(self.context.returncode, _('unable to confirm signing one key: %s') % e.found().decode('utf-8'))

        # we fallthrough here if there's only one key to sign
        self.context.write(proc.stdin, 'y')

        try:
            self.context.expect(proc.stderr, 'GOT_IT')
        except GpgProtocolError as e:
            # deal with expired keys
            # XXX: weird that this happens here and not earlier
            if 'EXPIRED' in str(e):
                raise GpgRuntimeError(self.context.returncode, _('key is expired, cannot sign'))
            else:
                raise GpgRuntimeError(self.context.returncode, _('unable to signing a single key: %s') % e.found().decode('utf-8') + proc.stderr.read())
        if multiuid:
            self.context.write(proc.stdin, "save")
        # expect the passphrase confirmation
        try:
            self.context.seek(proc.stderr, 'GOOD_PASSPHRASE')
        except GpgProtocolError:
            # GnuPG 2.1 stopped outputing GOOD_PASSPHRASE, so try our luck at just waiting for output
            self.context.returncode = proc.wait()
            if self.context.returncode == 0:
                return True
            else:
                raise GpgRuntimeError(self.context.returncode, _('password confirmation failed'))
        if multiuid:
            # we save the resulting key in uid selection mode
            self.context.expect(proc.stderr, 'GET_LINE keyedit.prompt')
            self.context.expect(proc.stderr, 'GOT_IT')
        return proc.wait() == 0

class TempKeyring(Keyring):
    def __init__(self):
        """Override the parent class to generate a temporary GPG home
        that gets destroyed at the end of operations."""
        Keyring.__init__(self, tempfile.mkdtemp(prefix="pygpg-"))

    def __del__(self):
        shutil.rmtree(self.homedir, ignore_errors=True)

class OpenPGPkey():
    """An OpenPGP key.

    Some of this datastructure is taken verbatim from GPGME.
    """

    @property
    def revoked(self):
        '''Returns whether GnuPG thinks the key has been revoked

        This is the second field of the result of the --list-key --with-colons
        call.  Note that this information is only present on public keys,
        i.e. not on secret keys.

        Returns None if it cannot be determined whether this key has
        been revoked.'''
        if self.trust == '':
            # We cannot determine whether this key has been revoked.
            # Locate the public key and try again.
            is_revoked = None
        elif self.trust == 'r':
            is_revoked = True
        else:
            is_revoked = False
            
        return is_revoked

    @property
    def expired(self):
        if not self.expiry:
            ret = False
        else:
            ret = datetime.now() > self.expiry
        return ret

    # the key has been disabled
    # @todo - not implemented
    disabled = False

    # ?
    invalid = False

    # the various flags on this key
    purpose = {}

    # This is true if the subkey can be used for qualified
    # signatures according to local government regulations.
    # @todo - not implemented
    qualified = False

    # this key has also secret key material
    secret = False

    # This is the public key algorithm supported by this subkey.
    algo = -1

    # This is the length of the subkey (in bits).
    length = None

    # The key fingerprint (a string representation)
    fpr = None

    # The key id (a string representation), only if the fingerprint is unavailable
    # use keyid() instead of this field to find the keyid
    _keyid = None

    # This is the creation timestamp of the subkey.  This is -1 if
    # the timestamp is invalid, and 0 if it is not available.
    creation = 0

    # This is the expiration timestamp of the subkey, or 0 if the
    # subkey does not expire.
    _expiry = 0
    
    @property
    def expiry(self):
        """Returns a datetime from the _expiry field or None if
        the key does not expire"""
        if self._expiry:
            expiry = int(self._expiry)
            if expiry > 0:
                result = datetime.fromtimestamp(expiry)
            else:
                result = None
        elif self._expiry == '':
                result = None
        else:
            raise ValueError("Expiry is %r but we expected an int or string",
                             self._expiry)
        return result

    # single-character trust status, see trust_map below for parsing
    trust = None

    # the list of OpenPGPuids associated with this key
    uids = {}

    # the list of subkeys associated with this key
    subkeys = {}

    trust_map = {'o': 'new', # this key is new to the system
                 'i': 'invalid', # The key is invalid (e.g. due to a
                                 # missing self-signature)
                 'd': 'disabled', # The key has been disabled
                                  # (deprecated - use the 'D' in field
                                  # 12 instead)
                 'r': 'revoked', # The key has been revoked
                 'e': 'expired', # The key has expired
                 '-': 'unknown', # Unknown trust (i.e. no value
                                 # assigned)
                 'q': 'undefined', # Undefined trust, '-' and 'q' may
                                   # safely be treated as the same
                                   # value for most purposes
                 'n': 'none', # Don't trust this key at all
                 'm': 'marginal', # There is marginal trust in this key
                 'f': 'full', # The key is fully trusted
                 'u': 'ultimate', # The key is ultimately trusted.
                                  # This often means that the secret
                                  # key is available, but any key may
                                  # be marked as ultimately trusted.
                 '': 'empty',  # trust value was not communicated by gpg
                               # this is a bug in gpg 2.1: secret keys do
                               # not have trust information attached
                 }

    def __init__(self, data=None):
        self.purpose = { 'encrypt': True, # if the public key part can be used to encrypt data
                         'sign': True,    # if the private key part can be used to sign data
                         'certify': True, # if the private key part can be used to sign other keys
                         'authenticate': True, # if this key can be used for authentication purposes
                         }
        self.uids = {}
        self.subkeys = {}
        if data is not None:
            self.parse_gpg_list(data)

    def keyid(self, l=8):
        if self.fpr is None:
            assert(self._keyid is not None)  # nosec
            return self._keyid[-l:]
        return self.fpr[-l:]

    def get_trust(self):
        return OpenPGPkey.trust_map[self.trust]

    def parse_gpg_list(self, text):
        uidslist = []
        for block in text.split("\n"):
            record = block.split(":")
            #for block in record:
            #        print >>sys.stderr, block, "|\t",
            #print >>sys.stderr, "\n"
            rectype = record[0]
            if rectype == 'tru':
                (rectype, trust, selflen, algo, keyid, creation, expiry, serial) = record[:8]
            elif rectype == 'fpr':
                if not self.fpr:
                    self.fpr = record[9]
            elif rectype == 'pub':
                (null, self.trust, self.length, self.algo, keyid, self.creation, self._expiry, serial, trust, uid, sigclass, purpose, smime) = record[:13]
                for p in self.purpose:
                    self.purpose[p] = p[0].lower() in purpose.lower()
            elif rectype == 'uid':
                (rectype, trust, null, null, null, creation, expiry, uidhash, null, uid) = record[:10]
                uid = OpenPGPuid(uid, trust, creation, expiry, uidhash)
                self.uids[uidhash] = uid
                uidslist.append(uid)
            elif rectype == 'sub':
                subkey = OpenPGPkey()
                (rectype, trust, subkey.length, subkey.algo, subkey._keyid, subkey.creation, subkey._expiry, serial, trust, uid, sigclass, purpose, smime) = record[:13]
                for p in subkey.purpose:
                    subkey.purpose[p] = p[0].lower() in purpose.lower()
                self.subkeys[subkey._keyid] = subkey
            elif rectype == 'sec':
                (null, self.trust, self.length, self.algo, keyid, self.creation, self._expiry, serial, trust, uid, sigclass, purpose, smime) = record[:13]
                self.secret = True
            elif rectype == 'ssb':
                subkey = OpenPGPkey()
                (rectype, trust, subkey.length, subkey.algo, subkey._keyid, subkey.creation, subkey._expiry, serial, trust, uid, sigclass, purpose, smime) = record[:13]
                if subkey._keyid in self.subkeys:
                    # XXX: nothing else to add here?
                    self.subkeys[subkey._keyid].secret = True
                else:
                    self.subkeys[subkey._keyid] = subkey
            elif rectype == 'uat':
                pass # user attributes, ignore for now
            elif rectype == 'rvk':
                pass # revocation key, ignored for now
            elif rectype == '':
                pass
            else:
                # XXX: need to log this
                #raise NotImplementedError(_("record type '%s' not implemented") % rectype)
                pass  # ignore unknown records for forward-compatibilty
        self.uidslist = uidslist


    def __str__(self):
        ret = u'pub  [%s] %sR/' % (self.get_trust(), self.length)
        ret += self.keyid(8) + u" " + self.creation
        if self._expiry: ret += u' [expiry: ' + str(self.expiry) + ']'
        ret += u"\n"
        ret += u'    Fingerprint = ' + self.format_fpr() + "\n"
        i = 1
        for uid in self.uidslist:
            ret += u"uid %d      [%s] %s\n" % (i, uid.get_trust(), uid.uid.decode('utf-8', 'replace'))
            i += 1
        for subkey in self.subkeys.values():
            ret += u"sub   " + subkey.length + u"R/" + subkey.keyid(8) + u" " + subkey.creation
            if subkey._expiry: ret += u' [expiry: ' + str(subkey.expiry) + "]"
            ret += u"\n"
        return ret


    def __repr__(self):
        s = '<OpenPGPkey(%s UIDs:%d)>'
        s %= (self.fpr,  len(self.uidslist))
        
        return s


    def format_fpr(self):
        """display a clean version of the fingerprint

        this is the display we usually see
        """
        l = list(self.fpr) # explode
        s = ''
        for i in range(10):
            # output 4 chars
            s += ''.join(l[4*i:4*i+4])
            # add a space, except at the end
            if i < 9: s += ' '
            # add an extra space in the middle
            if i == 4: s += ' '
        return s

    def __eq__(self, other):
        """
        Two keys are equal if their fingerprint matches. If either don't
        have a fingerprint, we can't say for sure that they're equal
        """
        if isinstance(other, self.__class__):
            return (self.fpr and
                    self.fpr and other.fpr
                    and self.fpr == other.fpr)
        else:
            return NotImplemented

    def __neq__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        else:
            return NotImplemented


class OpenPGPuid():
    def __init__(self, uid, trust, creation = 0, expire = None, uidhash = ''):
        self.uid = uid
        self.trust = trust
        self.creation = creation
        self.expire = expire
        self.uidhash = uidhash

    @property
    def revoked(self):
        '''Whether this UID has been revoked

        Note that, due to GnuPG not exporting that information
        for secret keys, UIDs of secret keys do not carry that
        information.

        Return None if it cannot be determined whether this UID
        has been revoked.  Try again with the public key.'''
        if self.trust == '':
            is_revoked = None
        elif self.trust == 'r':
            is_revoked = True
        else:
            is_revoked = False
        return is_revoked

    def get_trust(self):
        return OpenPGPkey.trust_map[self.trust]

    def __repr__(self):
        s = '<OpenPGPuid(%s) [%s:%s:%s]>' 
        s %= (self.uid, self.trust, self.creation, self.expire)

        return s


class GpgProtocolError(IOError):
    """simple exception raised when we have trouble talking with GPG

    we try to pass the subprocess.popen.returncode as an errorno and a
    significant description string

    this error shouldn't be propagated to the user, because it will
    contain mostly "expect" jargon from the DETAILS.txt file. the gpg
    module should instead raise a GpgRutimeError with a user-readable
    error message (e.g. "key not found").
    """

    def match(self):
        return re.search(r'(?:\[Errno [0-9]*\] )?expected "([^"]*)", found "(.*)\n*"', str(self))

    def found(self):
        if self.match():
            return self.match().group(2)
        else:
            return '<no error found in GPG output>'

    def expected(self):
        if self.match():
            return self.match().group(1)
        else:
            return '<not waiting for pattern>'

class GpgRuntimeError(IOError):
    pass

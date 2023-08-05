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

import monkeysign
# gpg interface
from monkeysign.gpg import Keyring, TempKeyring, GpgRuntimeError, Context
import monkeysign.translation

import errno
# mail functions
from email.mime.multipart import MIMEMultipart
from email.mime.message import MIMEMessage
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
from email import Charset
import smtplib
import subprocess  # nosec

# system libraries
import argparse
import errno
import getpass
import os
import platform
import sys
import re
import shlex
try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote
import shutil
import socket
import socks
import tempfile


class RunTests(argparse._VersionAction):
    '''argparse Action handler to run tests

    we want to run them immediately because we don't want to force
    users to provide a pattern.

    '''

    def __call__(self, parser, namespace, values, option_string=None):
        '''run the test suite and exit with the number of failures'''
        import unittest
        sys.argv.remove('--test')
        if '--version' in sys.argv:
            sys.argv.remove('--version')
        testdir = os.path.join(os.path.dirname(__file__), 'tests')
        suite = unittest.TestLoader().discover(testdir)
        results = unittest.TextTestRunner().run(suite)
        parser.exit(len(results.errors))


class MonkeysignArgumentParser(argparse.ArgumentParser):
    # config files, in priority order (first is higher)
    configs = ['~/.config/monkeysign.conf', '/etc/monkeysign.conf']

    # standard header that needs to be present in the config file for
    # us to rewrite it
    header = """# this file was created by monkeysign
# comments will be lost on next write"""

    # those parameters will not be saved to the config file
    ephemeral = ['save', 'version', 'help', 'pattern', 'to', 'test']

    def __init__(self,
                 prog=None, usage=None, description=None, epilog=None,
                 parents=[], formatter_class=argparse.HelpFormatter,
                 prefix_chars='-', fromfile_prefix_chars=None,
                 argument_default=None, conflict_handler='error',
                 add_help=True, allow_abbrev=True,
                 ui=None):
        """create a standard commandline parser based on the given class
        documentation"""

        if ui is None:
            # mock object:
            ui = MonkeysignUi(args=[])

        argparse.ArgumentParser.__init__(self, description=ui.__doc__,
                                         usage=ui.usage,
                                         epilog=ui.epilog
                                         % " or ".join(self.configs),
                                         fromfile_prefix_chars='@',
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
        self.add_argument('--version', action='version',
                            version="\n".join(ui.sysinfo()))
        self.add_argument('-d', '--debug', action='store_true',
                            help=_('request debugging information from GPG '
                                   'engine (lots of garbage)'))
        self.add_argument('-v', '--verbose', action='store_true',
                            help=_('explain what we do along the way'))
        self.add_argument('-n', '--dry-run', dest='dryrun', action='store_true',
                            help=_('do not actually do anything'))
        self.add_argument('--test', action=RunTests,
                          help=_('run test suite, exit with the number of failing tests'))
        self.add_argument('-u', '--user', nargs='+',
                            help=_('user id to sign the key with (equivalent '
                                   'to GPG\'s --local-user option)'))
        self.add_argument('--certlevel', '--cert-level',
                            help=_('certification level to sign the key with '
                                   '(equivalent to GPG\'s '
                                   '--default-cert-level)'))
        self.add_argument('-l', '--local', action='store_true',
                            help=_('import in normal keyring a local '
                                   'certification'))
        self.add_argument('-k', '--keyserver',
                            help=_('keyserver to fetch keys from'))
        self.add_argument('--tor', action='store_true',
                          help=_('use Tor to get keys and send email'))
        self.add_argument('--socks', metavar='HOST[:PORT]',
                          help=_('connect to SOCKS proxy'))
        self.add_argument('-s', '--smtpserver', '--smtp',
                            help=_('SMTP server to use, use a colon to specify '
                                   'the port number if non-default (%(port)d).'
                                   ' willl attempt to use STARTTLS to secure '
                                   'the connexion and fail if unsupported '
                                   '(default: deliver using the --mta '
                                   'command)') %
                            {'port': smtplib.SMTP_PORT})
        self.add_argument('--tls', action='store_true',
                            help=_('use a complete TLS connexion instead of '
                                   'using STARTTLS to upgrade the connexion. '
                                   'will change the default SMTP port to '
                                   '%(port)d')
                            % {'port': smtplib.SMTP_SSL_PORT})
        self.add_argument('--smtpuser',
                            help=_('username for the SMTP server '
                                   '(default: no user)'))
        self.add_argument('--smtppass',
                            help=_('password for the SMTP server '
                                   '(default: prompted, if --smtpuser is '
                                   'specified)'))
        self.add_argument('--mta', default="/usr/sbin/sendmail -t",
                            help=_('command to use to send mail, recipient is '
                                   'passed on the commandline in the "%%(to)s"'
                                   ' field, or the command must parse the '
                                   '"To:" header (default: %(default)s)'))
        default_mua = "xdg-email --utf8 --to '%(to)s' --subject '%(subject)s' --body '%(body)s' --attach '%(attach)s'"
        self.add_argument('--mua', nargs='?', default=None, const=default_mua,
                          help=_('Mail User Agent to use to send mail. all '
                                 'parameters are passed on the commandline,'
                                 'overrides --mta. '
                                 '(default: %(const)s when specified)'))
        self.add_argument('--nomail', '--no-mail', action='store_true',
                            help=_('do not send email at all'))
        self.add_argument('-t', '--to',
                            help=_('override destination email for testing '
                                   '(default: send individually encrypted '
                                   'email to each uid chosen)'))
        self.add_argument('--save', action='store_true',
                          help=_('save the given commandline parameters to the config file'))
        if 'cli' in ui.__class__.__name__.lower():
            nargs = '+'
        else:
            nargs = '*'
        self.add_argument('pattern', nargs=nargs,
                            help=_('pattern of the key to sign (fingerprint,'
                                   ' user id, etc)'))

    def convert_arg_line_to_args(self, arg_line):
        """parse a config file"""
        # skip whitespace and commented lines
        if re.match('^(#|[\s]*$)', arg_line):
            return []
        else:
            # all lines are assumed to be options
            # this is important otherwise an attacker could inject key
            # material in the config file and silently have his key be
            # signed
            return ['--' + arg_line]

    def parse_args(self, args=None, namespace=None):
        """override builtin argument parsing to also parse config files"""
        configs = map(lambda x: os.path.expanduser(x), self.configs)
        for conf in configs:
            try:
                with open(conf, 'r'):
                    if args:
                        args.insert(0, '@' + conf)
                    else:
                        sys.argv.insert(1, '@' + conf)
            except IOError:
                pass
        args = argparse.ArgumentParser.parse_args(self,
                                                  args=args,
                                                  namespace=namespace)
        # XXX: a bit clunky because the cli expects this to be the
        # output of parse_args() while the GTK ui expects this to be
        # populated as a string, later
        if len(args.pattern) < 1:
            args.pattern = None
        else:
            # accept space-separated fingerprints
            args.pattern = "".join(args.pattern)
        # accept space-separated fingerprints for user as well
        if args.user is not None:
            args.user = "".join(args.user)
        if args.save:
            self.save_config(args)
        if args.local:
            args.nomail = True
        if args.tor and args.socks:
            self.error('specify only one of --tor or --socks')
        if args.tor:
            args.socks = 'localhost:9050'
        if args.socks:
            args.socks = args.socks.split(':')
            if len(args.socks) < 2:
                # hardcode default port number
                args.socks += [socks.DEFAULT_PORTS[socks.SOCKS5]]
            args.socks[1] = int(args.socks[1])
            args.socks = tuple(args.socks)
        return args

    def save_config(self, args, config=None, close=True):
        """save given namespace to default configuration file

        config is a filehandle that will be written to. if None, the
        first element in the configs array will be opened and written
        to.

        the config file will not be written to if it doesn't contain
        the magic header

        performs no exception handling. returns True if all is well

        the config file will be closed unless close=False (used for
        unit tests)
        """
        lines = self.args_to_config(args)
        if config is None:
            config = open(os.path.expanduser(self.configs[0]),
                          'w+')
        contents = config.read()
        if len(contents) and self.header not in contents:
            if close:
                config.close()
            return False
        config.truncate(0)
        self.write_config(lines, config)
        if close:
            config.close()
        # self.ui.log() except that we don't have logging yet
        return True

    def args_to_config(self, args):
        """return given namespace as a configuration file"""
        lines = []
        for action in self._actions:
            if action.dest in self.ephemeral:
                continue
            val = vars(args)[action.dest]
            if val != action.default:
                if isinstance(action, argparse._StoreAction):
                    lines.append('%s=%s' % (action.dest, val))
                else:
                    lines.append(action.dest)
        return lines

    def write_config(self, config, fileobj):
        """take the list of lines and write it to the config file

        we implement our own here because:

        1. ConfigParser is not API stable across Py2/3
        2. ConfigParser is unnecessarily hard to use and complex
        3. ConfigParser requires sections which we don't need
        4. alternatives like ConfigObj are not in the standard library
        5. this whole config file writer is about 30 lines long
        """
        return fileobj.write(self.header + "\n" + "\n".join(config) + "\n")


class MonkeysignUi(object):
    """User interface abstraction for monkeysign.

    This aims to factor out a common pattern to sign keys that is used
    regardless of the UI used.

    This is mostly geared at console/text-based and X11 interfaces,
    but could also be ported to other interfaces (touch-screen/phone
    interfaces would be interesting).

    The actual process is in main(), which outlines what the
    subclasses of this should be doing.

    You should have a docstring in derived classes, as it will be
    added to the 'usage' output.
    """

    # what gets presented to the user in the usage (first and last lines)
    # default is to use the OptionParser's defaults
    # the 'docstring' above is the long description
    # XXX: deprecated, argparse is flexible enough that we do not need
    # this anymore
    usage = None
    epilog = """an arbitrary configuration file may also be supplied on the
commandline with a @ prefix (e.g. @foo.conf). the following
configuration files are parsed by default: %s"""

    @classmethod
    def sysinfo(cls):
        info = []
        info.append("Monkeysign: %s" % monkeysign.__version__)
        info.append('Load path: %s'
                    % os.path.realpath(os.path.dirname(__file__)))
        info.append("%s: %s (%s %s)"
                    % (platform.python_implementation(),
                       platform.python_version(),
                       platform.python_compiler(),
                       " ".join(platform.python_build())))
        info.append("Kernel: %s" % " ".join(platform.uname()))
        if 'linux' in platform.system().lower():
            distribution = " ".join(platform.linux_distribution()).rstrip()
        else:
            distribution = ''
        info.append("Operating system: %s (%s)"
                    % (distribution, platform.system()))
        info.append('PID: %d, CWD: %s' % (os.getpid(), os.getcwd()))
        info.append('Command: %r' % sys.argv)
        try:
            info.append('GnuPG: %s' % Context().version())
        except OSError as e:
            if e.errno == errno.ENOENT:
                info.append('GnuPG: error! %s: %s'
                            % (Context.gpg_binary, str(e)))
        return info

    def __init__(self, args = None):
        # the options that determine how we operate, from the parse_args()
        self.options = {}

        # the key we are signing, can be a keyid or a uid pattern
        self.pattern = None

        # the regular keyring we suck secrets and maybe the key to be signed from
        self.keyring = Keyring()

        # the temporary keyring we operate in, actually initialized in prepare()
        # this is because we want the constructor to just initialise
        # data structures and not write any data
        self.tmpkeyring = None

        # the fingerprints that we actually signed
        self.signed_keys = {}

        # temporary, to keep track of the OpenPGPkey we are signing
        self.signing_key = None

        self.parser = MonkeysignArgumentParser(ui=self)
        self.options = self.parser.parse_args(args=args)
        self.pattern = self.options.pattern

        # set a default logging mechanism
        self.logfile = sys.stderr
        self.log(_('Initializing UI'))

        # create the temporary keyring
        # XXX: i would prefer this to be done outside the constructor
        self.prepare()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # this is implicit in the garbage collection, but tell the user anyways
        self.log(_('deleting the temporary keyring %s') % self.tmpkeyring.homedir)

        if exc_type is NotImplementedError:
            self.abort(str(exc_value))

    def prepare(self):
        # initialize the temporary keyring directory
        self.tmpkeyring = TempKeyring()

        if self.options.debug:
            self.tmpkeyring.context.debug = self.logfile
            self.keyring.context.debug = self.logfile
        if self.options.keyserver is not None:
            self.tmpkeyring.context.set_option('keyserver', self.options.keyserver)
        if self.options.user is not None:
            self.tmpkeyring.context.set_option('local-user', self.options.user)
        if self.options.certlevel is not None:
            self.tmpkeyring.context.set_option('default-cert-level', self.options.certlevel)
        self.tmpkeyring.context.set_option('secret-keyring', self.keyring.homedir + '/secring.gpg')

        if self.options.socks:
            # test if tor is running, as a safety precaution
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(self.options.socks)
                s.close()
            except socket.error as e:
                m = list(self.options.socks)
                if self.options.tor:
                    m += [str(e) + _(' - is Tor running?')]
                else:
                    m += [str(e)]
                self.abort(_('cannot open SOCKS proxy %s:%d: %s') % m)
            else:
                self.log(_('SOCKS proxy %s:%d appears operational') % self.options.socks)
            # this should be --use-tor, but:
            # 1. that is available only in undetermined versions of GPG 2.1.x
            # 2. it is not available in GPG 1.x legacy, which we still support
            # 3. it is actually a flag to dirmngr, not gpg, so it
            # requires writing to a new config file
            ks_opts = 'no-auto-key-retrieve,no-try-dns-srv,http-proxy=socks5-hostname://%s:%d' % self.options.socks
            self.tmpkeyring.context.set_option('keyserver-options', ks_opts)
        # copy the gpg.conf from the real keyring
        try:
            self.log(_('copying your gpg.conf in temporary keyring'))
            shutil.copy(self.keyring.homedir + '/gpg.conf', self.tmpkeyring.homedir)
        except IOError as e:
            # no such file or directory is alright: it means the use
            # has no gpg.conf (because we are certain the temp homedir
            # exists at this point)
            if e.errno != errno.ENOENT:
                raise

        # install the gpg agent socket for GnuPG 2.1 because
        # --secret-keyring silently fails
        # this is apparently how we should do things:
        # https://lists.gnupg.org/pipermail/gnupg-devel/2015-January/029301.html
        # cargo-culted from caff, thanks guilhem!
        src = self.keyring.get_agent_socket()
        dst = self.tmpkeyring.get_agent_socket()
        self.log(_('installing symlinks for sockets from %s to %s') % (src, dst))
        try:
            os.unlink(dst)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
        os.symlink(src, dst)

    def main(self):
        """
        General process
        ===============

        1. fetch the key into a temporary keyring
        1.a) if allowed (@todo), from the keyservers
        1.b) from the local keyring (@todo try that first?)
        2. copy the signing key secrets into the keyring
        3. for every user id (or all, if -a is specified)
        3.1. sign the uid, using gpg-agent
        3.2. export and encrypt the signature
        3.3. mail the key to the user
        3.4. optionnally (-l), create a local signature and import in
        local keyring
        4. trash the temporary keyring
        """
        pass # we don't do anything because we allow for interactive process

    def abort(self, message):
        """show a message to the user and abort program"""
        sys.exit(message)

    def warn(self, message):
        """display an warning message

this should not interrupt the flow of the program, but must be visible to the user"""
        print message.encode('utf-8')

    def log(self, message):
        """log an informational message if verbose"""
        if self.options.verbose or self.options.debug: print >>self.logfile, message

    def yes_no(self, prompt, default = True):
        """default UI is not interactive, so we assume yes all the time"""
        return True

    def acknowledge(self, prompt):
        return True

    def choose_uid(self, prompt, uids):
        raise NotImplementedError('choosing not implemented in base class')

    def prompt_line(self, prompt):
        raise NotImplementedError('prompting for a line not implemented in base class')

    def prompt_pass(self, prompt):
        raise NotImplementedError('prompting for a password not implemented in base class')

    def find_key(self):
        """find the key to be signed somewhere"""
        # 1.b) from the local keyring
        self.log(_('looking for key %s in your keyring') % self.pattern)
        if not self.tmpkeyring.import_data(self.keyring.export_data(self.pattern)):
            self.log(_('key not in local keyring'))

            # 1.a) if allowed, from the keyservers
            self.log(_('fetching key %s from keyserver') % self.pattern)

            if not re.search('^[0-9A-F]*$', self.pattern, re.IGNORECASE): # this is not a keyid
                # the problem here is that we need to implement --search-keys, and it's a pain
                raise NotImplementedError(_('please provide a keyid or fingerprint, uids are not supported yet'))

            if not self.tmpkeyring.fetch_keys(self.pattern):
                self.abort(_('could not find key %s in your keyring or keyservers') % self.pattern)

    def copy_secrets(self):
        """import secret keys (but only the public part) from your keyring

we use --secret-keyring instead of copying the secret key material,
but we still need the public part in the temporary keyring for this to
work.

we copy all keys because we do not want to guess which keys gpg will
chose. it could vary based on default-key, for example, or some weird
ordering.
        """
        self.log(_('copying your public key to temporary keyring in %s') % self.tmpkeyring.homedir)
        # detect the proper uid
        keys = self.keyring.get_keys(self.options.user, True, False)

        for fpr, key in keys.iteritems():
            self.log(_('found secret key: %s') % key)
            if not key.invalid and not key.disabled and not key.expired and not key.revoked:
                self.signing_key = key
                # export public key material associated with all private keys
                # XXX: we should only do export-minimal here, but passing options down is a pain.
                if not self.tmpkeyring.import_data(self.keyring.export_data(key.fpr)):
                    self.warning(_('could not export public key material of private key %s') % key.fpr)

        if self.signing_key is None:
            self.abort(_('could not find public key material for any private key, do you have an OpenPGP key?'))

    def sign_key(self):
        """sign the key uids, as specified"""

        keys = self.tmpkeyring.get_keys(self.pattern)

        # this shouldn't happen unless caller forgot to call copy_secrets
        assert(keys is not None)  # nosec
        self.log(_('found %d keys matching your request') % len(keys))

        secret_keys = self.keyring.get_keys(self.options.user, True, False)

        for key in keys:
            # Make sure the user isn't signing their own key
            for secret_key in secret_keys.values():
                if keys[key] == secret_key:
                    self.warn(_('That is your own key, so it is already certified'))
                    return False

            alluids = self.yes_no(_("""\
Signing the following key

%s

Sign all identities? [y/N] \
""") % keys[key], False)

            self.chosen_uid = None
            if alluids:
                pattern = keys[key].fpr
            else:
                pattern = self.choose_uid(_('Choose the identity to sign'), keys[key])
                if not pattern:
                    self.log(_('no identity chosen'))
                    return False
                if not self.options.to:
                    self.options.to = pattern
                self.chosen_uid = pattern

            if not self.options.dryrun:
                if not self.yes_no(_('Really sign key? [y/N] '), False):
                    continue
                if not self.tmpkeyring.sign_key(pattern, alluids):
                    self.warn(_('key signing failed'))
                else:
                    self.signed_keys[key] = keys[key]
                if self.options.local:
                    self.log(_('making a non-exportable signature'))
                    self.tmpkeyring.context.set_option('export-options', 'export-minimal')

                    # this is inefficient - we could save a copy if we would fetch the key directly
                    if not self.keyring.import_data(self.tmpkeyring.export_data(self.pattern)):
                        self.abort(_('could not import public key back into public keyring, something is wrong'))
                    if not self.keyring.sign_key(pattern, alluids, True):
                        self.warn(_('local key signing failed'))

    def export_key(self):
        if self.options.user is not None and '@' in self.options.user:
            from_user = self.options.user
        else:
            from_user = self.signing_key.uidslist[0].uid

        if len(self.signed_keys) < 1:
            self.warn(_('no key signed, nothing to export'))
        ret = True
        for fpr, key in self.signed_keys.items():
            if self.chosen_uid is None:
                for uid in key.uids.values():
                    try:
                        msg = EmailFactory(self.tmpkeyring.export_data(fpr), fpr, uid.uid, from_user, self.options.to)
                    except GpgRuntimeError as e:
                        self.warn(_('failed to create email: %s') % e)
                        break
                    ret = ret and self.sendmail(msg)
            else:
                try:
                    msg = EmailFactory(self.tmpkeyring.export_data(fpr), fpr, self.chosen_uid, from_user, self.options.to)
                except GpgRuntimeError as e:
                    self.warn(_('failed to create email: %s') % e)
                    break
                ret = self.sendmail(msg)
        return ret

    def sendmail(self, msg):
            """actually send the email

expects an EmailFactory email, but will not mail if nomail is set"""
            if self.options.smtpserver is not None and not self.options.nomail:
                if self.options.dryrun: return True
                # no test, because we'd need to ship a socks server
                # we assume pysocks is correctly tested, basically:
                # https://github.com/Anorov/PySocks
                if self.options.socks:
                    socks.setdefaultproxy(socks.SOCKS5, *self.options.socks)
                    socks.wrapmodule(smtplib)
                if self.options.tls:
                    server = smtplib.SMTP_SSL()
                else:
                    server = smtplib.SMTP()
                server.set_debuglevel(self.options.debug)
                # to be nicer to users, we could catch socket.error exceptions from
                # server.connect() here and display a meaningful message to stderr.
                try:
                    (code, srvmsg) = server.connect(self.options.smtpserver)
                except (socket.error, socket.timeout, socks.SOCKS5Error) as e:
                    self.abort(_('Error connecting to SMTP server %s: %s') % (self.options.smtpserver, e))
                if code != 220:
                    self.abort(_('Unexpected SMTP server error while talking to %s, code: %s (%s)') % (self.options.smtpserver, code, srvmsg))
                if not self.options.tls:
                    try:
                        server.starttls()
                    except smtplib.SMTPException:
                        self.warn(_('SMTP server does not support STARTTLS'))
                        if self.options.smtpuser:
                            self.abort(_('aborting authentication as credentials would have been sent in clear text'))
                if self.options.smtpuser:
                    if not self.options.smtppass:
                        self.options.smtppass = self.prompt_pass(_('enter SMTP password for server %s: ') % self.options.smtpserver)
                    server.login(self.options.smtpuser, self.options.smtppass)
                try:
                    server.sendmail(msg.mailfrom.encode('utf-8'), msg.mailto.encode('utf-8'), msg.as_string().encode('utf-8'))
                except smtplib.SMTPException as e:
                    self.warn(_('failed to send email: %s') % e)
                else:
                    self.warn(_('sent message through SMTP server %s to %s') % (self.options.smtpserver, msg.mailto))
                server.quit()
                return True
            elif not self.options.nomail:
                if self.options.dryrun: return True
                if self.options.mua:
                    keyfile = tempfile.NamedTemporaryFile()
                    # XXX: this should be part of the EmailFactory
                    keymaterial = msg.tmpkeyring.export_data(msg.keyfpr)
                    encrypted = msg.tmpkeyring.encrypt_data(keymaterial,
                                                            msg.keyfpr)
                    keyfile.write(encrypted)
                    keyfile.flush()
                try:
                    if self.options.mua:
                        command = [x % {'to': msg.mailto,
                                        'body': msg.body,
                                        'subject': msg.subject,
                                        'attach': keyfile.name}
                                   for x in shlex.split(self.options.mua)]
                    else:
                        command = [x % {'to': msg.mailto}
                                   for x in shlex.split(self.options.mta)]
                except ValueError as e:
                    if 'incomplete format' in str(e):
                        self.warn(_('invalid command (%s) specified to send email: %s')
                                  % (self.options.mua or self.options.mta, str(e)))
                        return False
                    else:
                        raise
                self.log('running command %s' % command)
                try:
                    p = subprocess.Popen(command,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)  # nosec
                except OSError as e:
                    self.warn(_('cannot find MTA %s, try specifying --mua, --mta or --smtp: %s')
                              % (self.options.mua, repr(e)))
                    return False

                if self.options.mua:
                    tosend = None
                else:
                    tosend = msg.as_string().encode('utf-8')
                self.mailer_output, self.mailer_error = p.communicate(tosend)
                if self.options.mua:
                    self.acknowledge('when you have finished writing the email')
                    keyfile.close()  # remove the tmpfile
                if p.returncode == 0:
                    self.warn(_('sent message to %(destination)s with %(command)s')
                              % {'destination': msg.mailto,
                                 'command': self.options.mua or self.options.mta})
                else:
                    self.warn(_('failed sending message to %(destination)s with %(command)s: %(error)s')
                              % {'destination': msg.mailto,
                                 'command': self.options.mua or self.options.mta,
                                 'error': self.mailer_output + self.mailer_error})
                return p.returncode == 0
            else:
                # okay, no mail, just dump the exported key then
                self.warn(_("""\
not sending email to %s, as requested, here's the encrypted signed public key you can paste in your email client:

%s""") % (msg.mailto, msg.encrypted()))


class EmailFactory:
    """email generator

this is a factory, ie. a class generating an object that represents
the email and when turned into a string, is the actual
mail.
"""

    # the email subject
    subject = _("Your signed OpenPGP key")

    # the email body
    body = _("""
Please find attached your signed OpenPGP key. You can import the
signed key by running each through `gpg --import`.

If you have multiple user ids, each signature was sent in a separate
email to each user id.

Note that your key was not uploaded to any keyservers. If you want
this new signature to be available to others, please upload it
yourself.  With GnuPG this can be done using:

    gpg --keyserver pool.sks-keyservers.net --send-key <keyid>

Regards,
""")

    def __init__(self, keydata, keyfpr, recipient, mailfrom, mailto):
        """email constructor

we expect to find the following arguments:

keydata: the signed public key material
keyfpr: the fingerprint of that public key
recipient: the recipient to encrypt the mail to
mailfrom: who the mail originates from
mailto: who to send the mail to (usually similar to recipient, but can be used to specify specific keyids"""
        (self.keyfpr, self.recipient, self.mailfrom, self.mailto) = (keyfpr, recipient, mailfrom.decode('utf-8'), mailto or recipient)
        self.mailto = self.mailto.decode('utf-8')
        # operate over our own keyring, this allows us to remove UIDs freely
        self.tmpkeyring = TempKeyring()
        # copy data over from the UI keyring
        self.tmpkeyring.import_data(keydata)
        # prepare for email transport
        self.tmpkeyring.context.set_option('armor')
        # this is necessary because we reimport keys from outside our
        # keyring, so gpg doesn't trust them anymore
        # but we know we do, so we ignore the trustdb
        self.tmpkeyring.context.set_option('trust-model', 'always')
        # remove UIDs we don't want to send
        self.cleanup_uids()
        # cleanup email addresses
        self.cleanup_emails()

    def cleanup_emails(self):
        # wrap real name in quotes
        self.mailfrom = re.sub(r'^(.*) <', r'"\1" <',
                               # trim comment from uid
                               re.sub(r' \([^)]*\)', r'',
                                      self.mailfrom))
        # same with mailto
        self.mailto = re.sub(r'^(.*) <', r'"\1" <',
                             re.sub(r' \([^)]*\)', r'',
                                    self.mailto))

    def cleanup_uids(self):
        """this will remove any UID not matching the 'recipient' set in the class"""
        for fpr, key in self.tmpkeyring.get_keys().iteritems():
            todelete = []
            for uid in key.uids.values():
                if self.recipient != uid.uid:
                    todelete.append(uid.uid)
            for uid in todelete:
                self.tmpkeyring.del_uid(fpr, uid)

    def encrypted(self):
        '''encrypted blob of the MIME multipart message

        this is designed to be attached as the main body of an email,
        but can also be copy-pasted anywhere, although the decrypted
        version will look a little ackward because it will include all
        sorts of MIME stuff

        but if proper headers are added to the message, it should be
        parsed okay by OpenPGP and MIME-capable clients.'''

        msg = self.create_mail_from_block().as_string()
        return self.tmpkeyring.encrypt_data(msg, self.keyfpr)

    def get_message(self):
        # first layer, seen from within:
        # an encrypted MIME message, made of two parts: the
        # introduction and the signed key material
        encrypted = self.encrypted()

        # the second layer up, made of two parts: a version number
        # and the first layer, encrypted
        return self.wrap_crypted_mail(encrypted)

    def __str__(self):
        return self.get_message().as_string().decode('utf-8')

    def as_string(self):
        return self.__str__()

    def create_mail_from_block(self):
        """
        a multipart/mixed message containing a plain-text message
        explaining what this is, and a second part containing PGP data
        """

        # Override python's weird assumption that utf-8 text should be encoded with
        # base64, and instead use quoted-printable (for both subject and body).  I
        # can't figure out a way to specify QP (quoted-printable) instead of base64 in
        # a way that doesn't modify global state. :-(
        # (taken from http://radix.twistedmatrix.com/2010/07/how-to-send-good-unicode-email-with.html)
        Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

        text = MIMEText(self.body, 'plain', 'utf-8')
        filename = 'signed-%s.asc' % self.keyfpr # should be 0xkeyid.uididx.signed-by-0xkeyid.asc
        keypart = MIMEBase('application', 'pgp-keys', name=filename)
        keypart.add_header('Content-Disposition', 'attachment', filename=filename)
        keypart.add_header('Content-Transfer-Encoding', '7bit')
        keypart.add_header('Content-Description', (_('signed OpenPGP Key %s, uid %s') % (self.keyfpr, self.recipient.decode('utf-8'))))
        keypart.set_payload(self.tmpkeyring.export_data(self.keyfpr))
        return MIMEMultipart('mixed', None, [text, keypart])

    def wrap_crypted_mail(self, encrypted):
        p1 = MIMEBase('application', 'pgp-encrypted', filename='signedkey.msg')
        p1.add_header('Content-Disposition','attachment', filename='signedkey.msg')
        p1.set_payload('Version: 1')
        p2 = MIMEBase('application', 'octet-stream', filename='msg.asc')
        p2.add_header('Content-Disposition', 'inline', filename='msg.asc')
        p2.add_header('Content-Transfer-Encoding', '7bit')
        p2.set_payload(encrypted)
        msg = MIMEMultipart('encrypted', None, [p1, p2], protocol="application/pgp-encrypted")
        msg.preamble = _('This is a multi-part message in OpenPGP/MIME format...')
        try:
            msg['Subject'] = Header(self.subject.encode('ascii'))
        except UnicodeEncodeError:
            msg['Subject'] = Header(self.subject, 'UTF-8')
        name, address = parseaddr(self.mailfrom)
        msg['From'] = formataddr((Header(name.encode('utf-8'), 'UTF-8').encode(), address))
        name, address = parseaddr(self.mailto)
        msg['To'] = formataddr((Header(name.encode('utf-8'), 'UTF-8').encode(), address))
        return msg

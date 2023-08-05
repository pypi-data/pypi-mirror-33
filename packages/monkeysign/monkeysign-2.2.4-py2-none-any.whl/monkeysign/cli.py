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

import errno
import locale
import sys
import os
import getpass

from monkeysign.ui import MonkeysignUi
import monkeysign.translation

class MonkeysignCli(MonkeysignUi):
    """sign a key in a safe fashion.

This command signs a key based on the fingerprint or user id
specified on the commandline, encrypt the result and mail it to the
user. This leave the choice of publishing the certification to that
person and makes sure that person owns the identity signed.

This program assumes you have gpg-agent configured to prompt for
passwords."""

    def main(self):
        """main code execution loop

        we expect to have the commandline parsed for us
        """

        MonkeysignUi.main(self)

        if not 'GPG_TTY' in os.environ:
            try:
                os.environ['GPG_TTY'] = os.ttyname(sys.stdin.fileno())
            except OSError as e:
                if e.errno == errno.ENOTTY:
                    self.warn(_('cannot find your TTY, GPG may freak out if you do not set the GPG_TTY environment'))
                else:
                    raise
            else:
                self.log(_('reset GPG_TTY to %s') % os.environ['GPG_TTY'])

        # 1. fetch the key into a temporary keyring
        self.find_key()

        # 2. copy the signing key secrets into the keyring
        self.copy_secrets()

        self.warn(_('Preparing to sign with this key\n\n%s') % self.signing_key)

        # 3. for every user id (or all, if -a is specified)
        # 3.1. sign the uid, using gpg-agent
        self.sign_key()

        # 3.2. export and encrypt the signature
        # 3.3. mail the key to the user
        # 3.4. optionnally (-l), create a local signature and import in
        #local keyring
        self.export_key()

        # 4. trash the temporary keyring
        # implicit

    def yes_no(self, prompt, default = None):
        ans = raw_input(prompt.encode(sys.stdout.encoding or locale.getpreferredencoding(True)))
        while default is None and ans.lower() not in ["y", "n"]:
            ans = raw_input(prompt.encode(sys.stdout.encoding or locale.getpreferredencoding(True)))
        if default: return default
        else: return ans.lower() == 'y'

    def acknowledge(self, prompt):
        prompt = _('press enter when %s') % prompt
        raw_input(prompt.encode(sys.stdout.encoding or locale.getpreferredencoding(True)))

    def prompt_line(self, prompt):
        return raw_input(prompt.encode(sys.stdout.encoding or locale.getpreferredencoding(True)))

    def prompt_pass(self, prompt):
        return getpass.getpass(prompt)

    def choose_uid(self, prompt, key):
        """present the user with a list of UIDs and let him choose one"""
        try:
            allowed_uids = []
            for uid in key.uidslist:
                allowed_uids.append(uid.uid)

            prompt += _(' (1-%d or full UID, control-c to abort): ') % len(allowed_uids)

            # workaround http://bugs.python.org/issue7768
            pattern = raw_input(prompt.encode(sys.stdout.encoding or locale.getpreferredencoding(True)))
            while not (pattern in allowed_uids or (pattern.isdigit() and int(pattern)-1 in range(0,len(allowed_uids)))):
                print _('invalid uid')
                pattern = raw_input(prompt.encode(sys.stdout.encoding or locale.getpreferredencoding(True)))
            if pattern.isdigit():
                pattern = allowed_uids[int(pattern)-1]
            return pattern
        except KeyboardInterrupt:
            return False

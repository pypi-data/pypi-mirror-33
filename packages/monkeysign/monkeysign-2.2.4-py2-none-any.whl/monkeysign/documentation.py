# -*- coding: utf-8 -*-

"""build_manpage command -- Generate man page from setup()"""

import os
import datetime
import time
from distutils.command.build import build
from distutils.core import Command
from distutils.errors import DistutilsOptionError
import subprocess  # nosec


class build_slides(Command):

    description = 'Generate the HTML presentation with rst2s5.'

    user_options = [
        ('file=', 'f', 'rst file'),
        ]

    def initialize_options(self):
        self.file = None

    def finalize_options(self):
        if self.file is None:
            raise DistutilsOptionError('\'file\' option is required')

    def run(self):
        html = os.path.join(os.path.dirname(self.file), os.path.splitext(os.path.basename(self.file))[0] + '.html')
        self.announce('processing slides from %s to %s' % (self.file, html), 2)
        subprocess.call(['rst2s5', '--theme', 'default', self.file, html])  # nosec

def has_rst2s5(build):
    """predicate for this class: do not fail if rst2s5 is missing"""
    return (os.system('rst2s5 < /dev/null > /dev/null') == 0)  # nosec

# (function, predicate), see http://docs.python.org/2/distutils/apiref.html#distutils.cmd.Command.sub_commands
build.sub_commands.append(('build_slides', has_rst2s5))
build.sub_commands.append(('build_sphinx', None))

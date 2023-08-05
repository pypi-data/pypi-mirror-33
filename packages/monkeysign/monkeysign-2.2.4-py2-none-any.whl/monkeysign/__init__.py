# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

__description__ = 'OpenPGP key exchange for humans'
__long_description__ = """
monkeysign is a tool to overhaul the OpenPGP keysigning experience and
bring it closer to something that most primates can understand.

The project makes use of cheap digital cameras and the type of bar
code known as a QRcode to provide a human-friendly yet still-secure
keysigning experience.

No more reciting tedious strings of hexadecimal characters.  And, you
can build a little rogue's gallery of the people that you have met and
exchanged keys with!
"""
try:
    from _version import version
except ImportError:
    try:
        from setuptools_scm import get_version
        version = get_version()
    except (ImportError, LookupError):
        version = '???'
__version__ = version
__copyright__ = """Copyright (C) 2010-2013  Antoine Beaupré, Jerome Charaoui
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
For details see the COPYRIGHT file distributed along this program."""

__license__ = """
    This package is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    any later version.

    This package is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this package; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
"""

__website__ = 'http://web.monkeysphere.info/monkeysign'
__documentation__ = 'http://monkeysign.readthedocs.io/en/' + __version__
# hack to include the credits in the documentation
# maybe this should be parsed from a AUTHORS file instead, see
# https://0xacab.org/monkeysphere/monkeysign/issues/56
# if you feel comptent to respond to Code of Conduct reports,
# make sure you add your email address below
# credits-start
__authors__ = ['In alphabetical order:',
               '',
               'Antoine Beaupré',
               'Daniel Kahn Gillmor',
               'Gabriel Fillion',
               'Jérôme Charaoui',
               'Kristian Fiskerstrand',
               'Philip Jägenstedt',
               'Ramakrishnan Muthukrishnan',
               'Simon Fondrie-Teitler',
               'Tobias Mueller',
               ]
__documenters__ = ['In alphabetical order:',
                   '',
                   'Antoine Beaupré',
                   'Emma Peel',
                   ]
__translators__ = ['In alphabetical order:',
                   '',
                   'Antoine Beaupré',
                   'Ahmed El Azzabi',
                   'Gonzalo Exequiel Pedone',
                   'Michael R. Lawrence',
                   'Michal Čihař',
                   ]

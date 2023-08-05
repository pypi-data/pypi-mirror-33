#!/usr/bin/python

"""This deliberately incomplete MUA will emulate behaviors of the
worst MUA available we can think of. It will behave like xdg-email
with extra bugs. For example:

1. parameters are only passed on the commandline
2. complete MIME messages will not work
3. it will return before processing the message
4. it will sleep for 5 seconds before actually "sending" the message

The message is appended to a temporary file in a mbox-like format
(ie. messages are just concatenated). The path to the file is printed
to stdout.

Return code should be 0 if all goes well or non-zero for any other
failure. Errors are logged to stderr.
"""

from __future__ import division, absolute_import
from __future__ import print_function, unicode_literals

import argparse
from email import Charset
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
# Python 2 backwards-compatible open
from io import open
import logging
import os
import tempfile
import time
import sys

logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    parser = argparse.ArgumentParser(description='Fake Mail User Agent',
                                     epilog=__doc__)
    parser.add_argument('--to', required=True,
                        help='email address to send the message to')
    parser.add_argument('--body', help='body of the message')
    parser.add_argument('--subject', help='body of the message')
    parser.add_argument('--attach', help='file to attach to the message')
    parser.add_argument('--sleep', default=5, type=int,
                        help='how long to sleep for (default: %(default)s)')
    parser.add_argument('--output', default=None,
                        help='where to write the messages (default: tmpfil)')
    return parser.parse_args()


def make_message(args):
    """create mime message with the given arguments"""

    # Override python's weird assumption that utf-8 text should be
    # encoded with base64, and instead use quoted-printable (for both
    # subject and body).  I can't figure out a way to specify QP
    # (quoted-printable) instead of base64 in a way that doesn't
    # modify global state. :-( see
    # http://radix.twistedmatrix.com/2010/07/how-to-send-good-unicode-email-with.html
    Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

    msg = body = MIMEText(args.body, 'plain', 'utf-8')
    if args.attach:
        files = MIMEBase('text', 'plain', filename=args.attach)
        files.add_header('Content-Disposition', 'inline', filename='msg.asc')
        files.add_header('Content-Transfer-Encoding', '7bit')
        with open(args.attach, encoding='utf-8') as attach:
            files.set_payload(attach.read())

        msg = MIMEMultipart('mixed', None, (body, files))
    try:
        msg['Subject'] = Header(args.subject.encode('ascii'))
    except UnicodeDecodeError:
        msg['Subject'] = Header(args.subject, 'UTF-8')
    msg['From'] = 'unittests@localhost'
    msg['To'] = args.to
    return msg


def main():
    args = parse_args()
    if args.output is None:
        fd, tmpfile = tempfile.mkstemp()
        fd = open(fd, mode='a', encoding='utf-8')
        logging.debug('created tmpfile %s', tmpfile)
    elif args.output == '-':
        fd = sys.stdout
        tmpfile = '/dev/stdout'
    else:
        tmpfile = args.output
        fd = open(tmpfile, mode='w', encoding='utf-8')

    logging.debug('backgrounding')
    if os.fork():  # parent
        print(tmpfile)
        sys.exit(0)
    logging.debug('sleeping %d seconds', args.sleep)
    time.sleep(args.sleep)
    logging.debug('generating MIME message')
    msg = make_message(args)
    logging.debug('writing to file')
    fd.write(msg.as_string().decode('utf-8'))
    fd.close()

if __name__ == '__main__':
    main()

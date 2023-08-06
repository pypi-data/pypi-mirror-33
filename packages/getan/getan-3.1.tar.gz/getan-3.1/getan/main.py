#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# (c) 2010 by Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2011 by Björn Ricks <bjoern.ricks@intevation.de>
# (c) 2017, 2018 Intevation GmbH
#   Authors:
#    * Magnus Schieder <magnus.schieder@intevation.de>
#
# A python worklog-alike to log what you have 'getan' (done).
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging
import os
import os.path
import argparse
import textwrap

import getan
import getan.config as config

from getan.backend import DEFAULT_DATABASE, Backend
from getan.controller import GetanController

logger = logging.getLogger()


def main():

    usage = "%(prog)s [options] [databasefile (default: " + \
        DEFAULT_DATABASE + ")]"
    version = '''
    getan version %s
    (c) 2008-2018 by Intevation
        Author: Björn Ricks <bjoern.ricks@intevation.de>
                Bernhard Reiter <bernhard.reiter@intevation.de>
                Sascha L. Teichmann <teichmann@intevation.de>
                Thomas Arendsen Hein <thomas@intevation.de>
                Ingo Weinzierl <ingo.weinzierl@intevation.de>
                Magnus Schieder <magnus.schieder@intevation.de>

    This is Free Software licensed under the terms of GPLv3 or later.
    For details see LICENSE coming with the source of \'getan\'.
    ''' % getan.__version__

    parser = argparse.ArgumentParser(prog='getan', usage=usage,
             formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version',
                        version=textwrap.dedent(version))
    parser.add_argument(dest='filename', nargs='?',
                        help='[databasefile (default: %(default)s)]',
                        default=DEFAULT_DATABASE)
    parser.add_argument('--init-only', action='store_true', dest='initonly',
                        help='create databasefile if necessary and exit')
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel',
                        default=logging.NOTSET, const=logging.DEBUG,
                        help='Enable debung mode')
    parser.add_argument('-l', '--logfile', dest='logfile', metavar='FILE',
                        help='''write log information to FILE [default:
                        %(default)s]''', default='getan.log')

    args = parser.parse_args()

    config.initialize(args.loglevel, args.logfile)
    global logger

    if args.filename != DEFAULT_DATABASE:
        database = args.filename
    else:
        if os.path.isfile(DEFAULT_DATABASE):
            database = os.path.abspath(DEFAULT_DATABASE)
        else:
            getan_dir = os.path.expanduser(os.path.join("~", ".getan"))
            if not os.path.exists(getan_dir):
                os.mkdir(getan_dir)
            database = os.path.join(getan_dir, DEFAULT_DATABASE)

    backend = Backend(database)
    logging.info("Using database '%s'." % database)

    if args.initonly:
        return

    controller = GetanController(backend)

    try:
        controller.main()
    except KeyboardInterrupt:
        pass
    finally:
        controller.shutdown()


if __name__ == '__main__':
    main()

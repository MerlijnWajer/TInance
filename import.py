#!/usr/bin/env python2
# encoding: utf-8
"""
This file is part of the TechInc Financial Administration
Copyright (c) 2014 by Merlijn Wajer

TInance is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TInance is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TInance.  If not, see <http://www.gnu.org/licenses/>.

See the file COPYING, included in this distribution,
for details about the copyright.
"""


import os, sys, argparse, re
import datetime, time

import tidb
from tidb.sql import *

import json

NAME = 'Technologia Incognita'

def pretty_print(m, form, human):
    print m.format(form, human_read=human).encode('utf-8')

parser = argparse.ArgumentParser(description='%s Import tool' % NAME,
        epilog='')

parser.add_argument('-f', '--file', type=str, default='')
parser.add_argument('-i', '--really-import', action='store_true', default=False)
parser.add_argument('-C', '--no-check-hashes', action='store_true', default=False)
parser.add_argument('-R', '--reject-file', type=str, default='')


args = parser.parse_args()
if args.file == '':
    parser.print_help()
    sys.exit(1)

fd = open(args.file)

payments = json.loads(fd.read())

if args.reject_file:
    rfd = open(args.reject_file)
    rejects = map(lambda x: x.rstrip('\n'), rfd.readlines())

    fp = []

    for p in payments:
        if p['hash'] not in rejects:
            fp.append(p)
        else:
            print 'Rejecting:', p['hash']

    payments = list(fp)

if not args.no_check_hashes:
    fp = []

    for p in payments:
        q = Session.query(Payment).filter(Payment.payment_sha256 ==
                p['hash']).first()
        if q is not None:
            print p['hash'], 'already in database!'
        else:
            fp.append(p)

    payments = list(fp)

for p in payments:
    memb = Session.query(Member).filter(Member.nick.like(p['nick'])).first()

    if memb is None:
        print >>sys.stderr, p['nick'], 'not known!'
        raise Exception(p['nick'])

    d = datetime.date(*map(int, p['date'].split('-')))
    pay = Payment(member_id=memb.id, date=d, amount=p['amount'], comment=p['desc'],
            months=p['months'], payment_sha256=p['hash'])

    if args.really_import:
        Session.add(pay)

if args.really_import:
    Session.commit()
else:
    print('SIMULATE MODE: To actually import, use -i')

#!/usr/bin/env python2
# encoding: utf-8

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


args = parser.parse_args()
if args.file == '':
    parser.print_help()
    sys.exit(1)

fd = open(args.file)

payments = json.loads(fd.read())

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
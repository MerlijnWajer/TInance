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

import stats

NAME = 'Technologia Incognita'

def pretty_print(m, form, human):
    print m.format(form, human_read=human).encode('utf-8')

parser = argparse.ArgumentParser(description='%s administration tool' % NAME,
        epilog='') # TODO funny epilog


"""

Examples:

List all members that as overdue in paying, in csv:

        python ti.py -f '%j, %p, %N' -s -n % -r 'overdue'

"""

"""
Member:
* Add
* List
* [Future] Set non-active
* [Future] Manage payments?


* Add member
* List members
"""

parser.add_argument('-d', '--date', type=unicode,
        help='Either a valid format string or "now". Default format:'
        '%%Y-%%m-%%d. Used when adding a new member - as join date')
parser.add_argument('-r', '--restrict', default=None,
        help='Restrict viewing members based on their payment-status. '
              'Possible options: overdue,ontime,all')

filter_group = parser.add_argument_group('Filtering attributes')
filter_group.add_argument('-n', '--nick', type=unicode)
filter_group.add_argument('-N', '--name', type=unicode)
filter_group.add_argument('-e', '--email', type=unicode)
filter_group.add_argument('-k', '--fobid', type=unicode)

active_group = parser.add_argument_group('Activity filters and toggles')
active_group.add_argument('--all', action='store_true', default=False,
        help='Query active and inactive members')
active_group.add_argument('-A', '--active-only', action='store_true', default=True,
        help='Query only active members (default')
active_group.add_argument('-D', '--inactive-only', action='store_true', default=False,
        help='Query only inactive members')

active_group.add_argument('--activate', action='store_true', default=False,
        help='Activate a search match (zero or more members)')
active_group.add_argument('--deactivate', action='store_true', default=False,
        help='Deactivate a search match (zero or more members)')



output_group = parser.add_argument_group('Formatting options')

output_group.add_argument('--dateformat', type=unicode, default='%Y-%m-%d')

output_group.add_argument('-H', '--human', action='store_true', default=False)
output_group.add_argument('-f', '--format', type=str, default='%n %j %p',
    help="""Add percentage in front of the type. Allowed types:
id:        i
nick:      n
name:      N
mail:      m
join-date: j
paid:      p
keyid:     k
active:    A
""")

modes_group = parser.add_argument_group('Modes')
modes_group.add_argument('-a', '--add', action='store_true', default=False,
        help='Enter add mode')
modes_group.add_argument('-s', '--search', action='store_true', default=False,
        help='Enter search mode')
# TODO: Implement --modify
modes_group.add_argument('-m', '--modify', action='store_true', default=False)
modes_group.add_argument('-J', '--JSON', action='store_true', default=False)



payment_group = parser.add_argument_group('Payment options commands')
payment_group.add_argument('--payment', action='store_true', default=False,
        help='Enter payment mode; use with --search or --add.')
payment_group.add_argument('--payment-view', action='store_true', default=False,
        help='Enter payment view mode')
payment_group.add_argument('--payment-months', type=int,
        help='Amount of months: the amount of months the payment is for')
payment_group.add_argument('--payment-amount', type=float, default=None,
        help='Payment amount total: not per month, but of the entire payment')
payment_group.add_argument('--payment-comment', type=str,
        help='Payment comment: optional')
payment_group.add_argument('--payment-hash', type=str,
        help='Payment hash (optional for manual add)')
payment_group.add_argument('--payment-id', type=int,
        help='Payment id')

args = parser.parse_args()

if sum((args.search, args.add, args.deactivate, args.activate, args.modify)) > 1:
    print 'Searching, deleting and/or adding at the same time? Sense you no MAKE!'
    parser.print_help()
    sys.exit(1)

if args.JSON: # For LDAP
    import json
    q = Session.query(Member).filter(Member.active == True).all()

    members = []
    for x in q:
        members.append({"nickname":x.nick, "email":x.email})

    print json.dumps(members, indent=4)

activequery = None
if args.active_only and not args.all:
    activequery = True
if args.inactive_only and not args.all:
    activequery = False

if args.activate or args.deactivate:
    q = stats.members_query(args.nick, args.name, args.email, None,
            args.fobid)
    for m in q:
        m.active = args.activate and not args.deactivate
        if m.active:
            print m.nick, 'is now activated'
        else:
            print m.nick, 'is now deactivated'
        Session.add(m)

    Session.commit()

elif args.search:
    if args.payment:
        q = stats.members_query(args.nick, args.name, args.email, activequery,
                args.fobid)
        r = q.all()

        if args.payment_view:
            for m in r:
                print('%s\tJoined: %s' % (m.nick, m.member_date))
                pay = m.payments
                pay = sorted(m.payments, key=lambda x: x.date)

                for i, p in enumerate(pay):
                    p_u = m.paid_until(pay[:i+1])

                    print('for {}\t\ton {}\tA:{:6.2f}\tM:{:2d}\t\t {}'.format(p_u,
                        p.date, p.amount, p.months, p.comment[:40]))
        else:
            for m in r:
                for p in m.payments:
                    print m.nick, 'Date:', p.date, 'Amount:', p.amount, 'Months:', \
                        p.months, 'Comment:', p.comment[:40]

    else:
        q = stats.members_query(args.nick, args.name, args.email, activequery,
                args.fobid)
        r = q.all()

        for m in r:
            if args.restrict:
                try:
                    cmpfunc = {
                        'overdue': stats.member_overdue,
                        'ontime' : stats.member_ontime,
                        'all'    : None
                    }[args.restrict]
                except KeyError:
                    print 'Invalid restrict:', args.restrict
                    parser.print_help()
                    sys.exit(1)

                if cmpfunc(m):
                    pretty_print(m, args.format, args.human)

            else:
                pretty_print(m, args.format, args.human)

elif args.add:
    if args.payment:
        add_args = ['nick', 'payment_months', 'payment_amount', 'date', 'payment_comment']
        if not all(map(lambda x: getattr(args, x) is not None, add_args)):
            print 'Please provide: ' + ', '.join(add_args)
            parser.print_help()
            sys.exit(1)

        amount = args.payment_amount
        months = args.payment_months
        comment = args.payment_comment
        membern = args.nick
        member = Session.query(Member).filter(Member.nick == membern).first()

        if member is None:
            print 'Member not found, please check/mind casing as well:', membern
            exit(1)

        d = datetime.datetime.strptime(args.date, args.dateformat)

        p = Payment(member_id=member.id, date=d, amount=amount, months=months, comment=comment)

        Session.add(p)
        Session.commit()
        print('Added:', p)
    else:
        add_args = ['nick', 'name', 'email', 'date', 'fobid']
        if not all(map(lambda x: getattr(args, x), add_args)):
            print 'Please provide: ' + ', '.join(add_args)
            parser.print_help()
            sys.exit(1)

        d = args.date
        if d == 'now':
            d = datetime.date.today()
        else:
            d = datetime.datetime.strptime(args.date, args.dateformat)

        m = Member(nick=args.nick, name=args.name, email=args.email,
                member_date=d, fobid=args.fobid)
        Session.add(m)
        Session.commit()

elif args.modify:
    print 'Not implemented yet'
    if args.payment:
        pass
    else:
        pass
    # TODO
    pass
else:
    parser.print_help()
    sys.exit(1)

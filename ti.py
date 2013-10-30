#!/usr/bin/env python2
# encoding: utf-8

import os, sys, argparse, re
import datetime, time

from sql import *

NAME = 'Technologia Incognita'

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
* [Future] 


* Add member
* List members
"""

parser.add_argument('-n', '--nick', type=unicode)
parser.add_argument('-N', '--name', type=unicode)
parser.add_argument('-e', '--email', type=unicode)
parser.add_argument('-d', '--date', type=unicode,
    help='Either a valid format string or "now"')
parser.add_argument('--dateformat', type=unicode,
    default='%Y-%m-%d')

parser.add_argument('-s', '--search', action='store_true', default=False)
parser.add_argument('-f', '--format', type=str, default='%n %j %p',
    help="""Add percentage in front of the type. Allowed types:
id:        i
nick:      n
name:      N
mail:      m
join-date: j
paid:      p
""")
parser.add_argument('-r', '--restrict', default=None)

parser.add_argument('-a', '--add', action='store_true', default=False)


args = parser.parse_args()
if args.search and args.add:
    print 'Searching and adding at the same time? Sense you no MAKE!'
    # Trolo
    print 'make: *** No targets specified and no makefile found.  Stop.'
    print
    parser.print_help()
    sys.exit(1)

if args.search:
    f = lambda _, a: _.like(a)

    q = Session.query(Member)
    if args.nick:
        q = q.filter(f(Member.nick, args.nick))
    if args.name:
        q = q.filter(f(Member.name, args.name))
    if args.email:
        q = q.filter(f(Member.email, args.email))

    r = q.all()
    for m in r:
        if args.restrict:
            t = time.localtime()
            due = datetime.date(t.tm_year, t.tm_mon, 1)
            if args.restrict == 'overdue':
                cmpfunc = lambda d1, d2: d1 < d2 # overdue
            elif args.restrict == 'ontime':
                cmpfunc = lambda d1, d2: d1 >= d2 # on time
            else:
                cmpfunc = lambda d1, d2: True #all

            if cmpfunc(m.paid_until(), due):
                print m.format(args.format)


        else:
            print m.format(args.format)

elif args.add:
    add_args = ['nick', 'name', 'email', 'date']
    if not all(map(lambda x: getattr(args, x), add_args)):
        print 'Please provide: ' + ', '.join(add_args)
        parser.print_help()
        sys.exit(1)

    d = args.date
    if d == 'now':
        d = datetime.date.today()
    else:
        d = datetime.datetime.strptime(args.date, args.dateformat)

    m = Member(nick=args.nick, name=args.name, email=args.email, member_date=d)
    Session.add(m)
    Session.commit()

#!/usr/bin/env python2
# encoding: utf-8

import os, sys, argparse, re
import datetime, time

from sql import *

import stats

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
* [Future] Manage payments?


* Add member
* List members
"""

parser.add_argument('-n', '--nick', type=unicode)
parser.add_argument('-N', '--name', type=unicode)
parser.add_argument('-e', '--email', type=unicode)
parser.add_argument('-A', '--active-only', action='store_true', default=False)
parser.add_argument('-d', '--date', type=unicode,
    help='Either a valid format string or "now"')
parser.add_argument('--dateformat', type=unicode,
    default='%Y-%m-%d')

parser.add_argument('-H', '--human', action='store_true', default=False)
parser.add_argument('-s', '--search', action='store_true', default=False)
parser.add_argument('-f', '--format', type=str, default='%n %j %p',
    help="""Add percentage in front of the type. Allowed types:
id:        i
nick:      n
name:      N
mail:      m
join-date: j
paid:      p
keyid:     k
""")
parser.add_argument('-r', '--restrict', default=None,
        help='Possible options: overdue,ontime,all')
parser.add_argument('-a', '--add', action='store_true', default=False)
parser.add_argument('-J', '--JSON', action='store_true', default=False)


args = parser.parse_args()
if args.search and args.add:
    print 'Searching and adding at the same time? Sense you no MAKE!'
    print
    parser.print_help()
    sys.exit(1)

if args.JSON: # For LDAP
    import json
    q = Session.query(Member).filter(Member.active == True).all()

    members = []
    for x in q:
        members.append({"nickname":x.nick, "email":x.email})

    print json.dumps(members, indent=4)



if args.search:
    f = lambda _, a: _.like(a)

    q = stats.members_query(args.nick, args.name, args.email, args.active_only)
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
                print m.format(args.format, human_read=args.human).encode('utf-8')

        else:
            print m.format(args.format, human_read=args.human).encode('utf-8')

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

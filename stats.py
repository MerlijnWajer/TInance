#!/usr/bin/env python2

from sql import *

import datetime
import time

"""
Give member count, inactive and active seperate
Provide percentage of members paying more than X
Provide percentage of members who paid on time, and who have not
"""

start = datetime.date(2011, 11, 1)


def member_count():
    """
    """
    q = Session.query(Member).filter(Member.active==True)
    inactive = Session.query(Member).filter(Member.active==False)
    return len(q.all()), len(inactive.all())

def members_paying_more_than_x():
    """
    """

def members_query(nick=None, name=None, email=None, active=None):
    f = lambda _, a: _.like(a)
    q = Session.query(Member)

    if nick:
        q = q.filter(f(Member.nick, nick))
    if name:
        q = q.filter(f(Member.name, name))
    if email:
        q = q.filter(f(Member.email, email))
    if active:
        q = q.filter(Member.active, active)

    return q

def members_query_g(**kwargs):
    f = lambda _, a: _.like(a)
    q = Session.query(Member)

    for k, d in kwargs.iteritems():
        if d:
            q = q.filter(f(getattr(Member, k), k))

    return q

def member_paid(m, f, grace=None):
    t = time.localtime()
    due = datetime.date(t.tm_year, t.tm_mon, 1)

    if f(m.paid_until(), due):
        return m
    return None

def member_overdue(m):
    """
    """
    f = lambda d1, d2: d1 < d2 # overdue
    return member_paid(m, f)

def member_ontime(m):
    """
    """
    f = lambda d1, d2: d1 >= d2 # on time
    return member_paid(m, f)

def members_paid(f):
    q = members_query()
    for m in q:
        if not f:
            yield m
        elif f(m):
            yield m

def members_overdue():
    return members_paid(member_overdue)

def members_ontime():
    return members_paid(member_ontime)

if __name__ == '__main__':
    print member_count()
    print list(members_overdue())
    print list(members_ontime())

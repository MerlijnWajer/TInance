#!/usr/bin/env python2
import pylab

from sql import *

"""
DONE:
    * Breakdown of sum of money per month
    * Breakdown of new members per month
    * List of members that (have|have not) paid on time.
TODO:
    * Make function: members_at_month (with specific month)
    * Make function: money_at_month (with specific month)
"""

import datetime
import time

start = datetime.date(2011, 11, 1)

def average_payment():
    s = Session.query(Payment).all()
    ss = sum([0 if _.months == 0 else _.amount / _.months for _ in s])
    l = sum([_.months for _ in s])
    return ss / l

def mocalc(d):
    """ Convert years * 12 + months back to datetime """
    years = d / 12
    d -= years * 12
    years += start.year
    months = d + 1 # So januari is 1, not 0

    return '%s-%s' % (years, months)
    #return datetime.date(years, months, 1)


def members_per_month():
    """ Members added per month; not cummulative """
    s = Session.query(Member).all()
    so = sorted(s, key=lambda x: x.member_date)

    d = [x.member_date for x in so]

    d = [(_.year - start.year) * 12 + _.month for _ in d]

    t = set(d)

    numbers = range(max(t))
    labels = map(mocalc, numbers)

    pylab.xticks(numbers, labels, rotation='vertical')

    n, bins, patches = pylab.hist(d, bins=max(t))
    pylab.show()

    pylab.clf()

    pylab.xticks(numbers, labels, rotation='vertical')
    pylab.plot(numbers, n)
    pylab.show()

    pylab.clf()

    cumn = []
    for i in xrange(len(n)):
        cumn.append(sum(n[:i]))

    pylab.xticks(numbers, labels, rotation='vertical')
    pylab.plot(numbers, cumn)
    pylab.show()
    pylab.clf()

def money_per_month():
    def add_month_to_date(date, months):
        y = (date.month + months) / 12
        m = ((date.month + months) % 12) + 1

        return (date.year + y, m)


    s = Session.query(Payment).all()
    so = sorted(s, key=lambda x: x.date)

    d = {}
    for p in so:
        if (p.date.year, p.date.month) in d:
            d[(p.date.year, p.date.month)].append(p)
        else:
            d[(p.date.year, p.date.month)] = [p]

    dc = {}
    # Dirty hack for start
    for x in xrange(2011, 2012):
        for y in xrange(10, 13):
            dc[(x, y)] = 0

    for k, pays in d.iteritems():
        y, m = k
        for v in pays:

            for m in xrange(v.months):
                yy, mm = add_month_to_date(v.date, m)

                if (yy, mm) not in dc:
                    dc[(yy, mm)] = 0

                dc[(yy, mm)] += v.amount / v.months


    l = []
    for k, v in dc.iteritems():
        l.append((k, int(v)))

    ll = sorted(l, key=lambda x: datetime.date(x[0][0], x[0][1], 1))

    x, y = [], []
    for v in ll:
        x.append((v[0][0] - start.year) * 12 + v[0][1])
        y.append(v[1])

    numbers = range(max(x))
    labels = map(mocalc, numbers)

    pylab.xticks(numbers, labels, rotation='vertical')

    pylab.plot(x, y)
    #pylab.bar(x, y)
    pylab.xlabel('Month')
    pylab.ylabel('Income (Euro)')
    pylab.show()


money_per_month()
members_per_month()

#cmpfunc = lambda d1, d2: d1 >= d2 # on time
#cmpfunc = lambda d1, d2: d1 < d2 # overdue
cmpfunc = lambda d1, d2: True #all

t = time.localtime()
due = datetime.date(t.tm_year, t.tm_mon, 1)

s = Session.query(Member).all()
for m in s:
    if cmpfunc(m.paid_until(), due) and m.active:
        print repr(m).decode('utf-8'), len(m.payments), m.email, m.nick

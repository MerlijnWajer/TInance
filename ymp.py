from __future__ import print_function

from datetime import datetime, date
import time
import stats

import argparse

start = date(2011, 11, 1)
dateformat = '%Y-%m-%d'

parser = argparse.ArgumentParser()

parser.add_argument('--cutoff', type=unicode, default=None,
                    help='Cut off (ignore) payments after a certain date.\n'
                         'Format is YYYY-MM-DD. Day is ignored.\n'
                         'By default cutoff is equal to current')
parser.add_argument('--current', type=unicode, default=None,
                    help='Define for what month we want to know the YMP.\n'
                          'Format is YYYY-MM-DD. Day is ignored.')
parser.add_argument('-v', '--verbose', action='store_true', default=False)

args = parser.parse_args()

limit, current = None, None

if args.current is None:
    fuckoff = datetime.now()
    current = date(fuckoff.year, fuckoff.month, 7)
else:
    fuckoff = datetime.strptime(args.current, dateformat)
    current = date(fuckoff.year, fuckoff.month, 7)

if args.cutoff is None:
    # TODO: By default it makes sense to not count any payments made after
    # the date we want to know the YMP for.
    limit = current
    #limit = date(3000, 1, 1)
else:
    fuckoff = datetime.strptime(args.cutoff, dateformat)
    limit = date(fuckoff.year, fuckoff.month, 7)


def money_per_month():
    ymp = 0

    q = stats.members_query(nick='%', active=True)

    for m in q:

        p = filter(lambda x: x.date < limit, m.payments)
        if len(p) == 0:
            continue

        pu = m.paid_until(p)
        #print('Paid until:', pu)
        diff = pu - current
        diff_months = diff.days / 30
        if int(diff_months) < 1:
            continue


        if pu > current:
            if args.verbose:
                print('`%s` paid until %s' % (m.nick, pu))

            payments = sorted(p, key=lambda x: x.date)

            for idx in range(len((payments)) + 1):
                if m.paid_until(payments[:idx]) > current:
                    req = payments[:idx - 1]
                    ext = payments[idx - 1:]
                    #print('Payments required to reach current:', req)
                    if args.verbose:
                        print('\tExtra payments:', ext)

                        print('\tMonths ahead:', diff_months)

                    if len(ext) == 1:
                        avg = ext[0].amount / ext[0].months
                        s = avg * diff_months

                        if args.verbose:
                            print('\tAdds', s, 'to YMP')
                        ymp += s
                    else:
                        s = 0
                        for e in ext:
                            if e.months > 0:
                                s += e.amount

                        if args.verbose:
                            print('\tAdds', s, 'to YMP')
                        ymp += s

                    if args.verbose:
                        print()
                    break

    return ymp


ymp = money_per_month()
print('YMP', ymp)

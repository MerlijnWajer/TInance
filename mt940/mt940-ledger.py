# -*- coding: utf-8 -*-
from __future__ import print_function

import re
from datetime import date

import hashlib


class MT940Payment(object):
    def __init__(self, **kwargs):
        s = ''
        for x, y in kwargs.items():
            s += str(y)
            setattr(self, x, y)
        self._hash = str(hashlib.sha256(s).hexdigest())

    def __hash__(self):
        return self._hash

def parse(filename):
    f = open(filename, 'r')
    transactions = []
    for line in f:
        if line.startswith("ABNANL2A") or line.startswith("940"):
            continue
        elif line.startswith(':61:'):
            transactions.append([line[4:]])
        elif line.startswith(':86:'):
            transactions[-1].append(line[4:])
        elif not line.startswith(':') and not line.startswith('-'):
            transactions[-1][1] += line
    f.close()
    transregex = re.compile(r'([0-9]{6})[0-9]{4}(C|D)([0-9]*),([0-9]{0,2})N[0-9]{3}NONREF')
    results = []
    for trans in transactions:
        match = transregex.match(trans[0])
        datestr = match.group(1)
        dc = match.group(2)
        d = date(int('20'+datestr[0:2]),int(datestr[2:4]),int(datestr[4:6]))
        cents = match.group(4)
        while len(cents) < 2:
            cents += '0'
        amount = float(match.group(3) + cents) / 100.
        desc = trans[1].strip().replace('\n', '').replace('  ', ' ').replace('\r', '')
        results.append( 
            MT940Payment(**dict(dc=dc, date=d, amount=amount, desc=desc,
                raw=''.join(trans).replace('\r', ''))))
    return results

from member_strings import ID_STRINGS

def identify_member(payment):
    p = payment

    for nick, strings in ID_STRINGS.items():
        for string in strings:
            if p.desc.find(string) > 0:
                return nick

    return None

if __name__ == '__main__':
    import sys
    import re
    ibanres = [re.compile('.*IBAN/([A-Z,0-9]+).*'),
                re.compile('.*IBAN: ([A-Z,0-9]+).*')]

    s = parse(sys.argv[1])

    # Sort by date...
    s = sorted(s, key=lambda x: x.date)

    # TODO: All IBAN
    for x in s:
        # dc, date, amount, desc,
        for r in ibanres:
            iban = r.match(x.desc)
            if iban:
                break

        member = identify_member(x)

        if iban:
            iban = iban.groups()[0]

            if iban.endswith('BIC'):
                iban = iban[0:-3]

        income_str = 'Members' if member else 'Unknown'
        income_str = 'Income:' + income_str

        if not member:
            member = 'Unknown'

        if x.dc == 'D':
            x.amount = -x.amount

        print(';' + x.desc)
        print("""%s %s
    Assets:%s       %s
    %s
        """ % (x.date,
                '%s' % member,
                'Main',
                '€%s' % x.amount,
                income_str if x.dc == 'C' else 'Expenses:TODO')
        )

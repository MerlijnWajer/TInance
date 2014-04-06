import re
from datetime import date

import hashlib

class MT940Payment(object):

    def __init__(self, **kwargs):
        s = ''
        for x, y in kwargs.iteritems():
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
        desc = trans[1].strip().replace('\n', '').replace('  ', ' ')
        results.append( 
            MT940Payment(**dict(dc=dc, date=d, amount=amount, desc=desc,
                raw=''.join(trans))))
    return results

from member_strings import ID_STRINGS

def identify_member(payment):
    p = payment

    for nick, strings in ID_STRINGS.iteritems():
        for string in strings:
            if p.desc.find(string) > 0:
                return nick

    return None
    #raise ValueError('Cannot identify payment')

# Identifying:
# 0) Look for IBAN/<nr>
# 1) Look for GIRO  <nr>
# 2) look for 'MEMBER <NICK>'
# 3) Look for streetname / realname?

if __name__ == '__main__':
    import sys
    s = parse(sys.argv[1])

    if len(sys.argv) == 3:
        rejfd = open(sys.argv[2])
        rej = map(lambda x: x.rstrip('\n'), rejfd.readlines())
    else:
        rej = []


    accept = []
    reject = []

    for x in s:
        if x.dc == 'D':
            pass
        if x._hash in rej:
            print 'Hash (%s) found in previous hashes file; ignoring' % x._hash
            continue

        n = identify_member(x)

        if n:
            accept.append({'nick' : n, 'date' : str(x.date), 'amount' : x.amount,
                'desc' : x.desc, 'hash' : x._hash, 'months' : 1})
        else:
            reject.append({'nick' : 'UNKNOWN', 'date' : str(x.date), 'amount' : x.amount,
                'desc' : x.desc, 'hash' : x._hash, 'months' : 1})

    import json

    print json.dumps(accept, indent=4)
    print >>sys.stderr, json.dumps(reject, indent=4)

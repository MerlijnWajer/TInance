import re
from datetime import date

class MT940Payment(object):

    def __init__(self, **kwargs):
        self._hash = 0
        for x, y in kwargs.iteritems():
            setattr(self, x, y)
            self._hash ^= hash(y)

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
        amount = int(match.group(3) + cents)
        desc = trans[1].strip()
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
    print len(s)
    for x in s:
        n = identify_member(x)
        if n:
            print n, x.desc

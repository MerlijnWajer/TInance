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

from sqlalchemy import Table, Column, Integer, String, Date, func, \
     ForeignKey, Unicode, Boolean, Numeric

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
metadata = Base.metadata

import datetime

md = lambda p: 0 if p.months == 0 else p.amount / p.months

class Member(Base):
    __tablename__ = 'membership_member'

    id = Column(Integer, nullable=False, primary_key=True)
    nick = Column(Unicode(200), nullable=False)
    member_date = Column(Date, nullable=False, default=func.now())
    name = Column(Unicode(200), nullable=False)
    email = Column(Unicode(75), nullable=False)
    bankaccount = Column(Unicode(200), nullable=False, default=u'NaN')
    active = Column(Boolean, nullable=False, default=True)
    fobid = Column(Unicode(5), nullable=False, default=u'NaN')
    keyspaid = Column(Boolean, nullable=False, default=False)

    payments = relationship('Payment', backref=backref('member', order_by=id))

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def months_paid(self, payments):
        return sum(_.months for _ in payments)

    def paid_until(self, payments=None):
        pay = payments if payments is not None else self.payments

        p = self.months_paid(pay)

        y = p / 12
        m = p % 12

        d = self.member_date

        if d.month + m > 12:
            y += 1
            m -= 12

        try:
            d = datetime.date(d.year + y, d.month + m, d.day)
        except ValueError:
            # XXX, YES, I KNOW. Temp fix.
            if d.month == 2:
                d = datetime.date(d.year + y, d.month + m, 30)
            else:
                d = datetime.date(d.year + y, d.month + m, 28)

        return d

    def __repr__(self):
        s = '<Member (%s, %s, %s)>' % (self.name, self.member_date, self.paid_until())
	return s.encode('utf-8')

    def format(self, f, human_read=False):
        """
        id:        %i
        nick:      %n
        name:      %N
        mail:      %m
        join-date: %j
        paid:      %p
        keyid:     %k
        active:    %A
        """
        m = {
            '%i' : str(self.id),
            '%n' : self.nick,
            '%N' : self.name,
            '%m' : self.email,
            '%j' : str(self.member_date.strftime('%A %e, %B') if human_read else self.member_date),
            '%p' : str(self.paid_until().strftime('%A %e, %B') if human_read else self.paid_until()),
            '%k' : str(self.fobid),
            '%A' : str(self.active),
        }

        for pat, repl in m.iteritems():
            f = f.replace(pat, repl)

        return f

class Payment(Base):
    __tablename__ = 'membership_payment'

    id = Column(Integer, nullable=False, primary_key=True)
    member_id = Column(Integer, ForeignKey('membership_member.id'), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Numeric, nullable=False)
    comment = Column(Unicode(200), nullable=False, default=u'')
    months = Column(Integer, nullable=False, default=1)
    #payment_hash = Column(Integer, nullable=True, default=None) # TODO: Remove
    # from DB
    payment_sha256 = Column(String(64), nullable=True, default=None)

    # member -> Member object

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return u'Payment (%d, %d, %d, %s, %s)>' % (self.id, self.amount,
                self.months, self.date, self.comment[:40])

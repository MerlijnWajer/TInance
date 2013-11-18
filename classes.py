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

    def months_paid(self):
        return sum(_.months for _ in self.payments)

    def paid_until(self):
        p = self.months_paid()
        y = p / 12
        m = p % 12

        d = self.member_date

        if d.month + m > 12:
            y += 1
            m -= 12

        return datetime.date(d.year + y, d.month + m, d.day)

    def __repr__(self):
        s = '<Member (%s, %s, %s)>' % (self.name, self.member_date, self.paid_until())
	return s.encode('utf-8')

    def format(self, f):
        """
        id:        %i
        nick:      %n
        name:      %N
        mail:      %m
        join-date: %j
        paid:      %p
        keyid:     %k
        """
        m = {
            '%i' : str(self.id),
            '%n' : self.nick,
            '%N' : self.name,
            '%m' : self.email,
            '%j' : str(self.member_date),
            '%p' : str(self.paid_until()),
            '%k' : str(self.fobid),
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

    # member -> Member object

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return u'Payment (%d, %d, %d, %s)>' % (self.id, self.amount, self.months, self.date)

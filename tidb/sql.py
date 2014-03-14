import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("sqlite:///%s" % ('tidb/db.db'))

from classes import Member, Payment, Base

Base.metadata.create_all(engine)
metadata = Base.metadata
from sqlalchemy.orm import scoped_session, sessionmaker
Session = scoped_session(sessionmaker(bind=engine))

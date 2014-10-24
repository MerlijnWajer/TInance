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


import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("sqlite:///%s" % ('tidb/db.db'))

from classes import Member, Payment, Base

Base.metadata.create_all(engine)
metadata = Base.metadata
from sqlalchemy.orm import scoped_session, sessionmaker
Session = scoped_session(sessionmaker(bind=engine))

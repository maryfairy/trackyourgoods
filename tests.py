from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from datetime import date, timedelta
##sudo pip install python-dateutil --upgrade
from dateutil.relativedelta import relativedelta

from database_setup import Base, User, Closet, Category, Item



engine = create_engine('sqlite:///trackyourgoods.db')

Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)

session = DBSession()


#ClosetNames = session.query(Closet).all()
#for closet in ClosetNames:
#	print closet.id

## ISSUE: When clicking on a closet with no items, get the following error
## NoResultFound: No row was found for one()
## is it because there are no items?

#closet1 = Closet(user_id=1, name="Mary's First Closet")

#r = session.query(Closet).filter_by(id = 4).one()

#print(r)
purchasedate = datetime.date.today() - relativedelta(months=3)
# add an item to 4
# Item1 = Item(name = "Bicycle", \
# 		    description = "Specialized Dolce Elite 2009", \
# 		    value = "$1200", \
# 		    category = "Hobbies", \
# 		    closet = r, \
# 		    upload_date = datetime.date.today(), \
# 		    date_purchased = purchasedate
# 		    )

# session.add(Item1)
# session.commit()

#closet = session.query(Closet).filter_by(id=4).one()
#creator = getUserInfo(closet.user_id)
# items = session.query(Item).filter_by(closet_id=4).all()

# ClosetNames = session.query(Item).filter_by(closet_id=4).all()
# for closet in ClosetNames:
# 	print closet.id
# 	print closet.name

# items = session.query(Closet).all()
# for closet in items:
# 	print closet.id
# 	print closet.name
# 	print closet.user_id
# 	print closet.user

items = session.query(Item).all()
for closet in items:
	print closet.id
	print closet.name


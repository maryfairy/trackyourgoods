from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from datetime import date, timedelta
##sudo pip install python-dateutil --upgrade
from dateutil.relativedelta import relativedelta

from database_setup import Base, User, Closet, Item


engine = create_engine('sqlite:///trackyourgoods.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
# User1 = User(name="Mary Lesbirel", email="marylesbirel@gmail.com",
#              picture='http://www.tofighthiv.org/images/friendraiser_uploads/1770.1000514908.custom.jpg')
# session.add(User1)
# session.commit()

# # Create dummy closet
# closet1 = Closet(user_id=1, name="Mary's First Closet")

# session.add(closet1)
# session.commit()

# ## Date purchased
# purchasedate = datetime.date.today() - relativedelta(months=3)

# Create dummy items
# Item1 = Item(name = "Bicycle", \
# 		    description = "Specialized Dolce Elite 2009", \
# 		    value = "$1200", \
# 		    category = "Hobbies", \
# 		    closet = closet1 \
# 		    #upload_date = datetime.date.today(), \
# 		    #date_purchased = purchasedate
# 		    )

# session.add(Item1)
# session.commit()

# closet2 = Closet(user_id=2, name="Mary's First Closet")

# Item2 = Item(name = "Bicycle", \
# 		    description = "Specialized Dolce Elite 2009", \
# 		    value = "$1200", \
# 		    category = "Hobbies", \
# 		    closet = 2 \
# 		    #upload_date = datetime.date.today(), \
# 		    #date_purchased = purchasedate
# 		    )

# session.add(Item1)
# session.commit()

Item2 = Item(name = "Bicycle", \
		    description = "Specialized Dolce Elite 2009", \
		    value = "$1200", \
		    category = "Hobbies", \
		    closet = 3, \
		    user = 2
		    #upload_date = datetime.date.today(), \
		    #date_purchased = purchasedate
		    )

session.add(Item2)
session.commit()
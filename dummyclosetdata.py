from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from datetime import date, timedelta
##sudo pip install python-dateutil --upgrade
##from dateutil.relativedelta import relativedelta

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
User1 = User(name="Mary Lesbirel", email="marylesbirel@gmail.com",
             picture='http://www.tofighthiv.org/images/friendraiser_uploads/1770.1000514908.custom.jpg')
session.add(User1)
session.commit()

# Create dummy closet
closet1 = Closet(user_id=1, name="Mary's First Closet")

session.add(closet1)
session.commit()

## Date purchased
## purchasedate = datetime.date.today() - relativedelta(months=3)

#Create dummy items
Item1 = Item(name = "Bicycle", \
		    description = "Specialized Dolce Elite 2009", \
		    value = "$1000", \
		    category = "Hobbies", \
		    closet = closet1, \
		    photo_link = "static/img/item/1.jpg"
		    )

Item2 = Item(name = "Camera", \
		    description = "Canon Digital 2008", \
		    value = "$200", \
		    category = "Electronics", \
		    closet = closet1, \
		    photo_link = "static/img/item/2.jpg"
		    )

Item3 = Item(name = "Don Julio", \
		    description = "Unopened Tequila", \
		    value = "$30", \
		    category = "Kitchen + Dining", \
		    closet = closet1, \
		    photo_link = "static/img/item/3.jpg"
		    )

Item4 = Item(name = "Ring", \
		    description = "Tiffany's Ring", \
		    value = "$125", \
		    category = "Clothing", \
		    closet = closet1, \
		    photo_link = "static/img/item/4.jpg"
		    )

Item5 = Item(name = "Bracelet", \
		    description = "David Yurman Bracelet", \
		    value = "$750", \
		    category = "Clothing", \
		    closet = closet1, \
		    photo_link = "static/img/item/5.jpg" 
		    )

session.add(Item1)
session.add(Item2)
session.add(Item3)
session.add(Item4)
session.add(Item5)
session.commit()


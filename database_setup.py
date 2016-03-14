from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

class Closet(Base):
	__tablename__ = 'closet'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name': self.name,
			'id': self.id,
		}

class Category(Base):
	__tablename__ = 'category'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)

class Item(Base):
	__tablename__ = 'item'

	name = Column(String(80), nullable=False)
	id = Column(Integer, primary_key=True)
	description = Column(String(250))
	value = Column(String(8))
	## TODO: should probably add column purchase price, 
	## instead of relying on value
	category = Column(Integer, ForeignKey('category.name'))
	category_id = Column(Integer, ForeignKey('category.id'))
	closet_id = Column(Integer, ForeignKey('closet.id'))
	closet = relationship(Closet)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)
	photo_link = Column(String(250))
	receipt_image = Column(String(250))
	#upload_date = Column(Date)
	#date_purchased = Column(Date)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name': self.name,
			'id': self.id,
		}

engine = create_engine('sqlite:///trackyourgoods.db')

Base.metadata.create_all(engine)
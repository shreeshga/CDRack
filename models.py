from flaskext.sqlalchemy import SQLAlchemy
from CDRack import app
db = SQLAlchemy(app)

class Album(db.Model):
	__tablename__ = 'albums'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(100),unique=True)
	artist = db.Column(db.String(100),unique=True)
	desc = db.Column(db.String(500))
	price = db.Column(db.Float)
	genre = db.Column(db.String(100))
	date = db.Column(db.Float)
	cover_image = db.Column(db.String(100))
	rating = db.Column(db.Integer)
	rating_count  = db.Column(db.Integer)
		


class Song(db.Model):
	__tablename__ = 'songs'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(100),unique=True)
	rating = db.Column(db.Integer)
	duration = db.Column(db.Integer)
	buy_url = db.Column(db.String(500))		
	preview_url = db.Column(db.String(500))			
	youtube_url = db.Column(db.String(500))			
	album_id = db.Column(db.Integer)
	
	
class User(db.Model):
	__tablename__ = 'users'
	name = db.Column(db.String(100))
	email = db.Column(db.String(100),primary_key=True)
	passwd = db.Column(db.String(500))
	
	
	
	
	
	

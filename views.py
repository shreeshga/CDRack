from flask import  flash, session,redirect, url_for, render_template,render_template_string, request, jsonify
from flask import send_from_directory
from flaskext.uploads import UploadSet,configure_uploads, IMAGES,UploadNotAllowed
from flaskext.sqlalchemy import SQLAlchemy
from  sqlalchemy import and_
from sqlalchemy.orm import subqueryload
from sqlalchemy.ext.serializer import loads, dumps


import os
import simplejson as json
import urllib2 as url
import Image

from werkzeug import secure_filename
from CDRack import app #,models
from datetime import datetime
import time

# ========== Imports End here ============ 


images = UploadSet('images', IMAGES)
configure_uploads(app, images) 

# ========  SQLAlchemy ORM Models  ==========

db = SQLAlchemy(app)

class Album(db.Model):
	__tablename__ = 'albums'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(100))
	artist = db.Column(db.String(100))
	desc = db.Column(db.String(500))
	price = db.Column(db.Float)
	genre = db.Column(db.String(100))
	upload_time = db.Column(db.DateTime)
	cover_image = db.Column(db.String(100))
	rating = db.Column(db.Float)
	rating_count  = db.Column(db.Integer)
	songs = db.relationship("Song",lazy='joined',join_depth=2,backref="album", cascade="all, delete-orphan")


class Song(db.Model):
	__tablename__ = 'songs'
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String(100))
	rating = db.Column(db.Float)
	duration = db.Column(db.Integer)
	download_url = db.Column(db.String(500))		
	stream_url = db.Column(db.String(500))			
	youtube_url = db.Column(db.String(500))		
	streamable = db.Column(db.Boolean)		
	album_id = db.Column(db.Integer,db.ForeignKey('albums.id'))
	#album = db.relationship(Album, backref=db.backref('songs', cascade="all, delete-orphan"))
	
	
class User(db.Model):
	__tablename__ = 'users'
	name = db.Column(db.String(100))
	email = db.Column(db.String(100),primary_key=True)
	passwd = db.Column(db.String(500))
		


# =========== Utility Functions ============== 


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def create_thumbnails(filename):
	img = Image.open(os.path.join(app.config['UPLOADED_IMAGES_DEST'],filename))
	img.thumbnail( (600,600) )
	img.thumbnail( (300,300), Image.ANTIALIAS)
	out = os.path.join(app.config['UPLOADED_IMAGES_THUMBS_DEST'],filename)
	img.save(out)
	
#    for columnName in row.__table__.columns.keys():	
def row2dict(row):
	d = {}
	for columnName in row.__table__.columns.keys():	
		d[columnName] = getattr(row, columnName)
	songdict = []
	for song in row.songs:		
		ds = { }
		for cols in song.__table__.columns.keys():	
			ds[cols] = getattr(song,cols)
		songdict.append(ds)
	d['songs'] = songdict
	return d  	
	

# ============ View Functions ==================
  
@app.route('/album/<albumid>', methods=['GET', 'POST'])
def album(albumid):
	album = Album.query.filter(Album.id == albumid).first()
	if request.method == 'POST':
		filename = album.cover_image
		if  request.files['image']:
			file = request.files['image']		
			filename = images.save(file)
			create_thumbnails(filename)
		else: 
			print 'No file'


		data = request.form
		album.id = data['id']
		album.artist = data['artist']
		album.title =  data['title']
		album.url = data['url']
		album.desc = data['desc']
		album.price = data['price']
		album.genre = data['genre']
		album.upload_time = datetime.now()

		# Update Song data
		songtitles = request.form.getlist('songtitle')
		downloadurls = request.form.getlist('downloadurl')
		streamurls = request.form.getlist('streamurl')
		songids = request.form.getlist('songid')
		streamables = request.form.getlist('streamable')
		youtubeurls = request.form.getlist('youtubeurl')
		durations = request.form.getlist('duration')
		songs  = []
		for songtitle,streamurl,downloadurl,youtubeurl,streamable,duration in zip(songtitles,streamurls,downloadurls,youtubeurls,streamables,durations):
			song  = Song.query.filter(and_(Song.title==songtitle,Song.download_url==downloadurl)).first()
			if  song == None:
				song  = Song()
				song.album_id = albumid
				print 'Song Added:',songtitle
			else:
				print 'Song Merged:',songtitle

			song.streamable = streamable
			_time = time.strptime(duration,"%M:%S")
			song.duration = _time[4] * 60 + _time[5]
			song.title  = songtitle
			song.youtube_url = youtubeurl
			song.stream_url = streamurl
			song.download_url  = downloadurl
			songs.append(song)

		album.songs = songs
#		db.session.flush()

		album.cover_image = filename
		db.session.merge(album)
		try:	
			db.session.commit()
		except:
			db.session.rollback()
			flash(u'oh! Its  a Duplicate, Try again')
			return render_template("editalbum.html",album = album)
		flash(u'Album info updated') 
	return render_template("editalbum.html",album = album)
  


@app.route('/albums')
def albums():
	if request.args:
		if request.args['format'] == 'json':
			print 'JSON?'
			album_list = []
			for album in  Album.query.options(subqueryload(Album.songs)).all():
				album_list.append(row2dict(album))	
			dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None	
			return app.response_class(json.dumps(album_list,default=dthandler), mimetype='application/json')
	return render_template('albums.html',albums = Album.query.order_by(Album.id.asc()).all())
 

'''
@app.route('/albums')
def albums():
	if request.args:
		if request.args['format'] == 'json':
			return __unicode__(Album.query.order_by(Album.id.asc()))
	return render_template('albums.html',albums = Album.query.order_by(Album.id.asc()).all())
'''
  
@app.route('/uploads/<filename>')
def album_image(filename):
    return send_from_directory(app.config['UPLOADED_IMAGES_DEST'],
                               filename)

@app.route('/uploads/thumbnails/<filename>')
def album_thumbnail(filename):
    return send_from_directory(app.config['UPLOADED_IMAGES_THUMBS_DEST'],
                               filename)

  
@app.route ('/addalbum',methods=['GET','POST'])
def addalbum():
	album = Album()
	filename = None
	if request.method == 'POST':
		try: 
			file = request.files['image']		
			filename = images.save(file)
			create_thumbnails(filename)
		except: 
			flash(u'No album Cover selected') 
		#return redirect(url_for('uploaded_file',filename=filename))
		data = request.form
		album.artist = data['artist']
		album.title =  data['title']
		album.url = data['url']
		album.desc = data['desc']
		album.price = data['price']
		album.genre = data['genre']
		album.cover_image = filename	
		album.upload_time = datetime.now()
		songtitles = request.form.getlist('songtitle')
		downloadurls = request.form.getlist('downloadurl')
		streamurls = request.form.getlist('streamurl')
		streamables = request.form.getlist('streamable')
		youtubeurls = request.form.getlist('youtubeurl')
		durations = request.form.getlist('duration')
		if len(songtitles) != len(streamurls):
			flash(u' Song info incomplete')
			return render_template('addalbum.html')

		for songtitle,streamurl,downloadurl,youtubeurl,streamable,duration in zip(songtitles,streamurls,downloadurls,youtubeurls,streamables,durations):
			song  = Song()
			song.title = songtitle
			song.stream_url = streamurl
			song.download_url  = downloadurl
			song.streamable = streamable
			_time = time.strptime(duration,"%M:%S")
			song.duration = _time[4] * 60 + _time[5]
			song.youtube_url = youtubeurl			
			album.songs.append(song)
			
		db.session.add(album)
		try:
			db.session.commit()			
		except:
			db.session.rollback()
			flash(u'oh! There was an error, Try again')
			
		flash(u'Album was added Successfully') 
	return render_template('addalbum.html')





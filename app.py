#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# comment
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(), nullable=True)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    upcoming_shows = db.Column(db.ARRAY(db.Integer), foreign_keys='Show.id', nullable=True)
    past_shows  = db.Column(db.ARRAY(db.Integer), foreign_keys='Show.id', nullable=True)
    genres= db.Column(db.String(120))
    show = db.relationship('Show', backref="venue_show", cascade="save-update")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    upcoming_shows = db.Column(db.ARRAY(db.Integer), foreign_keys='Show.id', nullable=True)
    past_shows  = db.Column(db.ARRAY(db.Integer), foreign_keys='Show.id', nullable=True)

    show = db.relationship('Show', backref="artist_show", cascade="save-update")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    showtime = db.Column(db.DateTime)
    upcoming = db.Column(db.Boolean, default = True, nullable=True)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venue_areas = db.session.query(Venue.city, Venue.state).group_by(Venue.state,Venue.city).all()
  data = []
  for area in venue_areas:
    venues = db.session.query(Venue.id,Venue.name,
      Venue.upcoming_shows).filter(Venue.city==area[0],Venue.state==area[1]).all()
    data.append({
        "city": area[0],
        "state": area[1],
        "venues": []
    })
    for venue in venues:
      data[-1]["venues"].append({
              "id": venue[0],
              "name": venue[1],
              "num_upcoming_shows":venue[2]
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  response = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).all()
  data = []

  for v in venue:    
    if (v.upcoming_shows):
      upcoming_shows_count = v.upcoming_shows
    else:
      upcoming_shows_count = 0
    
    if (v.past_shows):
      past_shows_count = v.past_shows
    else:
      past_shows_count = 0
    data.append({
      "id": v.id,
      "name":v.name,
      "address": v.address,
      "phone":v.phone,
      "city": v.city,
      "state":v.state,
      "website":v.website,
      "facebook_link":v.facebook_link,
      "image_link":v.image_link,
      "seeking_talent":v.seeking_talent,
      "seeking_description":v.seeking_description,
      "upcoming_shows":v.upcoming_shows,
      "past_shows":v.past_shows,
      "genres":v.genres.split(','),
      "upcoming_shows_count": upcoming_shows_count,
      "past_shows_count":past_shows_count
    })

  return render_template('pages/show_venue.html', venues=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    address = request.get_json()['address']
    phone = request.get_json()['phone']
    genres = request.get_json()['genres']
    fb_link = request.get_json()['facebook_link']
    image_link = request.get_json()['image_link']
    if (request.get_json()['seeking_talent'] == 'y'):
      seeking_talent = True
    else:
      seeking_talent = False
    
    new_venue = Venue(name=name,city=city,state=state,address=address,phone=phone,image_link=image_link,facebook_link=fb_link,seeking_talent=seeking_talent,genres=genres)
    
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    flash('Venue  was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as e:
    db.session.rollback()
    flash(f'An error occurred. Show could not be listed. Error: {e}')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  # return render_template('pages/home.html')
  return redirect(url_for('index'))
  
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    id = Venue.query.filter_by(id=venue_id).first()
    
    db.session.delete(id)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    flash(f'An error occured. Error:  {e}')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  response = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artists = Artist.query.filter_by(id=artist_id).all()
  data = []

  for a in artists:    
    if (a.upcoming_shows):
      upcoming_shows_count = len(a.upcoming_shows)
    else:
      upcoming_shows_count = 0
    
    if (a.past_shows):
      past_shows_count = len(a.past_shows)
    else:
      past_shows_count = 0
    data.append({
      "id": a.id,
      "name":a.name,
      "phone":a.phone,
      "city": a.city,
      "state":a.state,
      "website":a.website,
      "facebook_link":a.facebook_link,
      "image_link":a.image_link,
      "seeking_venue":a.seeking_venue,
      "seeking_description":a.seeking_description,
      "upcoming_shows":a.upcoming_shows,
      "past_shows":a.past_shows,
      "genres":a.genres.split(','),
      "upcoming_shows_count": upcoming_shows_count,
      "past_shows_count":past_shows_count
    })


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).all()
  form = ArtistForm(request.form, obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artists=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venues = Venue.query.filter_by(id=venue_id).all()
  form = VenueForm(request.form, obj=venues)
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venues)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    genres = request.get_json()['genres']
    facebook_link = request.get_json()['facebook_link']
    image_link = request.get_json()['image_link']
    website = request.get_json()['website']
    
    if (request.get_json()['seeking_venue'] == 'y'):
      seeking_venue = True
    else:
      seeking_venue = False
    
    new_artist = Artist(name=name,city=city,state=state,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website=website,seeking_venue=seeking_venue)
    
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except Exception as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
    flash(f'Error: {e}')
  finally:
    db.session.close()  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    artist_image_link = str(db.session.query(Artist.image_link).filter_by(id=show.artist).first()).replace("(",'').replace(")",'').replace(",",'').replace("'",'')
    artist_name = str(db.session.query(Artist.name).filter_by(id=show.artist).one()).replace("(",'').replace(")",'').replace(",",'').replace("'",'')
    venue_name = str(db.session.query(Venue.name).filter_by(id=show.venue).first()).replace("(",'').replace(")",'').replace(",",'').replace("'",'')
    
    data.append({
      "artist_image_link": artist_image_link,
      "showtime": show.showtime,
      "artist_id": show.artist,
      "artist_name":artist_name,
      "venue_id": show.venue,
      "venue_name": venue_name

    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  venue_id = form.venue_id.data,
  artist_id = form.artist_id.data,
  start_time = form.start_time.data

  new_show = Show(artist=artist_id,venue=venue_id,showtime=start_time)

  try:
    db.session.add(new_show)
    db.session.commit()    

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except Exception as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash(f'Error: {e}')

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

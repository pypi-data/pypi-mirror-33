from flask import current_app as app
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.orm import aliased

db = SQLAlchemy()

class twitter_creds(db.Model):

    __tablename__ = 'twitter_creds'

    # Meta-data
    id = db.Column(db.Integer, primary_key=True)
    consumer_key = db.Column(db.String)
    consumer_secret = db.Column(db.String)
    callback_url = db.Column(db.String)
    def __repr__(self):
        return '<Twitter creds {}>'.format(self.callback_url)

class user_details(db.Model):

    __tablename__ = 'user_details'

    # Meta-data
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String)
    screenname = db.Column(db.String)
    credId =  db.Column(db.Integer,  db.ForeignKey('twitter_creds.id'))
    twitter_creds =  db.relationship(twitter_creds, backref='twitter_creds')
    def __repr__(self):
        return '<user details {}>'.format(self.screenname)



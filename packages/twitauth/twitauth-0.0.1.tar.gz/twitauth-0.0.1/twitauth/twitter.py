from flask import Flask, redirect, url_for, request, render_template, abort, session, flash
from sqlalchemy import create_engine, MetaData, Column, Integer, Float, String, Table, ForeignKey
from requests_oauthlib import OAuth1, OAuth1Session
import requests
from twitter_model import twitter_creds, user_details


twitter_info = {}
origin_url = ""
twitter_url = { "request_token_url": "https://api.twitter.com/oauth/request_token",
                 "authenticate_url": "https://api.twitter.com/oauth/authenticate?oauth_token=",
                 "access_token_url": "https://api.twitter.com/oauth/access_token"
            }
dict = {}

class twitter_login():
    def __init__(self, credId, db, callback_endpoint):
        self.credId = credId
        self.db = db
        self.callback_endpoint = callback_endpoint

    def twittertables(self, db_uri):
        engine = create_engine(db_uri)  # Access the DB Engine
        if not engine.dialect.has_table(engine, "twitter_creds"):  # If table don't exist, Create.
            metadata = MetaData(engine)
            Table("twitter_creds", metadata,
                Column('id', Integer, primary_key=True, nullable=False),
                Column('consumer_key', String(255)), Column('consumer_secret', String(255)), 
                Column('callback_url', String(255)))
            

            Table("user_details", metadata,
                Column('Id', Integer, primary_key=True, nullable=False), 
                Column('userId', String(50)),
                Column('screenname', String(200)),
                Column('credId', Integer, ForeignKey('twitter_creds.id')))

            metadata.create_all()
        else:
            print ("tables already created")

    def init_lib(self, app):
        @app.route('/index123')
        def index_lib():
            access_token = session.get('access_token')
            if access_token is None:
                return redirect(url_for('auth'))
        
            access_token = access_token[0]
        
            return render_template('index.html')

        @app.route('/auth')
        def auth():
            global dict
            global origin_url
            print (request.environ["HTTP_REFERER"])
            origin_url = request.environ["HTTP_REFERER"]
            
           
            twitter_info_new = twitter_creds.query.get(self.credId)
            twitter_info["consumer_key"] = twitter_info_new.consumer_key
            twitter_info["consumer_secret"] = twitter_info_new.consumer_secret
            twitter_info["callback_url"] = twitter_info_new.callback_url
            url = twitter_url['request_token_url']

            try:
                twitter = OAuth1Session(twitter_info["consumer_key"],
                                        client_secret=twitter_info["consumer_secret"],
                                        )
                resp = twitter.post(url)
            except Exception as e:
                print ("Something went wrong ",e)

            if resp.status_code == 200:
                for i in resp.text.split('&'):
                    split = i.split('=')
                    for j in range(0,1):
                        dict[split[j]] = split[j+1]
            else:
                print ("Request Failed ",resp.status_code)

            go_to_twitter = twitter_url['authenticate_url']+dict["oauth_token"]
            return redirect(go_to_twitter, code=302)

        @app.route(self.callback_endpoint)
        def oauth_authorized():
            global dict
            
            dict['oauth_verifier'] = request.args.get("oauth_verifier")
            url = twitter_url['access_token_url']

            try:
                twitter = OAuth1Session(twitter_info["consumer_key"],
                                        client_secret=twitter_info["consumer_secret"],
                                        resource_owner_key=dict["oauth_token"],
                                        resource_owner_secret=dict["oauth_token_secret"])
                data = {"oauth_verifier":dict['oauth_verifier']}
                response = twitter.post(url, data=data)
            except Exception as e:
                print ("Something went wrong ",e)
            resp = {}
            if response.status_code == 200:        
                for i in response.text.split('&'):
                    split = i.split('=')
                    for j in range(0,1):
                        resp[split[j]] = split[j+1]
            else:
                print ("Request Failed ",response.status_code)
            
            user_count = user_details.query.filter(user_details.userId == resp['user_id']).count()
            if user_count == 0:
                User_details = user_details(userId=resp['user_id'], screenname=resp['screen_name'], credId=self.credId)
                self.db.session.add(User_details)
                self.db.session.commit()
            else:
                print (user_count)
                print ("already fhddh there", 948795948)
            access_token = resp['oauth_token']
            session['access_token'] = access_token
            session['screen_name'] = resp['screen_name']
        
            session['twitter_token'] = (
                resp['oauth_token'],
                resp['oauth_token_secret']
            )

            return redirect(origin_url)

        @app.route('/logout')
        def logout():
            session.pop('screen_name', None)
            return redirect(request.referrer or url_for('index_lib'))




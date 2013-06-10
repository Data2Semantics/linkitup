from dropbox import session as db_session
from dropbox import client
from flask import request, session, render_template, redirect, url_for, g
from app import app, db, lm, oid, nanopubs_dir




APP_KEY = 'r2mo1zdpeg0vnw3'
APP_SECRET = 'xgurgou9iosk3c7'
ACCESS_TYPE = 'dropbox' # should be 'dropbox' or 'app_folder' as configured for your app


def get_session():
    return db_session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

@app.route('/dropbox_authorize')
def dropbox_authorize():
    
    # We only land on this page, if the user does not yet have granted access
    
    sess = get_session()
    request_token = sess.obtain_request_token()
    
    session['dropbox_request_token_key'] = request_token.key
    session['dropbox_request_token_secret'] = request_token.secret
    
    print request_token.key, request_token.secret

    callback = "http://localhost:5000" + url_for(dropbox_callback)
    oauth_request_auth_url = sess.build_authorize_url(request_token, oauth_callback=callback)
    
    print oauth_request_auth_url
    session.modified = True
    print "2"
    return redirect(oauth_request_auth_url)
    

@app.route('/dropbox_callback', methods=['GET'])
def dropbox_callback():
    request_token_key = request.args.get('oauth_token')
    
    if not request_token_key:
        return "Expected a request token key back!"
    
    print request_token_key
    
    sess = get_session()
    
    if session['dropbox_request_token_key'] != request_token_key :
        return "Request tokens do not match!"
    
    request_token_secret = session['dropbox_request_token_secret']
    
    request_token = db_session.OAuthToken(request_token_key,request_token_secret)
    access_token = sess.obtain_access_token(request_token)
    
    session['dropbox_access_token_key'] = access_token.key
    session['dropbox_access_token_secret'] = access_token.secret
        
    g.user.dropbox_access_token_key = access_token.key
    g.user.dropbox_access_token_secret = access_token.secret
    
    print "Committing DB session"
    db.session.commit()
    print "Good to go!"
    
    return redirect(url_for('dropbox'))

@app.route('/dropbox/list')
def dropbox_list():
    sess = get_session()
    sess.set_token(g.user.dropbox_access_token_key, g.user.dropbox_access_token_secret)
    
    db_client = client.DropboxClient(sess)
    
    print "linked account:", db_client.account_info()

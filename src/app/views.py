from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, db, lm, oid, plugins

from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN

from pprint import pprint

import yaml

from util.figshare import figshare_authorize, get_auth_url, validate_oauth_verifier, get_articles, update_article

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    

@app.route('/')
@app.route('/index')
def index():
#    if g.user:
#        user = g.user
#    else :
#        user = "<none>"

    
    return render_template('landing.html', 
                           user=g.user)
    

@app.route('/dashboard')
@login_required
def dashboard():
    """If this session has not yet been initialized (i.e. we don't yet have an oauth_token from Figshare), 
    it starts up the three-legged authentication procedure for OAuth v1.
    
    Otherwise, it initializes the session variable with the article details of the Figshare author
    
    """
    
    if g.user.oauth_token == None or g.user.oauth_token == "" :
        """This user does not yet have an oauth_token, so redirect to the authorization page"""
        
        return redirect(url_for('figshare_authorize'))
    else :
        """
        This is where we retrieve all articles of the Figshare author who provided the authentication.
        """
        
        try :
            if 'items' in session:
                app.logger.debug("Already found items! YAY")
            else:
                app.logger.debug("No items found bleh")
                
            get_articles()

            app.logger.debug(pprint(session))


            session.modified = True
            
            return render_template('articles.html', 
                               raw = str(session['items']),
                               results = session['items'], 
                               plugins = plugins.values(),
                               user = g.user)
            
        except Exception as e :
            return render_template('error.html', 
                                   message = "Error retrieving articles!: " + e.message, 
                                   user=g.user)
        

        
@app.route('/clear')
@login_required
def clear():
    logout_user()
    session.clear()
    return render_template('warning.html', 
                           message = "Session data cleared!",
                           user = g.user)

## LOGIN Stuff below

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['fullname', 'email'])
    return render_template('login.html', 
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('index'))
        
    user = User.query.filter_by(email = resp.email).first()
    
    if user is None:
        app.logger.warning(resp)
        
        nickname = resp.fullname
        
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    
    remember_me = False
    
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
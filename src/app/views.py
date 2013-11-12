from flask import render_template, flash, redirect, session, url_for, request, g, make_response, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, db, lm, oid, plugins

from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN

from pprint import pprint

import yaml

from util.figshare import figshare_authorize, get_auth_url, validate_oauth_verifier, get_articles, get_article, update_article, FigshareEmptyResponse, FigshareNoTokenError
from util.rdf import get_rdf, get_trig

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    app.logger.debug(request.path)
    g.user = current_user
    

@app.route('/')
@app.route('/index')
def index():
    return render_template('landing.html', 
                          user=g.user)
    

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('articles.html', user = g.user, results = {}, plugins = plugins.values())
    
@app.route('/articles')
@login_required
def load_articles():
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
            articles, details = get_articles()
            
            return jsonify({'articles': articles, 'details': details})
            
            # return render_template('articles.html', 
            #                    results = articles, 
            #                    plugins = plugins.values(),
            #                    user = g.user)
        except FigshareEmptyResponse as e :
            app.logger.error(e)
            return redirect(url_for('figshare_authorize'))
        except FigshareNoTokenError as e :
            app.logger.error(e)
            return redirect(url_for('figshare_authorize'))
        except Exception as e :
            app.logger.error(e)
            return render_template('error.html', 
                                   message = "Error retrieving articles!: " + e.message, 
                                   user=g.user)
        
@app.route('/plugins')
@login_required
def load_plugins():
    return jsonify({'result': plugins.values()})
    
    
@app.route('/details', methods=['POST'])
@login_required
def article_details():
    app.logger.debug(request)
    try :
        article = request.get_json()
        app.logger.debug(article)
    except Exception as e:
        app.logger.error(e)
        app.logger.debug("Something went wrong!")
    
    if article == None :
        article = request.get_json(force=True)
        app.logger.debug("Forced parsing")
        app.logger.debug(article)
    
    return render_template('article_details.html', article=article)
    

@app.route('/refresh', methods=['POST'])
@login_required
def refresh_article():
    data = request.get_json()

    article = get_article(data['article_id'])
    
    app.logger.debug(article)
    
    return jsonify({'details': article})


@app.route('/nanopublication', methods = ['POST'])
@login_required
def nanopublication():
    
    data = request.get_json()

    details = data['details']
    selected = data['selected']


    graphTrig = get_trig(details, selected)
    
    return graphTrig

    # response = make_response(graphTrig)
    # response.mimetype = "application/trig"
    # response.contenttype = "application/trig"
    # response.headers.add('Content-Disposition', 'attachment; filename={}.trig'.format(article_id))



@app.route('/publish', methods = ['POST'])
@login_required
def publish():
    data = request.get_json()
    
    details = data['details']
    selected = data['selected']
    
    try :
        update_article(details, selected)
        return jsonify({'success': True})    
    except :
        return jsonify({'success': False})


@app.route('/provenance', methods=['POST'])
@login_required
def provenance():
	data = request.get_json()

	provenance_trail = data['provenance']
		
	prov = trail_to_prov(provenance_trail)
	
	PROVOVIZ_SERVICE_URL = "http://semweb.cs.vu.nl/provoviz/service"
	# PROVOVIZ_SERVICE_URL = "http://localhost:8000/service"
	
	r = requests.post(PROVOVIZ_SERVICE_URL,data={'graph_uri': 'http://example.com/test', 'data': prov, 'client': 'linkitup'})
	
	if r.status_code == requests.codes.ok :
		app.logger.debug("Success for provoviz!")
		return jsonify({'success':True,'result': r.content})
	else :
		app.logger.debug("Failure for provoviz!")
		return jsonify({'success':False,'result': prov})

@app.route('/clear')
def clear_session_data():
    app.logger.debug("Logging out user")
    logout_user()
    app.logger.debug("Clearing session data")
    session.clear()
    app.logger.debug("Session data cleared")
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
import os
import yaml
import pickle
import sys

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

from simplekv.fs import FilesystemStore
from flaskext.kvsession import KVSessionExtension
from flaskext.uploads import UploadSet, configure_uploads

from config import basedir


this_dir = os.path.dirname(__file__)
sys.path.insert(0, this_dir)

# Make sure we have an absolute path to the template dir
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder = tmpl_dir)
app.logger.debug("Initializing Linkitup")

app.debug = True
app.logger.debug("Set app.debug=True")

# Initialize a simplekv FileystemStore in the tmp directory 
store = FilesystemStore(os.path.join(basedir, 'tmp'))
# this will replace the app's session handling
KVSessionExtension(store, app)

app.logger.debug("Added KVSessionExtension file system store")

app.config.from_object('config')

app.logger.debug("Loaded configuration")

db = SQLAlchemy(app)

app.logger.debug("Intialized database")

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.logger.debug("Initialized LoginManager")

oid = OpenID(app, os.path.join(basedir, 'tmp'))

app.logger.debug("Initialized OpenID module")

# setup flask-uploads

pdfs = UploadSet('pdfs', extensions=('pdf'))
configure_uploads(app, (pdfs))

app.logger.debug("Initialized UploadSet 'pdf'")

try :
    app.logger.debug("Loading plugins...")
    
    plugins = yaml.load(open(app.config['PLUGINS_FILE'],'r'))
    
    map(__import__, plugins.keys())
    
    app.logger.debug("Intialized plugins")
    
except Exception as e :
    app.logger.error("Error loading plugins from {}".format(app.config['PLUGINS_FILE']))
    app.logger.error(e.message)
    quit()

app.logger.debug("Now importing views and models")
from app import views, models

app.logger.debug("Finalized initialization")

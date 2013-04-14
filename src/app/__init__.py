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



# Add the current dir to the Python path
this_dir = os.path.dirname(__file__)
sys.path.insert(0, this_dir)


# Make sure we have an absolute path to the template dir
TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


# Intialize the Flask Appliation
app = Flask(__name__, template_folder = TEMPLATE_FOLDER)

# Load the configuration file
app.config.from_object('config')
app.debug = app.config['DEBUG']

app.logger.debug("Loaded configuration")

app.logger.info("Set app.debug={}".format(app.debug))

if not app.debug:
    import logging
    from logging.handlers import TimedRotatingFileHandler
    from logging import Formatter
    
    log_folder = app.config['LOG_FOLDER']
    
    if not os.path.exists(log_folder) :
        app.logger.warning("Log folder '{}' does not exist, creating".format(log_folder))
        os.mkdir(log_folder)
    
    log_file = os.path.join(log_folder, 'linkitup.log')
    
    # Start a timed rotating filehandler, for the WARNING level, that rotates the logs every Sunday
    file_handler = TimedRotatingFileHandler(log_file, when='W6')
    file_handler.setLevel(logging.INFO)
    
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    
    app.logger.addHandler(file_handler)



app.logger.debug("Initializing Linkitup Flask Application")






# Setup the Nanopublication Store
nanopubs_dir = app.config['NANOPUBLICATION_STORE']
app.logger.debug("Setting RDF Nanopublications storage location (temporary) to: {}".format(nanopubs_dir))

if not os.path.exists(nanopubs_dir) :
    app.logger.warning("Nanopublications folder '{}' does not yet exist: creating it!".format(nanopubs_dir))
    os.mkdir(nanopubs_dir)



# Setup the Session Store
if not os.path.exists(app.config['SESSION_STORE']) :
    app.logger.warning("Session store folder '{}' does not yet exist: creating it!".format(app.config['SESSION_STORE']))
    os.mkdir(app.config['SESSION_STORE'])

# Initialize a simplekv FileystemStore in the tmp directory 
store = FilesystemStore(app.config['SESSION_STORE'])
# this will replace the app's session handling
KVSessionExtension(store, app)

app.logger.debug("Added KVSessionExtension file system store")


# Setup SQLAlchemy

db = SQLAlchemy(app)

app.logger.debug("Intialized database")





# Setup LoginManager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.logger.debug("Initialized LoginManager")

# Setup OpenID
oid = OpenID(app, os.path.join(basedir, 'tmp'))

app.logger.debug("Initialized OpenID module")

# Setup flask-uploads

pdfs = UploadSet('pdfs', extensions=('pdf'))
configure_uploads(app, (pdfs))

app.logger.debug("Initialized UploadSet 'pdf'")


# Load the plugins
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
import views, models




app.logger.debug("Finalized initialization")

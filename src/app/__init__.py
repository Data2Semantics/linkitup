import os
import yaml
import pickle

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

from simplekv.fs import FilesystemStore
from flaskext.kvsession import KVSessionExtension

from config import basedir



# Initialze a simplekv FileystemStore in the tmp directory 
store = FilesystemStore('tmp')


app = Flask(__name__)

# this will replace the app's session handling
KVSessionExtension(store, app)

app.config.from_object('config')

db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))


try :
    plugins = yaml.load(open(app.config['PLUGINS_FILE'],'r'))
    
    map(__import__, plugins.keys())
except Exception as e :
    print "Error loading plugins from {}".format(app.config['PLUGINS_FILE']) 
    print e.message
    quit()


from app import views, models


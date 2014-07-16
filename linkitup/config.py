import os
import tempfile

configdir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.dirname(configdir)
tempdir = tempfile.gettempdir()

FIGSHARE_CALLBACK_URI = 'http://localhost:5000/callback'

# These articles appear in the dashboard if the user did not authenticate with Figshare
FIGSHARE_PREVIEW_IDS = ['828798' ,'90206', '860460', '91672', '92089', '785731', '104629', '94593']

SESSION_COOKIE_NAME = "linkitup_session"

CSRF_ENABLED = True
SECRET_KEY = '\x14%<`2\xecT*\xa7M\xd0\x90%\x8d\x9a\xdd\xdbCF\xec\x96\x0e\x0e\x96'

OPENID_FS_STORE_PATH = os.path.join(basedir, 'tmp')
OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
    
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# Setup Upload locations

UPLOADS_DEFAULT_DEST = os.path.join(tempdir, 'linkitup')

# Setup Plugins

PLUGINS_FILE = os.path.join(configdir, "plugins.yaml")

# Session store location

SESSION_STORE = os.path.join(basedir, 'tmp')

# Nanopublications store location

NANOPUBLICATION_STORE = os.path.join(basedir, 'nanopublications')

## Graph Store configuration

# GRAPH_STORE_ENDPOINT = 'http://d2s.ops.few.vu.nl/rdf-graph-store'
# GRAPH_STORE_AUTH = 'linkitup:password'

# Logging folder

LOG_FOLDER = os.path.join(basedir, 'log')


# Logging at DEBUG level?

DEBUG = True

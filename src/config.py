import os
import tempfile

basedir = os.path.abspath(os.path.dirname(__file__))
tempdir = tempfile.gettempdir()

SERVER_NAME = "linkitup.dev:5000"
SESSION_COOKIE_NAME = "linkitup_session"


CSRF_ENABLED = True
SECRET_KEY = '\x14%<`2\xecT*\xa7M\xd0\x90%\x8d\x9a\xdd\xdbCF\xec\x96\x0e\x0e\x96'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
    
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Setup Upload locations

UPLOADS_DEFAULT_DEST = os.path.join(tempdir, 'linkitup')

# Setup Plugins

PLUGINS_FILE = "/Users/hoekstra/projects/data2semantics/linkitup/src/plugins.yaml"
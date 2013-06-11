import os
import tempfile

basedir = os.path.abspath(os.path.dirname(__file__))
tempdir = tempfile.gettempdir()

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

PLUGINS_FILE = os.path.join(basedir, "plugins.yaml")

# Session store location

SESSION_STORE = os.path.join(basedir, 'tmp')

# Nanopublications store location

NANOPUBLICATION_STORE = os.path.join(basedir, 'nanopublications')

# Logging folder

LOG_FOLDER = os.path.join(basedir, 'log')

# Figshare

# client_key = 'K9qG70PgROIg8CpZGJlGRg'
# client_secret = '0JdZcz5pz0HwyWbeiwsviA'

FIGSHARE_CLIENT_KEY = 'K9qG70PgROIg8CpZGJlGRg'
FIGSHARE_CLIENT_SECRET = '0JdZcz5pz0HwyWbeiwsviA'

# LibreOffice & unoconv

LIBRE_OFFICE_PYTHON_PATH = "/Applications/LibreOffice.app/Contents/MacOS/python"
UNOCONV_PATH = "/Users/hoekstra/projects/data2semantics/linkitup/src/app/util/unoconv.py"

# -f ods ~/Dropbox/Data2Semantics/hackathon/excelSheets/timeValueConcepts.xls

# Cat

CAT_PATH = "/Users/hoekstra/Dropbox/Data2Semantics/hackathon/cat/cat.jar"
CAT_OUTPUT_PATH = "/Users/hoekstra/projects/data2semantics/cat"
CAT_BASE_URL = "http://localhost:8000"

# Plsheet

PLSHEET_PATH = "/Users/hoekstra/projects/data2semantics/plsheet/ods2rdf.pl"

# RScripts

NWANALYSIS_PATH = "/Users/hoekstra/projects/data2semantics/nwanalysis/runAllAlgs.R"
NWANALYSIS_OUTPUT_PATH = "/Users/hoekstra/projects/data2semantics/cat/nwanalysis"
NWANALYSIS_BASE_URL = "http://localhost:8000/nwanalysis"
NWANALYSIS_EXPLORER_PATH = "/Users/hoekstra/Dropbox/data2semantics/hackathon/sheet_explore"


# Logging at DEBUG level?

DEBUG = True



from flask_openid import OpenID

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


## Settings
DEBUG = True
SECRET_KEY = 'something very very secret and unique'
HOST = 'mac311.few.vu.nl'

## Linkitup App
linkitup = Flask(__name__)
linkitup.debug = DEBUG
linkitup.secret_key = SECRET_KEY
linkitup.host = HOST

linkitup.config.update(
    DATABASE_URI = 'sqlite:////tmp/flask-openid.db',
    SECRET_KEY = 'development key',
    DEBUG = True
)

# setup flask-openid
oid = OpenID(linkitup)




# setup sqlalchemy
engine = create_engine(linkitup.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid
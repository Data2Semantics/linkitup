from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    

    oauth_token = db.Column(db.String(66))
    oauth_token_secret = db.Column(db.String(22))
    xoauth_figshare_id = db.Column(db.String(5))
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)    
        

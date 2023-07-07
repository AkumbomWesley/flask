from app import db 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin #includes generic implementations that are appropriate for most user model classes
from app import login
from hashlib import md5
from time import time
import jwt
from app import app
from flask import url_for

#creating association table for relationship between followed and follower
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))    
        )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email= db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    post =  db.relationship('Post', backref='author', lazy='dynamic') #db.relationship is normally defined on the one side of a one to many rel
    #backref argument defines the name of a field that will be added to the objects of the many class that points back at the one objesct
    #lazy defines how the db query will be issued
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id), #references the follower_id column of the association table
        secondaryjoin = (followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic' #dynamic sets up the query to not run until specifically requested
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
  
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self,user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0          
    
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password':self.id, 'exp': time() + expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return 
        return User.query.get(id)      
                           
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def to_dict(self, include_email=False): #to_dict converts user object to python rep which is then convertd to JSON format
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed_count(),
            'links':{
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email 
        return data 
    
    def from_dict(self, data, new_user=False): #converts dictionary back to model
        for field in ['username', 'email', 'about_me']:
            if field in data: 
                setattr(self, field, data[field])
            if new_user and 'password' in data:
                self.set_password(data['password'])
                
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return '<Post {}>'.format(self.body)

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page=page, per_page=per_page, eroor_out=False)
        data = {
            'items' : [item.to_dict( for item in resources.items )]
        }        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))



    
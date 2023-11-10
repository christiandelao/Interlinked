from . import db 
from flask_login import UserMixin 
from sqlalchemy.sql import func 
from hashlib import md5

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(150), unique = True)
    email = db.Column(db.String(150), unique = True) 
    password = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone = True), default = func.now()) 
    posts = db.relationship('Post', backref = 'user', passive_deletes = True)
    comments = db.relationship('Comment', backref = 'user', passive_deletes = True)
    likes = db.relationship('Likes', backref = 'user', passive_deletes = True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
class Post(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False) 
    text = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime(timezone = True), default = func.now()) 
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable = False)
    comments = db.relationship('Comment', backref = 'post', passive_deletes = True) 
    likes = db.relationship('Likes', backref = 'post', passive_deletes = True)     


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(250), nullable = False)
    created_at = db.Column(db.DateTime(timezone = True), default = func.now()) 
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable = False) 

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime(timezone = True), default = func.now()) 
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable = False) 

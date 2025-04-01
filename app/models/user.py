from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt
import os
from time import time

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    canvas_id = db.Column(db.String(64), index=True, unique=True, nullable=True)
    name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_study_plans = db.relationship('StudyPlan', backref='creator', lazy='dynamic')
    group_memberships = db.relationship('GroupMember', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            os.environ.get('SECRET_KEY', 'dev-key'),
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token,
                os.environ.get('SECRET_KEY', 'dev-key'),
                algorithms=['HS256']
            )['reset_password']
        except:
            return None
        return User.query.get(id)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 
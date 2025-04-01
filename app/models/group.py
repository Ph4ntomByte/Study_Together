from app import db
from datetime import datetime

class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('GroupMember', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    study_plans = db.relationship('StudyPlan', backref='related_group', lazy='dynamic')
    messages = db.relationship('GroupMessage', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    location_change_requests = db.relationship('LocationChangeRequest', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<StudyGroup {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'member_count': self.members.count()
        }


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'group_id', name='unique_user_group'),)
    
    def __repr__(self):
        return f'<GroupMember user_id={self.user_id} group_id={self.group_id}>'


class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    sender = db.relationship('User', backref='sent_messages')
    
    def __repr__(self):
        return f'<GroupMessage {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'group_id': self.group_id,
            'user_id': self.user_id,
            'sender_name': self.sender.name
        }


class JoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plan.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='join_requests')
    study_plan = db.relationship('StudyPlan', backref='join_requests')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'study_plan_id', name='unique_user_study_plan'),)
    
    def __repr__(self):
        return f'<JoinRequest {self.id}>'


class LocationChangeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposed_location = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plan.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    
    # Relationship
    requester = db.relationship('User', backref='location_change_requests')
    study_plan = db.relationship('StudyPlan', backref='location_change_requests')
    
    # Votes
    votes = db.relationship('LocationChangeVote', backref='request', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LocationChangeRequest {self.id}>'


class LocationChangeVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.Boolean, nullable=False)  # True for approve, False for reject
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    request_id = db.Column(db.Integer, db.ForeignKey('location_change_request.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship
    voter = db.relationship('User', backref='location_change_votes')
    
    __table_args__ = (db.UniqueConstraint('request_id', 'voter_id', name='unique_request_voter'),) 
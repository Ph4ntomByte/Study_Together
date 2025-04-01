from app import db
from datetime import datetime
import secrets
import uuid
from flask_login import current_user

class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    share_link = db.Column(db.String(36), unique=True)
    
    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=True)
    
    # Relationships
    # Note: 'creator' backref is defined on the User model
    # Note: 'related_group' backref is defined on the StudyGroup model
    
    def __repr__(self):
        return f'<StudyPlan {self.title}>'
    
    def generate_share_link(self):
        self.share_link = str(uuid.uuid4())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'is_public': self.is_public,
            'max_participants': self.max_participants,
            'created_at': self.created_at.isoformat(),
            'creator_id': self.creator_id,
            'creator_name': self.creator.username,
            'group_id': self.group_id
        }
    
    def is_member(self, user):
        """Check if a user is a member of this study plan's group."""
        if not self.group_id or not user.is_authenticated:
            return False
        
        from app.models.group import GroupMember
        membership = GroupMember.query.filter_by(
            user_id=user.id,
            group_id=self.group_id
        ).first()
        
        return membership is not None


class TimeChangeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposed_start_time = db.Column(db.DateTime, nullable=False)
    proposed_end_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    study_plan_id = db.Column(db.Integer, db.ForeignKey('study_plan.id'), nullable=False)
    
    # Relationship
    requester = db.relationship('User', backref='time_change_requests')
    study_plan = db.relationship('StudyPlan', backref='time_change_requests')
    
    def __repr__(self):
        return f'<TimeChangeRequest {self.id}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'proposed_start_time': self.proposed_start_time.isoformat(),
            'proposed_end_time': self.proposed_end_time.isoformat(),
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'requester_id': self.requester_id,
            'study_plan_id': self.study_plan_id,
            'type': 'time',
            'requester': {
                'id': self.requester.id,
                'username': self.requester.username,
                'name': self.requester.name
            }
        } 
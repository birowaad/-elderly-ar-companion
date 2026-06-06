from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='elderly')  # 'elderly', 'family', 'admin'
    
    # Elderly specific fields
    age = db.Column(db.Integer, default=65)
    interests = db.Column(db.String(500), default='')
    mood_history = db.Column(db.Text, default='[]')  # JSON array
    daily_log = db.Column(db.Text, default='[]')  # JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Family connections
    family_members = db.Column(db.Text, default='[]')  # JSON array of family IDs
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)
    
    def get_mood_history(self):
        return json.loads(self.mood_history) if self.mood_history else []
    
    def add_mood_entry(self, mood_score, note=''):
        history = self.get_mood_history()
        history.append({
            'date': datetime.utcnow().isoformat(),
            'score': mood_score,
            'note': note
        })
        # Keep only last 30 days
        self.mood_history = json.dumps(history[-30:])
    
    def get_daily_log(self):
        return json.loads(self.daily_log) if self.daily_log else []
    
    def add_activity_log(self, activity_type, details):
        log = self.get_daily_log()
        log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': activity_type,
            'details': details
        })
        self.daily_log = json.dumps(log[-100:])  # Keep last 100 logs
    
    def get_interests_list(self):
        return [i.strip() for i in self.interests.split(',') if i.strip()] if self.interests else []
    
    def get_family_members(self):
        return json.loads(self.family_members) if self.family_members else []
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


class Interaction(db.Model):
    """تسجيل تفاعلات المسن مع التطبيق"""
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # 'chat', 'game', 'meditation', 'call'
    duration_seconds = db.Column(db.Integer, default=0)
    completion = db.Column(db.Float, default=0.0)
    metadata = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='interactions')


class MoodAssessment(db.Model):
    """تقييمات الحالة النفسية (للورقة العلمية)"""
    __tablename__ = 'mood_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # UCLA Loneliness Scale (3-9)
    loneliness_score = db.Column(db.Integer, nullable=False)
    
    # PHQ-9 Depression Scale (0-27)
    depression_score = db.Column(db.Integer, nullable=False)
    
    # SWLS Life Satisfaction (5-35)
    life_satisfaction_score = db.Column(db.Integer, nullable=False)
    
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='assessments')

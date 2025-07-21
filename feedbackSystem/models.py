from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    sentiment = db.Column(db.String(20))  # positive, neutral, negative
    category = db.Column(db.String(50))   # suggestion, complaint, question, etc.
    resolved = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Feedback {self.id}>'
        

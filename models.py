from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

#@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(100))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_team_tasks = db.relationship('Task', backref=db.backref('assigned_team_member'), lazy=True)

    def __repr__(self):
        return f'<TeamMember {self.name}>'


'''
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Not Started')
    tasks = db.relationship('Task', backref='project', lazy=True)

    def __repr__(self):
        return f'<Project {self.name}>'
'''

'''
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='To Do')
    priority = db.Column(db.String(20), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('team_member.id'))


    def __repr__(self):
        return f'<Task {self.title}>'
'''

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='Not Started')
    progress = db.Column(db.Integer, default=0)  # 0-100%
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def update_progress(self):
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            self.progress = 0
        else:
            completed_tasks = len([task for task in self.tasks if task.status == 'Completed'])
            self.progress = int((completed_tasks / total_tasks) * 100)
        db.session.commit()

    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='To Do')
    priority = db.Column(db.String(20), default='Medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'))
    team_member = db.relationship('TeamMember', backref='tasks')
    
    # Relationships
    attachments = db.relationship('Attachment', backref='task', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='task', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Task {self.title}>'

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50)) # Add role field
    assigned_task = db.relationship('Task', foreign_keys='Task.assignee_id', backref=db.backref('assignee', lazy=True), lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    created_task = db.relationship('Task', foreign_keys='Task.created_by', backref=db.backref('creator', lazy=True), lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

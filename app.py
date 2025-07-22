from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Project, Task, Attachment, Comment, TeamMember
from config import Config
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
##from flask_reuploaded import UploadSet, configure_uploads, IMAGES, DOCUMENTS
from flask_uploads import UploadSet, configure_uploads
from werkzeug.utils import secure_filename
from forms import LoginForm, RegistrationForm, ProjectForm, TaskForm, CommentForm, AttachmentForm, SearchForm
import os
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from export_utils import (
    export_tasks_to_csv,
    export_tasks_to_word,
    export_tasks_to_pdf,
    export_tasks_to_excel
)

# Initialization
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configure file uploads
attachments = UploadSet('attachments', extensions=('pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'))
configure_uploads(app, attachments)

# Create tables
with app.app_context():
    db.create_all()

# Login manager loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Auth routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

'''
@app.route('/')
def index():
    projects = Project.query.count()
    tasks = Task.query.count()
    team_members = TeamMember.query.count()
    return render_template('index.html', 
                         projects=projects, 
                         tasks=tasks, 
                         team_members=team_members)
'''

# Main routes
@app.route('/')
@login_required
def index():
    projects = Project.query.count()
    tasks = Task.query.count()
    team_members = User.query.count()
    
    # Get recent activities
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    recent_comments = Comment.query.order_by(Comment.timestamp.desc()).limit(5).all()
    
    # Generate progress chart
    projects_data = Project.query.all()
    project_names = [p.name for p in projects_data]
    project_progress = [p.progress for p in projects_data]
    
    plt.figure(figsize=(10, 5))
    plt.barh(project_names, project_progress)
    plt.title('Project Progress')
    plt.xlabel('Progress (%)')
    plt.tight_layout()
    
    # Save plot to a bytes buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    progress_chart = base64.b64encode(buf.read()).decode('ascii')
    plt.close()
    
    return render_template('index.html', 
                         projects=projects, 
                         tasks=tasks, 
                         team_members=team_members,
                         recent_tasks=recent_tasks,
                         recent_comments=recent_comments,
                         progress_chart=progress_chart)

'''
@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)
'''

# Project routes
@app.route('/projects')
@login_required
def projects():
    search_form = SearchForm()
    query = request.args.get('query')
    
    if query:
        projects = Project.query.filter(Project.name.ilike(f'%{query}%')).all()
    else:
        projects = Project.query.all()
    
    return render_template('projects.html', projects=projects, search_form=search_form)

'''
@app.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        end_date = request.form['end_date'] if request.form['end_date'] else None
        
        project = Project(name=name, description=description, end_date=end_date)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('projects'))
    return render_template('add_project.html')
'''

@app.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            project = Project(
                name=form.name.data,
                description=form.description.data,
                end_date=datetime.strptime(form.end_date.data, '%Y-%m-%d') if form.end_date.data else None,
                status=form.status.data,
                created_by=current_user.id
            )
            db.session.add(project)
            db.session.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('projects'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating project: {str(e)}', 'danger')
    return render_template('add_project.html', form=form)

@app.route('/projects/<int:id>')
@login_required
def project_detail(id):
    project = Project.query.get_or_404(id)
    return render_template('project_detail.html', project=project)

'''
@app.route('/tasks')
def tasks():
    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)
'''

# Task routes
@app.route('/tasks')
@login_required
def tasks():
    search_form = SearchForm()
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    query = request.args.get('query')
    
    tasks_query = Task.query
    
    if query:
        tasks_query = tasks_query.filter(Task.title.ilike(f'%{query}%'))
    
    if status_filter:
        tasks_query = tasks_query.filter_by(status=status_filter)
    
    if priority_filter:
        tasks_query = tasks_query.filter_by(priority=priority_filter)
    
    tasks = tasks_query.all()
    
    return render_template('tasks.html', tasks=tasks, search_form=search_form)

'''
@app.route('/tasks/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        project_id = request.form['project_id']
        assignee_id = request.form['assignee_id'] if request.form['assignee_id'] else None
        due_date = request.form['due_date'] if request.form['due_date'] else None
        
        task = Task(title=title, description=description, 
                   project_id=project_id, assignee_id=assignee_id,
                   due_date=due_date)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('tasks'))
    
    projects = Project.query.all()
    team_members = TeamMember.query.all()
    return render_template('add_task.html', projects=projects, team_members=team_members)
'''

@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    form.project_id.choices = [(p.id, p.name) for p in Project.query.all()]
    form.assignee_id.choices = [(u.id, u.username) for u in User.query.all()]
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            due_date=datetime.strptime(form.due_date.data, '%Y-%m-%d') if form.due_date.data else None,
            project_id=form.project_id.data,
            assignee_id=form.assignee_id.data if form.assignee_id.data else None,
            created_by=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!')
        return redirect(url_for('tasks'))
    return render_template('add_task.html', form=form)

@app.route('/tasks/<int:id>', methods=['GET', 'POST'])
@login_required
def task_detail(id):
    task = Task.query.get_or_404(id)
    comment_form = CommentForm()
    attachment_form = AttachmentForm()
    
    if comment_form.validate_on_submit():
        comment = Comment(
            content=comment_form.content.data,
            task_id=id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!')
        return redirect(url_for('task_detail', id=id))
    
    if attachment_form.validate_on_submit():
        filename = attachments.save(attachment_form.file.data)
        attachment = Attachment(
            filename=filename,
            path=attachments.path(filename),
            task_id=id,
            uploaded_by=current_user.id
        )
        db.session.add(attachment)
        db.session.commit()
        flash('Attachment uploaded!')
        return redirect(url_for('task_detail', id=id))
    
    return render_template('task_detail.html', 
                        task=task, 
                        comment_form=comment_form,
                        attachment_form=attachment_form)

@app.route('/tasks/update_status/<int:id>', methods=['POST'])
@login_required
def update_task_status(id):
    task = Task.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in ['To Do', 'In Progress', 'In Review', 'Completed']:
        task.status = new_status
        db.session.commit()
        
        # Update project progress
        if task.project:
            task.project.update_progress()
        
        flash('Task status updated!')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('task_detail', id=id))

@app.route('/tasks/export/csv')
@login_required
def export_tasks_csv():
    tasks = get_filtered_tasks()  # Reuse the same filtering logic
    csv_data = export_tasks_to_csv(tasks)
    
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=tasks_export.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/tasks/export/word')
@login_required
def export_tasks_word():
    tasks = get_filtered_tasks()
    word_file = export_tasks_to_word(tasks)
    
    response = make_response(word_file.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=tasks_export.docx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    return response

@app.route('/tasks/export/pdf')
@login_required
def export_tasks_pdf():
    tasks = get_filtered_tasks()
    pdf_file = export_tasks_to_pdf(tasks)
    
    response = make_response(pdf_file.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=tasks_export.pdf'
    response.headers['Content-type'] = 'application/pdf'
    return response

@app.route('/tasks/export/excel')
@login_required
def export_tasks_excel():
    tasks = get_filtered_tasks()
    excel_file = export_tasks_to_excel(tasks)
    
    response = make_response(excel_file.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=tasks_export.xlsx'
    response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def get_filtered_tasks():
    """Reuse the same filtering logic from the tasks route"""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    query = request.args.get('query')
    project_filter = request.args.get('project')
    
    tasks_query = Task.query.join(Project)
    
    if query:
        tasks_query = tasks_query.filter(Task.title.ilike(f'%{query}%'))
    
    if status_filter:
        tasks_query = tasks_query.filter_by(status=status_filter)
    
    if priority_filter:
        tasks_query = tasks_query.filter_by(priority=priority_filter)
    
    if project_filter:
        tasks_query = tasks_query.filter(Task.project_id == project_filter)
    
    return tasks_query.all()

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOADED_ATTACHMENTS_DEST'], filename)

'''
@app.route('/team')
def team():
    team_members = TeamMember.query.all()
    return render_template('team.html', team_members=team_members)
'''

# Team routes
@app.route('/team')
@login_required
def team():
    users = User.query.all()
    return render_template('team.html', users=users)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/team/add', methods=['GET', 'POST'])
def add_team_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        
        member = TeamMember(name=name, email=email, role=role)
        db.session.add(member)
        db.session.commit()
        return redirect(url_for('team'))
    return render_template('add_member.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5011)


from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import logging
from collections import defaultdict
from flask_login import LoginManager, UserMixin, login_required
import csv
from io import StringIO
from flask_caching import Cache

logging.basicConfig(filename='/var/log/gunicorn/learner_result.log', level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://thato:90059Jay#@127.0.0.1:3306/leaner_result'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

'''
login_manager = LoginManager(app)
login_manager.login_view = 'login'
'''
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Define the Results model
class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    date_taken = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Result {self.first_name} {self.last_name} - {self.subject}>'

# Route to display all results in HTML table

'''
@app.route('/results', methods=['GET'])
def show_results():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Adjust as needed
        results = Result.query.order_by(Result.date_taken.desc()).paginate(page=page, per_page=per_page)

        return render_template('results.html', results=results)
    except Exception as e:
        app.logger.error(f"Error fetching results: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
'''

@app.route('/results', methods=['GET'])
def show_results():
    subject_filter = request.args.get('subject')
    min_score = request.args.get('min_score', type=float)
    query = Result.query.order_by(Result.date_taken.desc())

    if subject_filter:
        query = query.filter(Result.subject == subject_filter)
    if min_score is not None:
        query = query.filter(Result.score >= min_score)

    #per_page = 10
    #results = query.paginate(page=range, per_page=per_page)
    return render_template('results.html', results=query)


# Route to get analytics data for Chart.js
@app.route('/analytics', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_analytics():
    try:
        # Get all results
        results = Result.query.all()
        
        # Prepare data for charts
        analytics_data = {
            # Average score per subject
            'subject_avg': defaultdict(list),
            # Score distribution
            'score_distribution': defaultdict(int),
            # Results over time
            'results_over_time': defaultdict(int)
        }
        
        # Calculate analytics
        for result in results:
            # For average score per subject
            analytics_data['subject_avg'][result.subject].append(result.score)
            
            # For score distribution (grouped in 10-point ranges)
            score_range = f"{int(result.score//10)*10}-{int(result.score//10)*10+10}"
            analytics_data['score_distribution'][score_range] += 1
            
            # For results over time (group by month)
            month_year = result.date_taken.strftime("%Y-%m")
            analytics_data['results_over_time'][month_year] += 1
        
        # Calculate average scores per subject
        subject_analytics = []
        for subject, scores in analytics_data['subject_avg'].items():
            subject_analytics.append({
                'subject': subject,
                'average_score': sum(scores) / len(scores),
                'count': len(scores)
            })
        
        # Convert score distribution to list
        score_distribution = [{'range': k, 'count': v} for k, v in sorted(analytics_data['score_distribution'].items())]
        
        # Convert results over time to list
        results_over_time = [{'date': k, 'count': v} for k, v in sorted(analytics_data['results_over_time'].items())]
        
        return jsonify({
            'success': True,
            'data': {
                'subject_analytics': subject_analytics,
                'score_distribution': score_distribution,
                'results_over_time': results_over_time
            }
        })
    except Exception as e:
        app.logger.error(f"Error generating analytics: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/save_result.php', methods=['POST'])
def save_result():
    data = request.get_json()   # Changed for better compatibility
    
    # Validate required fields
    required_fields = ['firstName', 'lastName', 'email', 'subject', 'score', 'dateTaken']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        # Parse the date string into a date object
        date_taken = datetime.strptime(data['dateTaken'], '%Y-%m-%d').date()
        
        # Validate e-mail format
        if '@' not in data['email'] or '.' not in data['email'].split('@')[-1]:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400

        # Validate score format
        if not (0 <= float(data['score']) <= 100):
            return jsonify({'success': False, 'message': 'Invalid score format must be between 0 and 100'}), 400

        # Create a new Result object
        new_result = Result(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            subject=data['subject'],
            score=float(data['score']),
            date_taken=date_taken
        )
        
        # Add to session and commit
        db.session.add(new_result)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Result saved successfully', 'id': new_result.id})
    
    except ValueError as e:
        return jsonify({'success': False, 'message': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving result: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/export_results.csv')
def export_results():
    results = Result.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Subject', 'Score', 'Date Taken'])
    for result in results:
        writer.writerow([
            result.id,
            f"{result.first_name} {result.last_name}",
            result.email,
            result.subject,
            result.score,
            result.date_taken
        ])
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=results.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5010, debug=True)

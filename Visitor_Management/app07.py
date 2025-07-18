from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
#from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from flask_cors import CORS
import logging
from flask_exceptions import BadRequest

# Place log config here:
logging.basicConfig(filename='/var/log/gunicorn/visitors.log', level=logging.DEBUG)

#load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configure SQLAlchemy for MariaDB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://thato:90059Jay#@127.0.0.1:3306/visitor_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Visitor model
class Visitor(db.Model):
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    purpose = db.Column(db.String(255), nullable=False)
    time_in = db.Column(db.DateTime, nullable=False)
    time_out = db.Column(db.DateTime)
    vehicleRegistrationNumber = db.Column(db.String(100), nullable=False)
    signature = db.Column(db.Text)  # For storing Base64 encoded signature

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
            'purpose': self.purpose,
            'timeIn': self.time_in.isoformat() if self.time_in else None,
            'timeOut': self.time_out.isoformat() if self.time_out else None,
            'vehicleRegistrationNumber': self.vehicleRegistrationNumber
        }
'''
# Create database here:
db.create_all()
'''

@app.route('/', methods=['GET', 'POST'])
def visitors():
    if request.method == 'POST':
        data = request.get_json()
        
        required_fields = ['name', 'purpose', 'timeIn', 'vehicleRegistrationNumber']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        try:
            time_in = datetime.fromisoformat(data['timeIn'])
            time_out = datetime.fromisoformat(data['timeOut']) if 'timeOut' in data and data['timeOut'] else None
            
            visitor = Visitor(
                name=data['name'],
                company=data.get('company'),
                phone=data.get('phone'),
                email=data.get('email'),
                purpose=data['purpose'],
                time_in=time_in,
                time_out=time_out,
                vehicleRegistrationNumber=data.get('vehicleRegistrationNumber')
            )
            
            db.session.add(visitor)
            db.session.commit()
            
            return jsonify({'message': 'Visitor added successfully', 'id': visitor.id}), 201
        
        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'GET':
        visitors = Visitor.query.order_by(Visitor.time_in.desc()).all()
        return jsonify([visitor.to_dict() for visitor in visitors])

@app.route('/api/visitors', methods=['GET', 'POST'])
def handle_visitor():
    if request.method == 'POST':
        return create_visitor()
    elif request.method == 'GET':
        return get_visitors()

def create_visitor():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No JSON data provided'}), 500
        #raise BadRequest('No JSON data provided')

    required_fields = ['name', 'purpose', 'vehicleRegistrationNumber']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 500
        #raise BadRequest('Missing required fields!')

    try:
        time_in = datetime.fromisoformat(data.get('time_in')) if 'time_in' in data else datetime.utcnow()
        time_out = datetime.fromisoformat(data['time_out']) if 'time_out' in data and data['time_out'] else None

        visitor = Visitor(
                    name=data['name'],
                    company=data.get('company'),
                    phone=data.get('phone'),
                    email=data.get('email'),
                    purpose=data['purpose'],
                    time_in=time_in,
                    time_out=time_out,
                    vehicleRegistrationNumber=data.get('vehicleRegistrationNumber', ''),
                    signature = data.get('signature')
        )
        
        db.session.add(visitor)
        db.session.commit()

        return jsonify({
                'message': 'Visitor added successfully',
                'visitor': visitor.to_dict()
            }), 201

    except ValueError as e:
        raise BadRequest(f'Invalide date format: {str(e)}')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_visitors():
#    visitors = Visitor.query.order_by(Visitor.time_in.desc()).all()
    visitors = Visitor.query.options(db.defer(Visitor.signature)).order_by(Visitor.time_in.desc()).all()
    return jsonify([visitor.to_dict() for visitor in visitors])

def signVisitorOut():
    visitors = Visitor.query.options(db.defer(Visitor.signature)).order_by(Visitor.time_in.desc()).all()
    return jsonify([visitor.to_dict() for visitor in visitors])

@app.route('/api/visitors/vehicle/{registration}')
def signOutVisitor():
    if request.method == 'GET':
        signVisitorOut()

'''
@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    print('Initialized the database.')
'''

# Add these new routes to your Flask app

@app.route('/api/visitors/metrics', methods=['GET'])
def get_visitor_metrics():
    """Get various visitor metrics for the dashboard"""
    
    # Total visitors count
    total_visitors = Visitor.query.count()
    
    # Visitors today
    today = datetime.utcnow().date()
    visitors_today = Visitor.query.filter(
        db.func.date(Visitor.time_in) == today
    ).count()
    
    # Currently signed in visitors (no time_out)
    current_visitors = Visitor.query.filter(
        Visitor.time_out.is_(None)
    ).count()
    
    # New visitors (first time visitors)
    # This assumes "new" means unique by name/email - adjust as needed
    unique_visitors = db.session.query(
        db.func.count(db.func.distinct(Visitor.email))
    ).scalar()
    
    # Visit frequency (group by visitor)
    visit_frequency = db.session.query(
        Visitor.name,
        Visitor.email,
        db.func.count().label('visit_count')
    ).group_by(
        Visitor.name,
        Visitor.email
    ).order_by(
        db.func.count().desc()
    ).limit(10).all()
    
    # Purpose breakdown
    purpose_counts = db.session.query(
        Visitor.purpose,
        db.func.count().label('count')
    ).group_by(
        Visitor.purpose
    ).all()
    
    # Time-based metrics (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_visits = db.session.query(
        db.func.date(Visitor.time_in).label('date'),
        db.func.count().label('count')
    ).filter(
        Visitor.time_in >= thirty_days_ago
    ).group_by(
        db.func.date(Visitor.time_in)
    ).order_by(
        db.func.date(Visitor.time_in)
    ).all()
    
    return jsonify({
        'total_visitors': total_visitors,
        'visitors_today': visitors_today,
        'current_visitors': current_visitors,
        'unique_visitors': unique_visitors,
        'visit_frequency': [{
            'name': v.name,
            'email': v.email,
            'visit_count': v.visit_count
        } for v in visit_frequency],
        'purpose_breakdown': [{
            'purpose': p.purpose,
            'count': p.count
        } for p in purpose_counts],
        'daily_visits': [{
            'date': d.date.isoformat(),
            'count': d.count
        } for d in daily_visits]
    })

@app.route('/api/visitors/new', methods=['GET'])
def get_new_visitors():
    """Get new visitors (first-time visitors)"""
    
    # Get visitors who have only visited once
    new_visitors = db.session.query(
        Visitor.name,
        Visitor.email,
        Visitor.company,
        Visitor.phone,
        db.func.count().label('visit_count')
    ).group_by(
        Visitor.name,
        Visitor.email,
        Visitor.company,
        Visitor.phone
    ).having(
        db.func.count() == 1
    ).order_by(
        Visitor.time_in.desc()
    ).limit(50).all()
    
    return jsonify([{
        'name': v.name,
        'email': v.email,
        'company': v.company,
        'phone': v.phone,
        'first_visit': v.time_in.isoformat() if v.time_in else None
    } for v in new_visitors])

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5050, debug=True)

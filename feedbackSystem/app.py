from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Feedback
import datetime
import random  # for demo sentiment analysis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = process_message(user_message)
    return jsonify({'response': response})

def process_message(message):
    # Simple chatbot logic
    message = message.lower()
    
    if any(word in message for word in ['hi', 'hello', 'hey']):
        return "Hello! I'm your feedback assistant. How can I help you today?"
    
    elif 'feedback' in message or 'comment' in message or 'suggestion' in message:
        return "I'd be happy to take your feedback. Please share your thoughts with me."
    
    elif 'thank' in message:
        return "You're welcome! Is there anything else I can help you with?"
    
    elif 'bye' in message or 'goodbye' in message:
        return "Goodbye! Thanks for your feedback. Have a great day!"
    
    else:
        # Save the message as feedback if it's not a greeting
        feedback = Feedback(
            message=message,
            timestamp=datetime.datetime.now()
        )
        db.session.add(feedback)
        db.session.commit()
        return "Thank you for your feedback! Is there anything else you'd like to share?"

@app.route('/dashboard')
def dashboard():
    # Get all feedback, ordered by newest first
    feedback_list = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('dashboard.html', feedback_list=feedback_list)

@app.route('/mark_resolved/<int:feedback_id>')
def mark_resolved(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.resolved = not feedback.resolved  # Toggle resolved status
    db.session.commit()
    return redirect(url_for('dashboard'))

# ... (keep your existing routes)

def process_message(message):
    # Enhanced to include sentiment analysis (simple demo version)
    message = message.lower()
    
    if any(word in message for word in ['hi', 'hello', 'hey']):
        return "Hello! I'm your feedback assistant. How can I help you today?"
    
    elif 'feedback' in message or 'comment' in message or 'suggestion' in message:
        return "I'd be happy to take your feedback. Please share your thoughts with me."
    
    elif 'thank' in message:
        return "You're welcome! Is there anything else I can help you with?"
    
    elif 'bye' in message or 'goodbye' in message:
        return "Goodbye! Thanks for your feedback. Have a great day!"
    
    else:
        # Simple sentiment analysis (in a real app, use a proper NLP library)
        positive_words = ['good', 'great', 'awesome', 'love', 'happy', 'excellent']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'poor', 'disappointed']
        
        sentiment = 'neutral'
        if any(word in message for word in positive_words):
            sentiment = 'positive'
        elif any(word in message for word in negative_words):
            sentiment = 'negative'
        
        # Simple category detection
        category = 'general'
        if '?' in message:
            category = 'question'
        elif 'suggest' in message or 'idea' in message:
            category = 'suggestion'
        elif 'problem' in message or 'issue' in message or 'not working' in message:
            category = 'complaint'
        
        # Save the feedback with sentiment and category
        feedback = Feedback(
            message=message,
            sentiment=sentiment,
            category=category
        )
        db.session.add(feedback)
        db.session.commit()
        
        return "Thank you for your feedback! Is there anything else you'd like to share?"
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5020)


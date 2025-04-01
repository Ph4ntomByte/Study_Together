from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user
from app.models.study_plan import StudyPlan
from app.models.feedback import Feedback
from app import db
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the homepage."""
    # Get recent public study plans
    recent_plans = StudyPlan.query.filter_by(is_public=True).order_by(StudyPlan.created_at.desc()).limit(6).all()
    return render_template('index.html', title='Study Together', recent_plans=recent_plans)

@main_bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html', title='About Study Together')

@main_bp.route('/api/user')
def get_current_user():
    """Get the current user's info as JSON."""
    if current_user.is_authenticated:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'name': current_user.name
        })
    return jsonify({'authenticated': False})

@main_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback form submissions."""
    data = request.get_json()
    
    # Extract form data
    name = data.get('name', '')
    email = data.get('email', '')
    subject = data.get('subject', '')
    message = data.get('message', '')
    
    try:
        # Create new feedback entry
        feedback = Feedback(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        # Save to database
        db.session.add(feedback)
        db.session.commit()
        
        # Log the feedback
        logging.info(f"Feedback saved from {name} ({email}): {subject}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback! We appreciate your input.'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while saving your feedback. Please try again.'
        }), 500 
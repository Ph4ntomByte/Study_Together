from flask import Blueprint, render_template, jsonify
from flask_login import current_user
from app.models.study_plan import StudyPlan

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
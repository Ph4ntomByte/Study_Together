from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.feedback import Feedback
from app.models.user import User
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Admin decorator to restrict access to administrators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        # Simple admin check - in a real app, you'd have an admin field in the User model
        # For now, let's consider the first registered user (ID 1) as admin
        if current_user.id != 1:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard home."""
    feedback_count = Feedback.query.count()
    user_count = User.query.count()
    
    return render_template(
        'admin/dashboard.html', 
        title='Admin Dashboard',
        feedback_count=feedback_count,
        user_count=user_count
    )

@admin_bp.route('/feedback')
@admin_required
def list_feedback():
    """List all feedback submissions."""
    feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template(
        'admin/feedback.html', 
        title='Feedback Submissions',
        feedback=feedback
    )

@admin_bp.route('/feedback/<int:feedback_id>')
@admin_required
def view_feedback(feedback_id):
    """View a specific feedback submission."""
    feedback = Feedback.query.get_or_404(feedback_id)
    return render_template(
        'admin/feedback_detail.html',
        title='Feedback Detail',
        feedback=feedback
    )

@admin_bp.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@admin_required
def delete_feedback(feedback_id):
    """Delete a feedback submission."""
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted successfully.', 'success')
    return redirect(url_for('admin.list_feedback')) 
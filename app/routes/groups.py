from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.group import (
    StudyGroup, GroupMember, GroupMessage, 
    LocationChangeRequest, LocationChangeVote, JoinRequest
)
from app.models.study_plan import StudyPlan

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/', methods=['GET'])
@login_required
def list_groups():
    """List all groups the user is a member of."""
    memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    groups = [membership.group for membership in memberships]
    return render_template('groups/list.html', groups=groups, title='My Study Groups')

@groups_bp.route('/api/groups', methods=['GET'])
@login_required
def api_list_groups():
    """API endpoint to get all groups the user is a member of."""
    memberships = GroupMember.query.filter_by(user_id=current_user.id).all()
    groups = [membership.group for membership in memberships]
    return jsonify([group.to_dict() for group in groups])

@groups_bp.route('/<int:group_id>', methods=['GET'])
@login_required
def view_group(group_id):
    """View a study group."""
    group = StudyGroup.query.get_or_404(group_id)
    
    # Check if the user is a member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()
    
    if not membership:
        abort(403)
    
    members = GroupMember.query.filter_by(group_id=group_id).all()
    messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp).all()
    study_plans = StudyPlan.query.filter_by(group_id=group_id).all()
    
    return render_template(
        'groups/view.html',
        group=group,
        members=members,
        messages=messages,
        study_plans=study_plans,
        is_admin=membership.is_admin,
        title=f'Group: {group.name}'
    )

@groups_bp.route('/api/groups/<int:group_id>', methods=['GET'])
@login_required
def api_view_group(group_id):
    """API endpoint to get a study group."""
    group = StudyGroup.query.get_or_404(group_id)
    
    # Check if the user is a member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()
    
    # Get all study plans for this group
    study_plans = StudyPlan.query.filter_by(group_id=group_id).all()
    study_plans_data = [plan.to_dict() for plan in study_plans]
    
    # If not a group member, check if they have a pending join request
    if not membership:
        # Check if user has any pending join requests to any study plans in this group
        study_plan_ids = [plan.id for plan in study_plans]
        
        if not study_plan_ids:
            return jsonify({'error': 'You are not a member of this group'}), 403
            
        pending_request = JoinRequest.query.filter(
            JoinRequest.user_id == current_user.id,
            JoinRequest.study_plan_id.in_(study_plan_ids)
        ).first()
        
        if pending_request:
            # Provide limited information for users with pending requests
            return jsonify({
                'group': group.to_dict(),
                'study_plans': study_plans_data,
                'pending_request': True,
                'members': [],
                'messages': [],
                'is_admin': False
            })
        else:
            return jsonify({'error': 'You are not a member of this group'}), 403
    
    # For actual members, provide full information
    members = GroupMember.query.filter_by(group_id=group_id).all()
    members_data = [{
        'id': member.id,
        'user_id': member.user_id,
        'username': member.user.username,
        'name': member.user.name,
        'is_admin': member.is_admin,
        'joined_at': member.joined_at.isoformat()
    } for member in members]
    
    messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp).all()
    messages_data = [message.to_dict() for message in messages]
    
    return jsonify({
        'group': group.to_dict(),
        'members': members_data,
        'messages': messages_data,
        'study_plans': study_plans_data,
        'is_admin': membership.is_admin,
        'pending_request': False
    })

@groups_bp.route('/<int:group_id>/messages', methods=['POST'])
@login_required
def add_message(group_id):
    """Add a message to the group chat."""
    group = StudyGroup.query.get_or_404(group_id)
    
    # Check if the user is a member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()
    
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Message content cannot be empty'}), 400
    
    message = GroupMessage(
        content=content,
        group_id=group_id,
        user_id=current_user.id
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict())

@groups_bp.route('/<int:group_id>/messages', methods=['GET'])
@login_required
def get_messages(group_id):
    """Get all messages for a group."""
    group = StudyGroup.query.get_or_404(group_id)
    
    # Check if the user is a member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()
    
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.timestamp).all()
    return jsonify([message.to_dict() for message in messages])

@groups_bp.route('/<int:group_id>/location-change', methods=['POST'])
@login_required
def request_location_change(group_id):
    """Request a change of meeting location."""
    group = StudyGroup.query.get_or_404(group_id)
    
    # Check if the user is a member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()
    
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    data = request.get_json()
    study_plan_id = data.get('study_plan_id')
    
    # Verify the study plan belongs to this group
    study_plan = StudyPlan.query.get_or_404(study_plan_id)
    if study_plan.group_id != group_id:
        return jsonify({'error': 'This study plan does not belong to this group'}), 400
    
    # Check if there's already an active location change request for this plan
    existing_request = LocationChangeRequest.query.filter_by(
        study_plan_id=study_plan_id,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': 'There is already a pending location change request for this plan'}), 400
    
    # Create new location change request
    location_request = LocationChangeRequest(
        proposed_location=data.get('proposed_location'),
        reason=data.get('reason', ''),
        requester_id=current_user.id,
        study_plan_id=study_plan_id,
        group_id=group_id
    )
    
    db.session.add(location_request)
    
    # The requester automatically votes yes
    vote = LocationChangeVote(
        vote=True,
        request_id=location_request.id,
        voter_id=current_user.id
    )
    
    db.session.add(vote)
    db.session.commit()
    
    # Update the location_request.id after commit
    return jsonify({
        'success': True,
        'request_id': location_request.id
    })

@groups_bp.route('/location-change/<int:request_id>/vote', methods=['POST'])
@login_required
def vote_location_change(request_id):
    """Vote on a location change request."""
    location_request = LocationChangeRequest.query.get_or_404(request_id)
    
    # Check if the request is still pending
    if location_request.status != 'pending':
        return jsonify({'error': 'This request has already been processed'}), 400
    
    # Check if the user is a member of the group
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=location_request.group_id
    ).first()
    
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Check if the user has already voted
    existing_vote = LocationChangeVote.query.filter_by(
        request_id=request_id,
        voter_id=current_user.id
    ).first()
    
    data = request.get_json()
    vote_value = data.get('vote', True)
    
    if existing_vote:
        # Update existing vote
        existing_vote.vote = vote_value
    else:
        # Create new vote
        vote = LocationChangeVote(
            vote=vote_value,
            request_id=request_id,
            voter_id=current_user.id
        )
        db.session.add(vote)
    
    db.session.commit()
    
    # Check if majority has voted to approve
    total_members = GroupMember.query.filter_by(group_id=location_request.group_id).count()
    yes_votes = LocationChangeVote.query.filter_by(request_id=request_id, vote=True).count()
    
    # More than 50% of members voted yes
    if yes_votes > total_members / 2:
        location_request.status = 'approved'
        
        # Update the study plan location
        study_plan = StudyPlan.query.get(location_request.study_plan_id)
        study_plan.location = location_request.proposed_location
        
        db.session.commit()
    
    return jsonify({'success': True})

@groups_bp.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    """Leave a study group."""
    group = StudyGroup.query.get_or_404(group_id)
    
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()
    
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 400
    
    # Check if this is the last admin
    if membership.is_admin:
        admin_count = GroupMember.query.filter_by(
            group_id=group_id,
            is_admin=True
        ).count()
        
        if admin_count == 1:
            # Find another member to promote to admin
            another_member = GroupMember.query.filter_by(
                group_id=group_id,
                is_admin=False
            ).first()
            
            if another_member:
                another_member.is_admin = True
            else:
                # This was the last member, delete the group
                db.session.delete(group)
                db.session.commit()
                return jsonify({'success': True})
    
    # Remove the membership
    db.session.delete(membership)
    db.session.commit()
    
    return jsonify({'success': True}) 
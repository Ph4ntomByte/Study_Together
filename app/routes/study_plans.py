from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.study_plan import StudyPlan, TimeChangeRequest
from app.models.group import JoinRequest, StudyGroup, GroupMember, LocationChangeRequest
from datetime import datetime

study_plans_bp = Blueprint('study_plans', __name__)

@study_plans_bp.route('/', methods=['GET'])
def list_plans():
    """List all public study plans."""
    public_plans = StudyPlan.query.filter_by(is_public=True).all()
    return render_template('study_plans/list.html', plans=public_plans, title='Study Plans')

@study_plans_bp.route('/api/plans', methods=['GET'])
def api_list_plans():
    """API endpoint to get public study plans."""
    public_plans = StudyPlan.query.filter_by(is_public=True).all()
    return jsonify([plan.to_dict() for plan in public_plans])

@study_plans_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    """Create a new study plan."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(data.get('start_time'))
            end_time = datetime.fromisoformat(data.get('end_time'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        if start_time >= end_time:
            return jsonify({'error': 'End time must be after start time'}), 400
        
        plan = StudyPlan(
            title=data.get('title'),
            subject=data.get('subject'),
            description=data.get('description'),
            location=data.get('location'),
            start_time=start_time,
            end_time=end_time,
            is_public=data.get('is_public', True),
            max_participants=data.get('max_participants', 10),
            creator_id=current_user.id
        )
        
        # Generate a share link for private plans
        if not plan.is_public:
            plan.generate_share_link()
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({'success': True, 'id': plan.id, 'share_link': plan.share_link})
    
    return render_template('study_plans/create.html', title='Create Study Plan')

@study_plans_bp.route('/<int:plan_id>', methods=['GET'])
def view_plan(plan_id):
    """View a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # If the plan is not public, check if the user has access
    if not plan.is_public:
        share_token = request.args.get('token')
        if not share_token or share_token != plan.share_link:
            if not current_user.is_authenticated or current_user.id != plan.creator_id:
                abort(403)
    
    return render_template('study_plans/view.html', plan=plan, title=plan.title)

@study_plans_bp.route('/api/plans/<int:plan_id>', methods=['GET'])
def api_view_plan(plan_id):
    """API endpoint to get a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # If the plan is not public, check if the user has access
    if not plan.is_public:
        share_token = request.args.get('token')
        if not share_token or share_token != plan.share_link:
            if not current_user.is_authenticated or current_user.id != plan.creator_id:
                return jsonify({'error': 'Unauthorized access to private study plan'}), 403
    
    return jsonify(plan.to_dict())

@study_plans_bp.route('/<int:plan_id>/edit', methods=['GET', 'PUT'])
@login_required
def edit_plan(plan_id):
    """Edit a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Only the creator can edit the plan
    if current_user.id != plan.creator_id:
        abort(403)
    
    if request.method == 'PUT':
        data = request.get_json()
        
        # Parse datetime strings if provided
        if 'start_time' in data and 'end_time' in data:
            try:
                start_time = datetime.fromisoformat(data.get('start_time'))
                end_time = datetime.fromisoformat(data.get('end_time'))
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
            
            if start_time >= end_time:
                return jsonify({'error': 'End time must be after start time'}), 400
            
            plan.start_time = start_time
            plan.end_time = end_time
        
        # Update fields if provided
        if 'title' in data:
            plan.title = data.get('title')
        if 'subject' in data:
            plan.subject = data.get('subject')
        if 'description' in data:
            plan.description = data.get('description')
        if 'location' in data:
            plan.location = data.get('location')
        if 'is_public' in data:
            plan.is_public = data.get('is_public')
            # Generate a share link for private plans if it doesn't have one
            if not plan.is_public and not plan.share_link:
                plan.generate_share_link()
        if 'max_participants' in data:
            plan.max_participants = data.get('max_participants')
        
        db.session.commit()
        return jsonify({'success': True})
    
    return render_template('study_plans/edit.html', plan=plan, title=f'Edit {plan.title}')

@study_plans_bp.route('/<int:plan_id>/delete', methods=['DELETE'])
@login_required
def delete_plan(plan_id):
    """Delete a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Only the creator can delete the plan
    if current_user.id != plan.creator_id:
        return jsonify({'error': 'Only the creator can delete a study plan'}), 403
    
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({'success': True})

@study_plans_bp.route('/<int:plan_id>/join', methods=['POST'])
@login_required
def request_to_join(plan_id):
    """Request to join a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Check if the user is already the creator
    if current_user.id == plan.creator_id:
        return jsonify({'error': 'You are already the creator of this study plan'}), 400
    
    # Check if the user already has a pending or approved join request
    existing_request = JoinRequest.query.filter_by(
        user_id=current_user.id,
        study_plan_id=plan_id
    ).first()
    
    if existing_request:
        if existing_request.status == 'pending':
            return jsonify({'error': 'You already have a pending request for this study plan'}), 400
        elif existing_request.status == 'approved':
            return jsonify({'error': 'You have already been approved to join this study plan'}), 400
    
    # Check if the plan already has a group and if the user is already a member
    if plan.group_id:
        is_member = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=plan.group_id
        ).first()
        
        if is_member:
            return jsonify({'error': 'You are already a member of this study group'}), 400
    
    data = request.get_json()
    
    # Create a new join request
    join_request = JoinRequest(
        message=data.get('message', ''),
        user_id=current_user.id,
        study_plan_id=plan_id
    )
    
    db.session.add(join_request)
    db.session.commit()
    
    return jsonify({'success': True, 'request_id': join_request.id})

@study_plans_bp.route('/requests/<int:request_id>/<string:action>', methods=['POST'])
@login_required
def handle_join_request(request_id, action):
    """Approve or reject a join request."""
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid action'}), 400
    
    join_request = JoinRequest.query.get_or_404(request_id)
    plan = join_request.study_plan
    
    # Only the creator can approve/reject requests
    if current_user.id != plan.creator_id:
        return jsonify({'error': 'Only the creator can manage join requests'}), 403
    
    if join_request.status != 'pending':
        return jsonify({'error': 'This request has already been processed'}), 400
    
    if action == 'approve':
        join_request.status = 'approved'
        
        # Create or get the study group
        if not plan.group_id:
            # Create a new group
            group = StudyGroup(name=f"Group for {plan.title}")
            db.session.add(group)
            db.session.flush()  # Get the ID without committing
            
            # Add the creator as admin
            creator_member = GroupMember(
                user_id=plan.creator_id,
                group_id=group.id,
                is_admin=True
            )
            db.session.add(creator_member)
            
            # Update the plan with the group ID
            plan.group_id = group.id
        
        # Add the requesting user to the group
        member = GroupMember(
            user_id=join_request.user_id,
            group_id=plan.group_id,
            is_admin=False
        )
        db.session.add(member)
    
    else:  # reject
        join_request.status = 'rejected'
    
    db.session.commit()
    
    return jsonify({'success': True})

@study_plans_bp.route('/api/study-plans/<int:plan_id>/join-requests', methods=['GET'])
@login_required
def get_join_requests(plan_id):
    """API endpoint to get join requests for a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Only the creator can view join requests
    if current_user.id != plan.creator_id:
        return jsonify({'error': 'Only the creator can view join requests'}), 403
    
    join_requests = JoinRequest.query.filter_by(study_plan_id=plan_id).all()
    
    # Convert to dict and include user info
    result = []
    for request in join_requests:
        request_dict = {
            'id': request.id,
            'message': request.message,
            'status': request.status,
            'created_at': request.created_at.isoformat(),
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'name': request.user.name
            }
        }
        result.append(request_dict)
    
    return jsonify(result)

@study_plans_bp.route('/<int:plan_id>/remove-participant', methods=['POST'])
@login_required
def remove_participant(plan_id):
    """Remove a participant from a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Only the creator can remove participants
    if current_user.id != plan.creator_id:
        return jsonify({'error': 'Only the creator can remove participants'}), 403
    
    # Check if study plan has a group
    if not plan.group_id:
        return jsonify({'error': 'This study plan does not have a group yet'}), 400
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # Can't remove the creator
    if int(user_id) == plan.creator_id:
        return jsonify({'error': 'Cannot remove the creator of the study plan'}), 400
    
    # Find the group member
    member = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=plan.group_id
    ).first()
    
    if not member:
        return jsonify({'error': 'User is not a member of this study plan'}), 404
    
    # Delete the member
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({'success': True})

@study_plans_bp.route('/<int:plan_id>/request-time-change', methods=['POST'])
@login_required
def request_time_change(plan_id):
    """Request a change of study plan time."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Check if the user is a member of the group
    if not plan.group_id:
        return jsonify({'error': 'This study plan does not have a group yet'}), 400
        
    membership = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=plan.group_id
    ).first()
    
    if not membership:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    # Check if there's already an active time change request for this plan
    existing_request = TimeChangeRequest.query.filter_by(
        study_plan_id=plan_id,
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': 'There is already a pending time change request for this plan'}), 400
    
    data = request.get_json()
    
    # Parse datetime strings
    try:
        proposed_start_time = datetime.fromisoformat(data.get('proposed_start_time'))
        proposed_end_time = datetime.fromisoformat(data.get('proposed_end_time'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400
    
    if proposed_start_time >= proposed_end_time:
        return jsonify({'error': 'End time must be after start time'}), 400
    
    # Create new time change request
    time_request = TimeChangeRequest(
        proposed_start_time=proposed_start_time,
        proposed_end_time=proposed_end_time,
        reason=data.get('reason', ''),
        requester_id=current_user.id,
        study_plan_id=plan_id
    )
    
    db.session.add(time_request)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'request_id': time_request.id
    })

@study_plans_bp.route('/<int:plan_id>/change-requests', methods=['GET'])
@login_required
def get_change_requests(plan_id):
    """Get all change requests for a study plan."""
    plan = StudyPlan.query.get_or_404(plan_id)
    
    # Check if the user is a member of the group
    if plan.group_id:
        membership = GroupMember.query.filter_by(
            user_id=current_user.id,
            group_id=plan.group_id
        ).first()
        
        if not membership and current_user.id != plan.creator_id:
            return jsonify({'error': 'You are not authorized to view change requests'}), 403
    elif current_user.id != plan.creator_id:
        return jsonify({'error': 'You are not authorized to view change requests'}), 403
    
    # Get time change requests
    time_requests = TimeChangeRequest.query.filter_by(
        study_plan_id=plan_id
    ).all()
    
    time_requests_data = [request.to_dict() for request in time_requests]
    
    # Get location change requests if group exists
    location_requests_data = []
    if plan.group_id:
        location_requests = LocationChangeRequest.query.filter_by(
            study_plan_id=plan_id
        ).all()
        
        for request in location_requests:
            request_data = {
                'id': request.id,
                'proposed_location': request.proposed_location,
                'reason': request.reason,
                'status': request.status,
                'created_at': request.created_at.isoformat(),
                'requester_id': request.requester_id,
                'study_plan_id': request.study_plan_id,
                'type': 'location',
                'requester': {
                    'id': request.requester.id,
                    'username': request.requester.username,
                    'name': request.requester.name
                }
            }
            location_requests_data.append(request_data)
    
    # Combine both types of requests
    all_requests = time_requests_data + location_requests_data
    
    # Sort by created_at (newest first)
    all_requests.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify(all_requests)

@study_plans_bp.route('/time-change/<int:request_id>/<string:action>', methods=['POST'])
@login_required
def handle_time_change(request_id, action):
    """Approve or reject a time change request."""
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid action'}), 400
    
    time_request = TimeChangeRequest.query.get_or_404(request_id)
    plan = time_request.study_plan
    
    # Only the creator can approve/reject time change requests
    if current_user.id != plan.creator_id:
        return jsonify({'error': 'Only the creator can manage time change requests'}), 403
    
    if time_request.status != 'pending':
        return jsonify({'error': 'This request has already been processed'}), 400
    
    if action == 'approve':
        time_request.status = 'approved'
        
        # Update the study plan times
        plan.start_time = time_request.proposed_start_time
        plan.end_time = time_request.proposed_end_time
    else:  # reject
        time_request.status = 'rejected'
    
    db.session.commit()
    
    return jsonify({'success': True}) 
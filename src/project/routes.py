from flask import Blueprint, request, jsonify 
import bcrypt, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from project.models import Project
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
projects = Blueprint('projects', __name__)


@projects.route('/user/<int:user_id>', methods=['POST'])
@jwt_required()
def create_project(user_id):
    data = request.json
    if not user_id:
        return jsonify({
            "success": False,
            "message": "user_id is required"
        }), 400
    user_auth_id = get_jwt_identity()
    if not user_auth_id == user_id:
        return jsonify({
            "success": False,
            "message": "Users can only create projects for themselves."
        }), 403
    if len(data) > 2:
        return jsonify({
            "success": False,
            "message": "Only needs title and image_url"
        }), 400
    new_project = Project.create(
        title=data["title"],
        user_id=user_id,
        image_url=data.get("image_url")
    )
    response_body = {}
    
    if not isinstance(new_project, Project) and type(new_project) == dict:
        response_body = new_project
        return jsonify({
            "message" : response_body["error"]
        }), response_body["status"]
    
    new_project_saved = new_project.save_and_commit()
    response_body = new_project.serialize()
    return jsonify(response_body), 201

@projects.route('/token', methods=['POST'])
def login():
    body = request.json
    if body.get('email') is None or body.get('password') is None:
        return jsonify({
            'message': 'Missing credentials. Password and email are required'
        }), 400
    user = User.query.filter_by(email=body['email']).one_or_none()
    if user is None:
        return jsonify({
            'message': 'Invalid credentials'
        }), 400
    
    #Check if user is valid
    password_is_valid = check_password_hash(user.hash_password, user.salt + body['password'])
    if not password_is_valid:
        return jsonify({
            'message': 'Invalid credentials'
        }), 400
    authorization = {
        'token': create_access_token(identity=user.id),
        'refresh': create_refresh_token(identity= user.id) 
    }
    return jsonify({
        'message': 'Logged in',
        'authorizathion': authorization
    }), 200
from flask import Blueprint, request, jsonify 
import bcrypt, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from user.models import User
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
users = Blueprint('users', __name__)


@users.route('', methods=['POST'])
def create_user():
    data = request.json
    if not "email" in data or not "password" in data:
        return jsonify({
            "success": False,
            "message": "email and password required"
        }), 400
    if len(data) > 3:
        return jsonify({
            "success": False,
            "message": "Only needs name, email and password"
        }), 400
    new_user = User.create(
        email=data["email"], 
        password=data["password"],
        name=data["name"]
    )
    response_body = {}
    
    if not isinstance(new_user, User) and type(new_user) == dict:
        response_body = new_user
        return jsonify({
            "message" : response_body["error"]
        }), response_body["status"]
    
    new_user_saved = new_user.save_and_commit()
    response_body = new_user.serialize()
    return jsonify(response_body), 201

@users.route('/token', methods=['POST'])
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


@users.route('/', methods=['GET'])
@jwt_required()
def get_user_data():
    """Get authenticated user with token """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    print(user.serialize())
    return jsonify(user.serialize()), 200
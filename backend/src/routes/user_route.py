import json
from math import ceil

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required , get_jwt_identity , get_jwt

from src.models.user import UserProfile
from concurrent.futures import ThreadPoolExecutor

email_thread_pool = ThreadPoolExecutor(max_workers=10)

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register_user():
	data = request.get_json()
	try:
		if data :
			user=UserProfile.register_user(data)
			print(user)
			return jsonify(
            {"message": "User registered", "username": user.username}
        ), 201
	except Exception as e:
		return jsonify({"error": str(e)}), 400

@user_bp.route("/login", methods=["POST"])
def login():
	data = request.get_json()
	if not data or "username" not in data or "password" not in data:
		return jsonify({"error": "Username and password are required"}), 400

	user = UserProfile.query.filter_by(username=data["username"]).first()
	if not user or not user.check_password(data["password"]):
		return jsonify({"error": "Invalid username or password"}), 401

	# access_token = create_access_token(identity=str(user.id))
	access_token = create_access_token(
    identity=str(user.id),  # Use a string for the `identity` (sub claim)
    additional_claims={"role": user.role.name}  # Add `role` as a custom claim
)

	print(access_token)
    # Generate refresh token
    # refresh_token = create_refresh_token(identity={"username": user.username})
	return jsonify({"access_token": access_token}), 200

@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    jwt_user_id = int(get_jwt_identity())  # Extract the `identity` (sub claim)
    jwt_role = get_jwt()["role"]  # Extract the custom claim `role`
    print(user_id)
    print(jwt_role)
    print(jwt_user_id)
    # Authorization logic
    if user_id != jwt_user_id:
        return jsonify({"error": "Unauthorized to delete this user"}), 403	
    
    user=UserProfile.delete_user(user_id=user_id)
    print(user)
    if user:
        return jsonify({"message":"User deleted sucessfully"})
    return jsonify({"error":"NO user found"}),404

@user_bp.route("/<int:user_id>",methods = ["GET"])	
def get_user(user_id):
	user = UserProfile.get_user(id=user_id)
	if user:
		return jsonify({
			"id":user.id,
			"username":user.username,
            "email":user.email,
			"created_at":user.created_at,
			"role":user.role.value
		})
	return jsonify({"error": "User not found"}), 404	

@user_bp.route("/",methods=["GET"])
def list_users():
	page = request.args.get("page", 1, type=int)
	per_page = request.args.get("per_page", 5, type=int)
	query = UserProfile.query
	total_users = query.count()
	users = (
		query.offset((page - 1) * per_page).limit(per_page).all()
	) 
	paginated_response = {
			"data": [
				{
					"username": user.username,
					"email": user.email,
					"created_at": user.created_at,
					"role":user.role.value
				}
				for user in users
			],
			"pagination": {
				"current_page": page,
				"per_page": per_page,
				"total_pages": ceil(total_users / per_page),
				"total_users": total_users,
			},
		}
	return jsonify(paginated_response), 200

# UPdate user 

## no need of get or list user - only for Application level purpose - make it private
# user_profile - vendor or customer dashboard
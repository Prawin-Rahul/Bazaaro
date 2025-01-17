from flask import Blueprint, jsonify, request
import json
from math import ceil
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required , get_jwt_identity , get_jwt

from src.models.product import Product 


product_bp = Blueprint("posts", __name__)
  
# @product_bp.route("/", methods=["GET", "POST"])  
# def user_operation():
#     if request.method == "POST":
#         return create_product()
   
@product_bp.route("/", methods=["POST"])  
@jwt_required()
def create_product():
    jwt_user_id = int(get_jwt_identity())  
    jwt_role = get_jwt()["role"] 
    data = request.get_json()

    try:
        if jwt_role != "VENDOR":
            return jsonify({"error": "Unauthorized to delete this user"}), 403	
        Product.create_product(id=jwt_user_id, data= data)
        return jsonify({"message": "Product created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
      
@product_bp.route("/<int:product_id>/", methods=["DELETE"])
@jwt_required()
def delete_Product(product_id):
    jwt_user_id = int(get_jwt_identity())  
    jwt_role = get_jwt()["role"] 
    try :
        if jwt_role != "VENDOR":
            return jsonify({"error": "Unauthorized to delete this user"}), 403
        response = Product.delete_product(product_id=product_id,vendor_id=jwt_user_id)
        return response
    except Exception as e : 
	    return jsonify({"error": str(e)}),404


@product_bp.route("/products/<int:product_id>",methods = ["GET"])	
def get_product(product_id):
	product = Product.view_product(product_id=product_id)
	if product:
		return jsonify({
			"id":product.id,
			"title":product.title,
            "description":product.description,
			"created_at":product.created_at,
			"is_in_stock":product.is_in_stock,
			"stock_quantity":product.stock_quantity 
		})
	return jsonify({"error": "User not found"}), 404	

@product_bp.route("/products/<int:product_id>",methods = ["PUT"])
def update_product(product_id, updates, vendor_id):
    pass

@product_bp.route("/products/search", methods=["GET"])
def search_product():
    keyword = request.args.get('keyword')
    category = request.args.get('category')
    price_range = request.args.get('price_range')
    try:
        products = Product.search_products(keyword, category, price_range)
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@product_bp.route("/products/<int:product_id>/<int:owner_id>", methods=["POST"])  
def restock_product(product_id,owner_id):
    data = request.get_json() 
    print(data)
    try:
        Product.restock_product(product_id=product_id,owner_id=owner_id)
        return jsonify({"message": "Product Restocked"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

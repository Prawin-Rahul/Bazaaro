from flask import Blueprint, jsonify, request
from src.services.order_services import OrderService
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required , get_jwt_identity , get_jwt
from ..models import Order
from uuid import uuid4

order_bp = Blueprint("orders", __name__)

# NOTE : Currently idempotency_key is not stored in Localstorage or cache .
# Successful Response (response.ok) -  2xx HTTP status code -  key is removed from local storage
# Failed Response (Non-2xx Status) -  non-2xx HTTP status (e.g., 4xx or 5xx), response.ok evaluates to false - idempotency key is retained in local storage , used Again
# 								   -  4xx (Client Error):The request was invalid or unauthorized (e.g., missing parameters or idempotency key issues).
#								   -  5xx (Server Error): The server encountered an issue while processing the request.
# Network Error (.catch) - request fails entirely (e.g., due to network lag, timeout, or connection issues) - key is explicitly retained for retries.
## Aditional mechanisms like custom headers or retry tokens, especially in distributed or high-reliability systems.
'''
function generateIdempotencyKey() {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
}

function placeOrder(productId, customerId, quantity) {
    const idempotencyKey = localStorage.getItem('lastOrderKey') || generateIdempotencyKey();
    const orderData = { product_id: productId, customer_id: customerId, quantity: quantity };

    fetch('/order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Idempotency-Key': idempotencyKey,
        },
        body: JSON.stringify(orderData),
    })
    .then(response => {
        if (response.ok) {
            localStorage.removeItem('lastOrderKey'); // Clear key after success (removed from local storage)
        }
        return response.json();
    })
    .catch(error => {
        console.error('Error:', error);
        localStorage.setItem('lastOrderKey', idempotencyKey); // Retain key for retry
    });
}

'''


@order_bp.route("/", methods=["POST"])
@jwt_required()
def place_order():
    data = request.get_json()
    product_id = data.get("product_id")
    customer_id = data.get("customer_id")
    quantity = data.get("quantity")
    idempotency_key = request.headers.get("Idempotency-Key", str(uuid4()))  # Generate if not provided
    
    jwt_user_id = int(get_jwt_identity()) 
    if not all([product_id, customer_id, quantity]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        if jwt_user_id != customer_id:
            return jsonify({"error": "Unauthorized to place order"}), 403
        
        existing_order = OrderService.get_order_by_idempotency_key(idempotency_key)
        
        if existing_order:
            return jsonify({
                "message": "Order already placed",
                "id": existing_order.id,
                "product_id": existing_order.product_id,
                "customer_id": existing_order.customer_id,
                "quantity": existing_order.quantity,
                "total_price": existing_order.total_price,
                "created_at": existing_order.created_at
            }), 200


        order = OrderService.place_order(product_id=product_id, customer_id=customer_id, quantity=quantity, idempotency_key=idempotency_key)
        return jsonify({"message": "Product created"},{
            "id": order.id,
            "product_id": order.product_id,
            "customer_id": order.customer_id,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "created_at": order.created_at
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# Cancel an order
@order_bp.route("/<int:order_id>", methods=["DELETE"])
@jwt_required()
def cancel_order(order_id):
    jwt_user_id = int(get_jwt_identity()) 
    try:
        if not OrderService.is_order_owner(order_id, jwt_user_id):
            return jsonify({"error": "Unauthorized to cancel this order"}), 403
        OrderService.cancel_order(order_id)
        return jsonify({"message": "Order canceled successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

# Get a single order
@order_bp.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({
        "id": order.id,
        "product_id": order.product_id,
        "customer_id": order.customer_id,
        "quantity": order.quantity,
        "total_price": order.total_price,
        "created_at": order.created_at
    }), 200

# List all orders (with optional filtering)
@order_bp.route("/orders", methods=["GET"])
def list_orders():
    product_id = request.args.get("product_id")
    customer_id = request.args.get("customer_id")
    
    query = Order.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    orders = query.all()
    if not orders:
        return jsonify({"message": "No orders found"}), 404
    
    return jsonify([
        {
            "id": order.id,
            "product_id": order.product_id,
            "customer_id": order.customer_id,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "created_at": order.created_at
        } for order in orders
    ]), 200

# Search orders (example: filter by date or price range)
@order_bp.route("/orders/search", methods=["GET"])
def search_orders():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    
    query = Order.query
    if start_date and end_date:
        query = query.filter(Order.created_at.between(start_date, end_date))
    if min_price and max_price:
        query = query.filter(Order.total_price.between(min_price, max_price))
    
    orders = query.all()
    if not orders:
        return jsonify({"message": "No orders found"}), 404
    
    return jsonify([
        {
            "id": order.id,
            "product_id": order.product_id,
            "customer_id": order.customer_id,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "created_at": order.created_at
        } for order in orders
    ]), 200


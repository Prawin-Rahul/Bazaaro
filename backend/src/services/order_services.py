from .inventory_services import InventoryService
from src import db
from flask import jsonify

class OrderService:
    
    @staticmethod
    def is_order_owner(order_id, user_id):
        from ..models import Order
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        return order.customer_id == user_id

    @staticmethod
    def get_order_by_idempotency_key(idempotency_key):
        from ..models import Order
        return Order.query.filter_by(idempotency_key=idempotency_key).first()

    @staticmethod
    def place_order(product_id, customer_id, quantity,idempotency_key):
        from ..models import Product
        from ..models import Order
     
        try:
            product = Product.query.get(product_id)
            if product:
                order = Order(
					product_id=product_id,
					customer_id=customer_id,
					quantity=quantity,
                    idempotency_key=idempotency_key,
					total_price=Product.query.get(product_id).price * quantity
				)
                InventoryService.update_stock(product_id, quantity, action="subtract")
                db.session.add(order)
                db.session.commit()
                return order
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @staticmethod
    def cancel_order(order_id):
        from ..models import Order
        order = Order.query.get(order_id)
        if not order:
            raise ValueError("Order not found")
        InventoryService.update_stock(order.product_id, order.quantity, action="add")
        db.session.delete(order)
        db.session.commit()

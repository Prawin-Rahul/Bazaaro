from src import db

#  inventory logic is separate from the core application logic.

class InventoryService:
    @staticmethod
    def update_stock(product_id, quantity, action="add"):
        from ..models import Product
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        if action == "add":
            product.stock_quantity += quantity
        elif action == "subtract" and product.stock_quantity >= quantity:
            product.stock_quantity -= quantity
        else:
            raise ValueError("Insufficient stock")
        product.is_in_stock = product.stock_quantity > 0
        db.session.commit()
    
    @staticmethod
    def check_stock(product_id):
        from ..models import Product
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        return product.stock_quantity

    @staticmethod
    def verify_stock(product_id, quantity):
        from ..models import Product
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        if product.stock_quantity < quantity:
            raise ValueError("Insufficient stock")

    @staticmethod
    def reduce_stock(product_id, quantity):
        InventoryService.update_stock(product_id, quantity, action="subtract")

    @staticmethod
    def return_stock(product_id, quantity):
        InventoryService.update_stock(product_id, quantity, action="add")

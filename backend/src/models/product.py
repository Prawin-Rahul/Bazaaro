from enum import Enum
from src import db , bcrypt
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Enum as SqlAlchemyEnum
import pytz
from flask import jsonify
from src.services.inventory_services import InventoryService

class Product(db.Model):
    
    __tablename__ = 'product_list'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)
    category = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Integer,nullable=False)
    stock_quantity = db.Column(db.Integer)
    is_in_stock = db.Column(db.Boolean, default=True)  
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    image_url = db.Column(db.String(255), nullable=True)
    # Foreign_key
    owner_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)  
    # relationship
    vendor = db.relationship('UserProfile', back_populates='listed_product')
    
## For vendors
    @staticmethod 
    def create_product(data,id):
        product =Product(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            price=data["price"],
			stock_quantity=data["stock_quantity"],
            owner_id = id
        )
        db.session.add(product)
        db.session.commit()
        return product
    

    def update_product(product_id, updates, vendor_id):
        product = Product.query.get(product_id)
        if not product:
            return None
        if product.owner_id != vendor_id:
            raise PermissionError("Unauthorized")
        for key, value in updates.items():
            setattr(product, key, value)
        db.session.commit()


    @staticmethod 
    def delete_product(product_id, vendor_id):
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        if product.owner_id != vendor_id :
            return jsonify({"error": "Unauthorized access"}), 403
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
        
        
    
    def restock_product(product_id, quantity, owner_id):
        product = Product.query.get(product_id)
        if product.owner_id != owner_id:
            raise PermissionError("Unauthorized")
        InventoryService.update_stock(product_id, quantity, action="add")
    
    ### For Customers

    def view_product(product_id):
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        return product

    # Use datbase indexing Here
    def search_products(keyword=None, category=None, price_range=None):
        query = Product.query
        if keyword:
            query = query.filter(Product.name.ilike(f"%{keyword}%"))
        if category:
            query = query.filter_by(category=category)
        if price_range:
            query = query.filter(Product.price.between(price_range[0], price_range[1]))
        return query.all()

    ### Integration with Orders
    def verify_stock(product_id, quantity):
        product = Product.query.get(product_id)
        if product.stock_quantity < quantity:
            raise ValueError("Insufficient stock")

    def reduce_stock(product_id, quantity):
        InventoryService.update_stock(product_id, quantity, action="subtract")

    def return_stock(product_id, quantity):
        InventoryService.update_stock(product_id, quantity, action="add")

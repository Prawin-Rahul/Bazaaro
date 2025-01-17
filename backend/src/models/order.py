from src import db
from sqlalchemy.sql import func

class Order(db.Model):
    __tablename__ = 'order_table'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product_list.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    idempotency_key = db.Column(db.String(255), unique=True, nullable=False) 
    # Relationships
    product = db.relationship('Product', backref='orders')
    customer = db.relationship('UserProfile',backref=db.backref('orders', cascade='all, delete-orphan'))

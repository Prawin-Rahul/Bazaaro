from enum import Enum
from src import db , bcrypt
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Enum as SqlAlchemyEnum
import pytz

class UserRole(Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"

class UserProfile(db.Model):
    
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    role = db.Column(SqlAlchemyEnum(UserRole), nullable=False, default=UserRole.CUSTOMER)  # Default role - 'customer'
    image = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(100))
    # relationship 
    listed_product = db.relationship('Product',back_populates='vendor',lazy='dynamic',cascade='all, delete-orphan')


    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)
    	
    def get_created_at_ist(self):	
        ist = pytz.timezone("Asia/Kolkata")
        return self.created_at.astimezone(ist) if self.created_at else None
       
    @staticmethod
    def register_user(data):
        if not all(
            key in data
            for key in ["username", "email", "password",]
        ):
            raise ValueError("Missing required fields")
        if UserProfile.query.filter_by(email=data["email"]).first():
            raise ValueError("Email already exists")
        role = data.get("role","customer")
        if role not in [r.value for r in UserRole]:  
           raise ValueError("Invalid role")
        role = data.get("role", "customer")
		
        if role not in [r.value for r in UserRole]:  
            raise ValueError("Invalid role")
        user = UserProfile(
            username=data["username"],
			email=data["email"],
			role=role,
		)
        
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user
	
    
    @staticmethod
    def delete_user(user_id):
        try:
            user = UserProfile.query.filter_by(id=user_id).first()
            if user:
                db.session.delete(
                    user
                ) 
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user(id):
        user = UserProfile.query.filter_by(id=id).first()
        if not user:
            return None, []
        return user 

    @staticmethod
    def list_users():
        _users= []
        users = UserProfile.query.all()
        for user in users:
            _users.append({
            "username":user.username,
            "email":user.email,
            "user_id":user.id,
        })
        return _users

    @staticmethod
    def update_user(updates,id):
        pass
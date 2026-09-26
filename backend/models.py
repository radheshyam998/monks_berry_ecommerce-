from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="customer", nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="customer", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "role": self.role, "phone": self.phone, "address": self.address
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False)
    short_description = db.Column(db.String(500))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    mrp = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    weight = db.Column(db.String(50))
    image = db.Column(db.String(300))
    category = db.Column(db.String(80), default="Rosehip")
    benefits = db.Column(db.Text)
    usage = db.Column(db.Text)
    nutrition = db.Column(db.Text)
    featured = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "slug": self.slug,
            "short_description": self.short_description,
            "description": self.description, "price": self.price,
            "mrp": self.mrp, "discount": round(max(0, (self.mrp-self.price)/self.mrp*100)) if self.mrp else 0,
            "stock": self.stock, "weight": self.weight, "image": self.image,
            "category": self.category, "benefits": self.benefits or "",
            "usage": self.usage or "", "nutrition": self.nutrition or "",
            "featured": self.featured, "active": self.active
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    shipping = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), default="COD")
    payment_status = db.Column(db.String(30), default="Pending")
    order_status = db.Column(db.String(30), default="Placed")
    shipping_name = db.Column(db.String(120), nullable=False)
    shipping_phone = db.Column(db.String(30), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan", lazy=True)

    def to_dict(self, include_items=True):
        data = {
            "id": self.id, "order_number": self.order_number, "subtotal": self.subtotal,
            "shipping": self.shipping, "discount": self.discount, "total": self.total,
            "payment_method": self.payment_method, "payment_status": self.payment_status,
            "order_status": self.order_status, "shipping_name": self.shipping_name,
            "shipping_phone": self.shipping_phone, "shipping_address": self.shipping_address,
            "notes": self.notes, "created_at": self.created_at.isoformat()
        }
        if include_items:
            data["items"] = [i.to_dict() for i in self.items]
        return data

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(180), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(300))

    def to_dict(self):
        return {
            "id": self.id, "product_id": self.product_id, "product_name": self.product_name,
            "price": self.price, "quantity": self.quantity, "image": self.image
        }

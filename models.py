from database import db
from datetime import datetime

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    square_feet = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    additional_images = db.Column(db.JSON)
    floorplan_url = db.Column(db.String(500))
    flyer_url = db.Column(db.String(500))
    available_space = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    listing_type = db.Column(db.String(50))
    business_type = db.Column(db.String(100))
    ceiling_height = db.Column(db.Float)
    loading_docks = db.Column(db.Integer)
    power_capacity = db.Column(db.String(50))
    column_spacing = db.Column(db.String(50))
    year_built = db.Column(db.Integer)
    property_features = db.Column(db.JSON)

class BusinessTypePreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_type = db.Column(db.String(100), nullable=False)
    min_square_feet = db.Column(db.Integer)
    max_square_feet = db.Column(db.Integer)
    min_ceiling_height = db.Column(db.Float)
    min_loading_docks = db.Column(db.Integer)
    power_requirements = db.Column(db.String(50))
    preferred_features = db.Column(db.JSON)
    importance_weights = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    business_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(200), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'lease' or 'sale'
    square_feet = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
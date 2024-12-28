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
    additional_images = db.Column(db.JSON)  # Store multiple image URLs
    floorplan_url = db.Column(db.String(500))  # URL for floorplan image
    flyer_url = db.Column(db.String(500))  # URL for property flyer
    available_space = db.Column(db.Text)  # Details about available space
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # New fields for business type recommendation
    business_type = db.Column(db.String(100))  # e.g., "manufacturing", "warehousing", "distribution"
    ceiling_height = db.Column(db.Float)  # in feet
    loading_docks = db.Column(db.Integer)
    power_capacity = db.Column(db.String(50))  # e.g., "2000A, 480/277V"
    column_spacing = db.Column(db.String(50))  # e.g., "40' x 40'"
    year_built = db.Column(db.Integer)
    property_features = db.Column(db.JSON)  # Additional features as JSON

class BusinessTypePreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_type = db.Column(db.String(100), nullable=False)
    min_square_feet = db.Column(db.Integer)
    max_square_feet = db.Column(db.Integer)
    min_ceiling_height = db.Column(db.Float)
    min_loading_docks = db.Column(db.Integer)
    power_requirements = db.Column(db.String(50))
    preferred_features = db.Column(db.JSON)
    importance_weights = db.Column(db.JSON)  # Weights for different features
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    business_type = db.Column(db.String(100))  # New field for business type
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "industrial-properties-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Import routes after app initialization
from models import Property, Inquiry

@app.route('/')
def index():
    featured_properties = Property.query.filter_by(is_featured=True).limit(6).all()
    return render_template('index.html', properties=featured_properties)

@app.route('/properties')
def properties():
    properties = Property.query.all()
    return render_template('properties.html', properties=properties)

@app.route('/property/<int:id>')
def property_detail(id):
    property = Property.query.get_or_404(id)
    return render_template('property_detail.html', property=property)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        inquiry = Inquiry(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            message=request.form['message'],
            created_at=datetime.utcnow()
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Thank you for your inquiry. We will contact you soon!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# Initialize database
with app.app_context():
    db.create_all()

    # Add sample data if database is empty
    if not Property.query.first():
        sample_properties = [
            Property(
                title="Broadbent Business Park",
                description="Premium industrial space in Salt Lake City's thriving business district",
                square_feet=150000,
                price=2500000,
                location="3607 W 2100 S Salt Lake City, UT",
                latitude=40.72614,
                longitude=-111.96744,
                image_url="https://images.unsplash.com/photo-1565077744449-04961a45ec61",
                additional_images=["https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
                                "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d"],
                floorplan_url="https://example.com/floorplans/broadbent.pdf",
                available_space="Suite A: 5,000 sq ft\nSuite B: 7,500 sq ft\nSuite C: 10,000 sq ft",
                is_featured=True
            ),
            Property(
                title="Redwood Business Park",
                description="Modern industrial complex with excellent accessibility",
                square_feet=200000,
                price=3000000,
                location="2850 S Redwood Rd West Valley, UT",
                latitude=40.71643,
                longitude=-111.93912,
                image_url="https://images.unsplash.com/photo-1664382953403-fc1ac77073a0",
                additional_images=["https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
                                "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d"],
                floorplan_url="https://example.com/floorplans/redwood.pdf",
                available_space="Unit 1: 15,000 sq ft\nUnit 2: 20,000 sq ft",
                is_featured=True
            ),
            Property(
                title="Sandy Business Park",
                description="State-of-the-art business park in Sandy's growing commercial district",
                square_feet=175000,
                price=2750000,
                location="9520 S 500 W Sandy, UT",
                latitude=40.58764,
                longitude=-111.90606,
                image_url="https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d",
                additional_images=["https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",
                                "https://images.unsplash.com/photo-1664382953403-fc1ac77073a0"],
                floorplan_url="https://example.com/floorplans/sandy.pdf",
                available_space="Building A: 25,000 sq ft\nBuilding B: 30,000 sq ft",
                is_featured=True
            )
        ]
        db.session.bulk_save_objects(sample_properties)
        db.session.commit()
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
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///properties.db")
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
                title="Modern Warehouse Complex",
                description="State-of-the-art warehouse facility with loading docks",
                square_feet=50000,
                price=2500000,
                location="123 Industrial Park Road",
                latitude=40.7128,
                longitude=-74.0060,
                image_url="https://images.unsplash.com/photo-1565077744449-04961a45ec61",
                is_featured=True
            ),
            Property(
                title="Distribution Center",
                description="Large distribution center with excellent highway access",
                square_feet=75000,
                price=3750000,
                location="456 Logistics Way",
                latitude=40.7589,
                longitude=-73.9851,
                image_url="https://images.unsplash.com/photo-1664382953403-fc1ac77073a0",
                is_featured=True
            )
        ]
        db.session.bulk_save_objects(sample_properties)
        db.session.commit()

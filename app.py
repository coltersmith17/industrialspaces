import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from datetime import datetime
from database import db

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# create the app
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "industrial-properties-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Import models after db initialization
from models import Property, Inquiry, BusinessTypePreference
from services.recommendation_engine import PropertyRecommendationEngine

# Initialize recommendation engine
recommendation_engine = PropertyRecommendationEngine()

@app.route('/')
def index():
    featured_properties = Property.query.filter_by(is_featured=True).limit(6).all()
    return render_template('index.html', properties=featured_properties)

@app.route('/properties')
def properties():
    business_type = request.args.get('business_type')
    min_square_feet = request.args.get('min_square_feet', type=int)
    max_square_feet = request.args.get('max_square_feet', type=int)

    properties = Property.query.all()

    if business_type:
        recommended = recommendation_engine.get_recommendations(
            properties,
            business_type,
            min_square_feet,
            max_square_feet
        )
        properties = [r['property'] for r in recommended]

    return render_template('properties.html', 
                         properties=properties,
                         business_type=business_type)

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
            business_type=request.form.get('business_type'),
            created_at=datetime.utcnow()
        )
        db.session.add(inquiry)
        db.session.commit()
        flash('Thank you for your inquiry. We will contact you soon!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    business_type = data.get('business_type')
    min_square_feet = data.get('min_square_feet')
    max_square_feet = data.get('max_square_feet')

    if not business_type:
        return jsonify({'error': 'Business type is required'}), 400

    properties = Property.query.all()
    recommendations = recommendation_engine.get_recommendations(
        properties,
        business_type,
        min_square_feet,
        max_square_feet
    )

    return jsonify({
        'recommendations': [
            {
                'id': r['property'].id,
                'title': r['property'].title,
                'score': r['score']
            }
            for r in recommendations[:5]  # Return top 5 recommendations
        ]
    })

@app.route('/for-lease')
def for_lease():
    properties = Property.query.filter_by(listing_type='lease').all()
    return render_template('properties.html', 
                         properties=properties,
                         page_title='Properties For Lease')

@app.route('/for-sale')
def for_sale():
    properties = Property.query.filter_by(listing_type='sale').all()
    return render_template('properties.html', 
                         page_title='Properties For Sale',
                         properties=properties)


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
                business_type="manufacturing",
                ceiling_height=24.0,
                loading_docks=8,
                power_capacity="2000A, 480/277V",
                column_spacing="40' x 40'",
                year_built=2015,
                is_featured=True,
                listing_type='sale' #Added listing type
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
                business_type="warehousing",
                ceiling_height=32.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="50' x 50'",
                year_built=2018,
                is_featured=True,
                listing_type='lease' #Added listing type
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
                business_type="distribution",
                ceiling_height=28.0,
                loading_docks=16,
                power_capacity="2500A, 480/277V",
                column_spacing="45' x 45'",
                year_built=2020,
                is_featured=True,
                listing_type='sale' #Added listing type
            )
        ]
        db.session.bulk_save_objects(sample_properties)

        # Add sample business type preferences
        sample_preferences = [
            BusinessTypePreference(
                business_type="manufacturing",
                min_square_feet=100000,
                max_square_feet=250000,
                min_ceiling_height=20.0,
                min_loading_docks=6,
                power_requirements="2000A+",
                preferred_features={"column_spacing": "40' x 40'"},
                importance_weights={"square_feet": 0.3, "ceiling_height": 0.2, "loading_docks": 0.2, "power": 0.3}
            ),
            BusinessTypePreference(
                business_type="warehousing",
                min_square_feet=150000,
                max_square_feet=300000,
                min_ceiling_height=30.0,
                min_loading_docks=10,
                power_requirements="1500A+",
                preferred_features={"column_spacing": "50' x 50'"},
                importance_weights={"square_feet": 0.4, "ceiling_height": 0.3, "loading_docks": 0.2, "power": 0.1}
            ),
            BusinessTypePreference(
                business_type="distribution",
                min_square_feet=125000,
                max_square_feet=275000,
                min_ceiling_height=25.0,
                min_loading_docks=12,
                power_requirements="2000A+",
                preferred_features={"column_spacing": "45' x 45'"},
                importance_weights={"square_feet": 0.3, "ceiling_height": 0.2, "loading_docks": 0.4, "power": 0.1}
            )
        ]
        db.session.bulk_save_objects(sample_preferences)
        db.session.commit()
import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from database import db
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
from models import Property, Inquiry, BusinessTypePreference, Transaction
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
                         properties=properties,
                         page_title='Properties For Sale')

@app.route('/transactions')
def transactions():
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/state-of-market')
def state_of_market():
    return render_template('state-of-market.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

def init_sample_data():
    """Initialize sample data for the application"""
    logger.info("Initializing sample data...")

    # Set up static image directory if it doesn't exist
    static_img_dir = os.path.join(app.static_folder, 'images')
    if not os.path.exists(static_img_dir):
        os.makedirs(static_img_dir)
        logger.info(f"Created static images directory: {static_img_dir}")

    # Copy the Redwood Business Park image from attached assets to static folder
    source_image = 'attached_assets/2850 S Redwood Rd Edit.jpg'
    dest_image = os.path.join(static_img_dir, '2850_S_Redwood_Rd_Edit.jpg')

    try:
        if os.path.exists(source_image):
            shutil.copy2(source_image, dest_image)
            logger.info(f"Successfully copied image from {source_image} to {dest_image}")
            redwood_image_url = '/static/images/2850_S_Redwood_Rd_Edit.jpg'
        else:
            logger.error(f"Source image not found: {source_image}")
            redwood_image_url = "https://images.unsplash.com/photo-1565793979436-5a9844c3d0dd"
    except Exception as e:
        logger.error(f"Error copying image: {str(e)}")
        redwood_image_url = "https://images.unsplash.com/photo-1565793979436-5a9844c3d0dd"

    # Add sample properties if none exist
    if not Property.query.first():
        logger.info("Adding sample properties...")

        sample_properties = [
            Property(
                title="Broadbent Business Park",
                description="Premium industrial space in Salt Lake City's thriving business district",
                square_feet=150000,
                price=1.05,
                location="3607 W 2100 S Salt Lake City, UT",
                latitude=40.72614,
                longitude=-111.96744,
                image_url="https://images.unsplash.com/photo-1587534774765-84ef7be11179",
                additional_images=[
                    "https://images.unsplash.com/photo-1580674684081-7617fbf3d745",
                    "https://images.unsplash.com/photo-1581578731548-c64695cc6952"
                ],
                floorplan_url="https://example.com/floorplans/broadbent.pdf",
                available_space="Suite A: 5,000 sq ft\nSuite B: 7,500 sq ft\nSuite C: 10,000 sq ft",
                business_type="manufacturing",
                ceiling_height=32.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="40' x 40'",
                year_built=2015,
                is_featured=True,
                listing_type='lease'
            ),
            Property(
                title="Redwood Business Park",
                description="Modern industrial complex with excellent accessibility",
                square_feet=200000,
                price=1.05,
                location="2850 S Redwood Rd West Valley, UT",
                latitude=40.71643,
                longitude=-111.93912,
                image_url=redwood_image_url,
                additional_images=[
                    "https://images.unsplash.com/photo-1581578731548-c64695cc6952",
                    "https://images.unsplash.com/photo-1580674684081-7617fbf3d745"
                ],
                floorplan_url="https://example.com/floorplans/redwood.pdf",
                available_space="Unit 1: 15,000 sq ft\nUnit 2: 20,000 sq ft",
                business_type="warehousing",
                ceiling_height=32.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="50' x 50'",
                year_built=2018,
                is_featured=True,
                listing_type='lease'
            ),
            Property(
                title="Sandy Business Park",
                description="State-of-the-art business park in Sandy's growing commercial district",
                square_feet=175000,
                price=1.05,
                location="9520 S 500 W Sandy, UT",
                latitude=40.58764,
                longitude=-111.90606,
                image_url="https://images.unsplash.com/photo-1565793979436-5a9844c3d0dd",
                additional_images=[
                    "https://images.unsplash.com/photo-1587534774765-84ef7be11179",
                    "https://images.unsplash.com/photo-1580674684081-7617fbf3d745"
                ],
                floorplan_url="https://example.com/floorplans/sandy.pdf",
                available_space="Building A: 25,000 sq ft\nBuilding B: 30,000 sq ft",
                business_type="distribution",
                ceiling_height=32.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="45' x 45'",
                year_built=2020,
                is_featured=True,
                listing_type='lease'
            )
        ]
        db.session.bulk_save_objects(sample_properties)
        logger.info("Sample properties added successfully")

    try:
        db.session.commit()
        logger.info("All sample data committed successfully")
    except Exception as e:
        logger.error(f"Error committing sample data: {str(e)}")
        db.session.rollback()
        raise

# Initialize database and sample data
with app.app_context():
    db.create_all()
    init_sample_data()
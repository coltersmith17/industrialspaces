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
    properties = Property.query.all()
    return render_template('properties.html', properties=properties)

@app.route('/property/<slug>')
def property_detail(slug):
    property = Property.query.filter_by(slug=slug).first_or_404()
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

@app.route('/article/<slug>')
def article_detail(slug):
    # This is a placeholder route for the article details
    # In a real application, you would fetch the article from a database
    return render_template('article_detail.html', slug=slug)


def copy_image(source_filename, dest_filename):
    """Helper function to copy images from attached_assets to static/images"""
    source_path = os.path.join('attached_assets', source_filename)
    dest_path = os.path.join('static', 'images', dest_filename)

    try:
        if os.path.exists(source_path):
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
            logger.info(f"Successfully copied image from {source_path} to {dest_path}")
            return f'/static/images/{dest_filename}'
        else:
            logger.error(f"Source image not found: {source_path}")
            return None
    except Exception as e:
        logger.error(f"Error copying image {source_filename}: {str(e)}")
        return None

def init_sample_data():
    """Initialize sample data for the application"""
    logger.info("Initializing sample data...")

    # Copy all business park images
    broadbent_image_url = copy_image('broadbentmain.jpg', 'broadbentmain.jpg')
    redwood_image_url = copy_image('redwoodmain.jpg', 'redwoodmain.jpg')
    sandy_image_url = copy_image('sipmain.jpg', 'sipmain.jpg')
    modern_building_url = copy_image('2400smain.JPG', '2400smain.jpg')
    power_district_url = copy_image('139s1400wmain.jpg', '139s1400wmain.jpg')

    # Add sample properties if none exist
    if not Property.query.first():
        logger.info("Adding sample properties...")

        sample_properties = [
            Property(
                slug="broadbent",
                title="Broadbent Business Park",
                description="Multi-Tenant Industrial Building in the Heart of Salt Lake with a short, 5 minute drive to the Salt Lake City International Airport",
                square_feet=150000,
                square_feet_range="1,482 - 3,774 SF",
                price=1.05,
                price_display="$1.05 PSF NNN",
                location="3607 W 2100 S Salt Lake City, UT",
                latitude=40.72614,
                longitude=-111.96744,
                image_url=broadbent_image_url or "https://images.unsplash.com/photo-1587534774765-84ef7be11179",
                additional_images=[],
                floorplan_url="https://example.com/floorplans/broadbent.pdf",
                available_space=(
                    "Unit 3668: 1,968 SF\n"
                    "Unit 3673: 1,482 SF\n"
                    "Unit 3671: 2,292 SF\n"
                    "Units 3671 & 3673: 3,774 SF\n"
                    "Unit 3649: 2,026 SF\n"
                    "Unit 3621: 2,568 SF"
                ),
                business_type="manufacturing",
                ceiling_height=12.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="40' x 40'",
                year_built=2015,
                is_featured=True,
                listing_type='lease',
                property_features=[
                    "Industrial & Manufacturing Warehouse Space",
                    "(1) 10x10 GL Door Per Unit",
                    "Ample Parking",
                    "5 Minutes to SLC International Airport",
                    "Additional Office / Retail Spaces Available",
                    "Signage Available"
                ]
            ),
            Property(
                slug="redwood",
                title="Redwood Business Park",
                description="A recently repainted business park, with easy freeway access to Highway 201, I-15, I-215 and a traditional warehouse layout",
                square_feet=200000,
                square_feet_range="1,600 - 3,200 SF",
                price=1.05,
                price_display="$1.05 PSF NNN",
                location="2850 S Redwood Rd West Valley, UT",
                latitude=40.71643,
                longitude=-111.93912,
                image_url=redwood_image_url or "https://images.unsplash.com/photo-1565793979436-5a9844c3d0dd",
                additional_images=[],
                floorplan_url="https://example.com/floorplans/redwood.pdf",
                available_space=(
                    "Units B-9/10: 3,200 SF\n"
                    "Unit C-8: 1,600 SF\n"
                    "Unit C-12: 1,600 SF"
                ),
                business_type="warehousing",
                ceiling_height=12.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="50' x 50'",
                year_built=2018,
                is_featured=True,
                listing_type='lease',
                property_features=[
                    "(1) 10x10 Ground Level Door Per Unit",
                    "12' Clear Height",
                    "Redwood Road Frontage",
                    "Easy Highway Access",
                    "Signage Available"
                ]
            ),
            Property(
                slug="sip",
                title="Sandy Business Park",
                description="A 5 building Business Park just minutes from I-15 with an 18' Clear Height and 12x12 Ground Level Doors",
                square_feet=175000,
                square_feet_range="1,200 SF",
                price=1.40,
                price_display="$1.40 PSF NNN",
                location="9520 S 500 W Sandy, UT",
                latitude=40.58764,
                longitude=-111.90606,
                image_url=sandy_image_url or "https://images.unsplash.com/photo-1565793979436-5a9844c3d0dd",
                additional_images=[],
                floorplan_url="https://example.com/floorplans/sandy.pdf",
                available_space="Building C: 1,200 SF",
                business_type="distribution",
                ceiling_height=18.0,
                loading_docks=12,
                power_capacity="3000A, 480/277V",
                column_spacing="45' x 45'",
                year_built=2020,
                is_featured=True,
                listing_type='lease',
                property_features=[
                    "(1) 12x12 GL Door Per Unit",
                    "3 Phase Power*",
                    "Clear Height: 18'",
                    "Signage Available",
                    "Additional Office Space"
                ]
            ),
            Property(
                slug="power-district",
                title="Power District Warehouse",
                description="A heavy-powered warehouse adjacent to the future Larry H. Miller Ballpark Development with Seller Financing Available",
                square_feet=4400,
                square_feet_range="4,400 SF",
                price=1200000,
                price_display="$1,200,000",
                location="139 S 1400 W Salt Lake City, UT 84107",
                latitude=40.767,
                longitude=-111.928,
                image_url=power_district_url or "https://images.unsplash.com/photo-1565793979436-5a9844c3d0dd",
                additional_images=[],
                floorplan_url=None,
                available_space="4,400 SF",
                business_type=None,
                ceiling_height=16.0,
                loading_docks=1,
                power_capacity="3 Phase 400 Amps",
                column_spacing="30' x 30'",
                year_built=1975,
                is_featured=True,
                listing_type='sale',
                property_features=[
                    "Seller Financing Available",
                    "Heavy Power: 3 Phase 400 Amps",
                    "1 - (10x10) GL Door",
                    "Adjacent to Proposed MLB Stadium",
                    "Easy Access to I-15, I-215 & I-80",
                    "Located in an Opportunity Zone",
                    "Walking Distance to Trax Station",
                    "Lease Options Available as Well"
                ]
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
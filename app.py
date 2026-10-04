import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, abort
)
from flask_sqlalchemy import SQLAlchemy
import qrcode

# Initialize Flask Application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart_traffic_enforcement_secret_key_2026'

# Configure SQLite Database in the instance directory
os.makedirs(app.instance_path, exist_ok=True)
db_path = os.path.join(app.instance_path, 'traffic.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ensure QR codes directory exists
QR_FOLDER = os.path.join(app.static_folder, 'qr_codes')
os.makedirs(QR_FOLDER, exist_ok=True)

# Pre-defined list of common violation types
VIOLATION_TYPES = [
    "No Helmet",
    "Overspeeding",
    "Signal Violation",
    "No Seat Belt",
    "Wrong Parking",
    "Drunk and Driving",
    "Triple Riding",
    "Using Mobile While Driving"
]

# ==============================================================================
# DATABASE MODEL
# ==============================================================================
class Violation(db.Model):
    __tablename__ = 'violations'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(30), nullable=False)
    violation_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    violation_date = db.Column(db.String(20), nullable=False)
    fine_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Unpaid", nullable=False)

    def __repr__(self):
        return f"<Violation {self.id}: {self.vehicle_number} - {self.violation_type}>"


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def login_required(f):
    """Decorator to protect officer-only routes using session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please log in as an officer to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def generate_qr_code(violation_id):
    """
    Dynamically generate a QR code pointing to the public status page.
    The URL uses the host and scheme of the current request.
    Saved as: static/qr_codes/challan_<violation_id>.png
    """
    filename = f"challan_{violation_id}.png"
    filepath = os.path.join(QR_FOLDER, filename)
    status_url = url_for('public_status', id=violation_id, _external=True)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(status_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f2c59", back_color="white")
    img.save(filepath)

    return filename


# ==============================================================================
# AUTHENTICATION ROUTES
# ==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Officer authentication route."""
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Hardcoded officer credentials for mini-project requirement
        if username == 'KXNISH' and password == 'traffic123':
            session['logged_in'] = True
            session['officer_name'] = username
            flash("Logged in successfully as KXNISH.", "success")
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash("Invalid officer credentials. Please check username and password.", "danger")

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out officer and clear session."""
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


# ==============================================================================
# OFFICER MANAGEMENT ROUTES (PROTECTED)
# ==============================================================================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """
    Display statistics:
    - Total Violations
    - Paid Violations
    - Unpaid Violations
    And recent violations list.
    """
    total_violations = Violation.query.count()
    paid_violations = Violation.query.filter_by(status='Paid').count()
    unpaid_violations = Violation.query.filter_by(status='Unpaid').count()

    recent_violations = Violation.query.order_by(Violation.id.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_violations=total_violations,
        paid_violations=paid_violations,
        unpaid_violations=unpaid_violations,
        recent_violations=recent_violations
    )


@app.route('/add-violation', methods=['GET', 'POST'])
@login_required
def add_violation():
    """
    Officer form to register a new violation.
    Auto-assigns status = 'Unpaid' and generates QR code.
    """
    today_date = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        violation_type = request.form.get('violation_type', '').strip()
        location = request.form.get('location', '').strip()
        violation_date = request.form.get('violation_date', '').strip()
        fine_amount_str = request.form.get('fine_amount', '').strip()

        # Server-side validation
        if not vehicle_number or not violation_type or not location or not violation_date or not fine_amount_str:
            flash("All fields are required. Please fill out the complete form.", "danger")
            return render_template('add_violation.html', today_date=today_date)

        try:
            fine_amount = int(fine_amount_str)
            if fine_amount <= 0:
                raise ValueError("Fine amount must be positive.")
        except ValueError:
            flash("Fine amount must be a valid positive number.", "danger")
            return render_template('add_violation.html', today_date=today_date)

        # Create new violation record with automatic Unpaid status
        new_violation = Violation(
            vehicle_number=vehicle_number,
            violation_type=violation_type,
            location=location,
            violation_date=violation_date,
            fine_amount=fine_amount,
            status="Unpaid"  # Automatically assigned
        )

        db.session.add(new_violation)
        db.session.commit()

        # Generate QR code immediately
        generate_qr_code(new_violation.id)

        flash("Violation added successfully.", "success")
        return redirect(url_for('challan', id=new_violation.id))

    return render_template('add_violation.html', today_date=today_date)


@app.route('/history')
@login_required
def history():
    """
    View, search by vehicle number, and filter violations by:
    - Date
    - Status (All, Paid, Unpaid)
    - Violation Type
    """
    search_vehicle = request.args.get('vehicle', '').strip().upper()
    filter_type = request.args.get('type', '').strip()
    filter_status = request.args.get('status', '').strip()
    filter_date = request.args.get('date', '').strip()

    query = Violation.query

    # Search by vehicle number
    if search_vehicle:
        query = query.filter(Violation.vehicle_number.ilike(f"%{search_vehicle}%"))

    # Filter by violation type
    if filter_type:
        query = query.filter(Violation.violation_type == filter_type)

    # Filter by status
    if filter_status and filter_status != 'All':
        query = query.filter(Violation.status == filter_status)

    # Filter by date
    if filter_date:
        query = query.filter(Violation.violation_date == filter_date)

    violations = query.order_by(Violation.id.desc()).all()

    # Flash notification if user searched and nothing matched
    if search_vehicle and not violations:
        flash("No violation records found.", "info")

    return render_template(
        'history.html',
        violations=violations,
        search_vehicle=search_vehicle,
        filter_type=filter_type,
        filter_status=filter_status,
        filter_date=filter_date,
        violation_types=VIOLATION_TYPES
    )


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_violation(id):
    """Edit existing violation record."""
    violation = db.get_or_404(Violation, id)

    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        violation_type = request.form.get('violation_type', '').strip()
        location = request.form.get('location', '').strip()
        violation_date = request.form.get('violation_date', '').strip()
        fine_amount_str = request.form.get('fine_amount', '').strip()
        status = request.form.get('status', '').strip()

        # Validation
        if not vehicle_number or not violation_type or not location or not violation_date or not fine_amount_str:
            flash("All fields are required. Please check your inputs.", "danger")
            return render_template('edit_violation.html', violation=violation)

        try:
            fine_amount = int(fine_amount_str)
            if fine_amount <= 0:
                raise ValueError("Fine amount must be positive.")
        except ValueError:
            flash("Fine amount must be a valid positive number.", "danger")
            return render_template('edit_violation.html', violation=violation)

        if status not in ['Paid', 'Unpaid']:
            status = 'Unpaid'

        # Update record
        violation.vehicle_number = vehicle_number
        violation.violation_type = violation_type
        violation.location = location
        violation.violation_date = violation_date
        violation.fine_amount = fine_amount
        violation.status = status

        db.session.commit()

        flash("Violation updated successfully.", "success")
        return redirect(url_for('history'))

    return render_template('edit_violation.html', violation=violation)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_violation(id):
    """Delete a violation record."""
    violation = db.get_or_404(Violation, id)

    # Clean up associated QR code if present
    qr_file = os.path.join(QR_FOLDER, f"challan_{violation.id}.png")
    if os.path.exists(qr_file):
        try:
            os.remove(qr_file)
        except OSError:
            pass

    db.session.delete(violation)
    db.session.commit()

    flash("Violation deleted successfully.", "success")
    return redirect(url_for('history'))


@app.route('/mark-paid/<int:id>', methods=['GET', 'POST'])
@login_required
def mark_paid(id):
    """Quick action to update status from Unpaid to Paid."""
    violation = db.get_or_404(Violation, id)

    if violation.status != 'Paid':
        violation.status = 'Paid'
        db.session.commit()
        flash("Payment status updated successfully.", "success")
    else:
        flash("Violation is already marked as Paid.", "info")

    # Redirect to referrer or history
    referrer = request.referrer
    if referrer and ('/challan/' in referrer or '/history' in referrer or '/dashboard' in referrer):
        return redirect(referrer)
    return redirect(url_for('history'))


@app.route('/challan/<int:id>')
@login_required
def challan(id):
    """View and print digital challan with dynamic QR code."""
    violation = db.get_or_404(Violation, id)

    # Regenerate the QR code so its destination matches the current host.
    qr_filename = f"challan_{violation.id}.png"
    generate_qr_code(violation.id)

    status_url = url_for('public_status', id=violation.id, _external=True)

    return render_template(
        'challan.html',
        violation=violation,
        qr_filename=qr_filename,
        status_url=status_url
    )


# ==============================================================================
# PUBLIC ROUTE (ACCESSIBLE WITHOUT LOGIN)
# ==============================================================================
@app.route('/status/<int:id>')
def public_status(id):
    """
    Publicly accessible read-only verification page scanned via QR code.
    No login required.
    """
    violation = db.session.get(Violation, id)
    # If violation does not exist, public_status.html displays "Invalid or unavailable challan."
    return render_template('public_status.html', violation=violation)


# ==============================================================================
# ERROR HANDLERS
# ==============================================================================
@app.errorhandler(404)
def not_found_error(error):
    return render_template('public_status.html', violation=None), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash("An unexpected server error occurred. Please try again.", "danger")
    return redirect(url_for('dashboard'))


# ==============================================================================
# DATABASE INITIALIZATION AND SEED DATA
# ==============================================================================
def seed_database():
    """Seed initial sample records as required by the specification."""
    with app.app_context():
        db.create_all()

        if Violation.query.count() == 0:
            sample_violations = [
                Violation(
                    vehicle_number="TN30AB1234",
                    violation_type="No Helmet",
                    location="Salem",
                    violation_date="2026-09-26",
                    fine_amount=1000,
                    status="Unpaid"
                ),
                Violation(
                    vehicle_number="TN33CD5678",
                    violation_type="Overspeeding",
                    location="Namakkal",
                    violation_date="2026-09-25",
                    fine_amount=2000,
                    status="Paid"
                ),
                Violation(
                    vehicle_number="TN29EF9012",
                    violation_type="Signal Violation",
                    location="Erode",
                    violation_date="2026-09-24",
                    fine_amount=500,
                    status="Unpaid"
                )
            ]

            db.session.bulk_save_objects(sample_violations)
            db.session.commit()

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, host='127.0.0.1', port=5000)

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import enum, os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('ROADGUARD_SECRET', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roadguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------- MODELS ----------
class Role(enum.Enum):
    USER = "user"
    MECHANIC = "mechanic"
    ADMIN = "admin"

# models.py (or wherever your models are)
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))  # "user", "mechanic", "admin"
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# app.py
@app.route('/notifications')
@login_required
def notifications():
    # Show notifications for the current user's role
    notes = Notification.query.filter_by(role=current_user.role).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notes)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))  # NOTE: store hashed in production
    role = db.Column(db.String(20), default=Role.USER.value)
    phone = db.Column(db.String(20))

class Workshop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    status = db.Column(db.String(50), default="open")  # open/closed
    rating = db.Column(db.Float, default=0.0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    owner = db.relationship("User", backref="owned_workshops")
    reviews = db.relationship("WorkshopReview", backref="workshop", cascade="all, delete-orphan")


class WorkshopReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="workshop_reviews")

@app.route("/workshops")
@login_required
def workshops():
    # Fetch all workshops
    all_workshops = Workshop.query.all()
    return render_template("workshops.html", workshops=all_workshops)


@app.route("/workshop/<int:w_id>")
@login_required
def workshop_detail(w_id):
    ws = Workshop.query.get_or_404(w_id)
    return render_template("workshop_detail.html", workshop=ws)


@app.route("/workshop/<int:w_id>/review", methods=["POST"])
@login_required
def add_review(w_id):
    ws = Workshop.query.get_or_404(w_id)
    # Check if user completed service with this workshop
    completed_services = ServiceRequest.query.filter_by(user_id=current_user.id, status="completed").all()
    if not completed_services:
        flash("You can review only after completing a service!", "danger")
        return redirect(url_for("workshop_detail", w_id=w_id))

    rating = int(request.form.get("rating"))
    comment = request.form.get("comment")

    review = WorkshopReview(user_id=current_user.id, workshop_id=w_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()

    # Update workshop rating
    reviews = ws.reviews
    ws.rating = sum(r.rating for r in reviews)/len(reviews)
    db.session.commit()

    flash("Review submitted!", "success")
    return redirect(url_for("workshop_detail", w_id=w_id))

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    status = db.Column(db.String(50), default='Submitted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_mechanic_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    mechanic_response = db.Column(db.Text, nullable=True)

    # ✅ Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="requests_made")
    mechanic = db.relationship("User", foreign_keys=[assigned_mechanic_id], backref="requests_taken")


# ---------- LOGIN ----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------- INIT DB ----------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@roadguard.local').first():
        admin = User(
            name='Admin',
            email='admin@roadguard.local',
            password='admin',  # TODO: hash in production
            role=Role.ADMIN.value
        )
        db.session.add(admin)
        db.session.commit()


# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    # Allow only logged-in users (any role)
    current_user.name = request.form.get("name")
    current_user.email = request.form.get("email")
    current_user.phone = request.form.get("phone")

    db.session.commit()
    flash("Profile updated successfully ✅", "success")

    # redirect back to user_dashboard (or mechanic/admin depending on role)
    if current_user.role == Role.USER.value:
        return redirect(url_for("user_dashboard"))
    elif current_user.role == Role.MECHANIC.value:
        return redirect(url_for("mechanic_dashboard"))
    else:
        return redirect(url_for("admin_dashboard"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')
        phone = request.form.get('phone', '')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'warning')
            return redirect(url_for('register'))

        user = User(name=name, email=email, password=password, role=role, phone=phone)
        db.session.add(user)
        db.session.commit()
        flash('Registered! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        u = User.query.filter_by(email=email, password=password).first()

        if not u:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

        login_user(u)
        flash('Logged in', 'success')

        if u.role == Role.ADMIN.value:
            return redirect(url_for('admin_dashboard'))
        elif u.role == Role.MECHANIC.value:
            return redirect(url_for('mechanic_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


# ---------- USER ----------
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != Role.USER.value:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    requests = ServiceRequest.query.filter_by(user_id=current_user.id).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('user_dashboard.html', requests=requests)


@app.route('/request/new', methods=['GET', 'POST'])
@login_required
def new_request():
    if current_user.role != Role.USER.value:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        lat = float(request.form['lat'])
        lng = float(request.form['lng'])

        sr = ServiceRequest(
            user_id=current_user.id,
            title=title,
            description=description,
            lat=lat,
            lng=lng
        )
        db.session.add(sr)
        db.session.commit()

        flash('Service request submitted', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('request_form.html')


@app.route('/request/<int:req_id>')
@login_required
def request_detail(req_id):
    req = ServiceRequest.query.get_or_404(req_id)

    # authorization: user who created, assigned mechanic, or admin can view
    if not (
        current_user.role == Role.ADMIN.value
        or current_user.id == req.user_id
        or current_user.id == req.assigned_mechanic_id
    ):
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    mechanic = User.query.get(req.assigned_mechanic_id) if req.assigned_mechanic_id else None
    return render_template('request_detail.html', req=req, mechanic=mechanic)


# ---------- ADMIN ----------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != Role.ADMIN.value:
        flash('Unauthorized','danger')
        return redirect(url_for('index'))

    pending = ServiceRequest.query.filter(ServiceRequest.assigned_mechanic_id==None).order_by(ServiceRequest.created_at.desc()).all()
    all_requests = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).limit(50).all()
    mechanics = User.query.filter_by(role=Role.MECHANIC.value).all()
    users = User.query.filter_by(role=Role.USER.value).all()
    return render_template('admin_dashboard.html', pending=pending, mechanics=mechanics, all_requests=all_requests, users=users)


@app.route("/admin/assign", methods=["POST"])
@login_required
def admin_assign():
    if current_user.role != Role.ADMIN.value:
        flash("Unauthorized", "danger")
        return redirect(url_for("index"))

    req_id = request.form.get("req_id")
    mech_id = request.form.get("mech_id")

    service_request = ServiceRequest.query.get_or_404(req_id)
    service_request.assigned_mechanic_id = int(mech_id)   # ✅ FIX HERE
    service_request.status = "pending"  # better than "assigned", since mechanic acts next
    db.session.commit()

    flash(f"Request #{service_request.id} assigned to mechanic.", "success")
    return redirect(url_for("admin_dashboard"))

# ---------- MECHANIC ----------
@app.route('/mechanic/dashboard')
@login_required
def mechanic_dashboard():
    if current_user.role != Role.MECHANIC.value:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))

    assigned = ServiceRequest.query.filter_by(assigned_mechanic_id=current_user.id).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('mechanic_dashboard.html', assigned=assigned)


@app.route("/mechanic/respond/<int:req_id>", methods=["POST"])
@login_required
def mechanic_respond(req_id):
    if current_user.role != Role.MECHANIC.value:
        flash("Unauthorized", "danger")
        return redirect(url_for("index"))

    req = ServiceRequest.query.get_or_404(req_id)
    if req.assigned_mechanic_id != current_user.id:
        flash("This request is not assigned to you.", "danger")
        return redirect(url_for("mechanic_dashboard"))

    action = request.form.get("action")
    comment = request.form.get("comment")

    if action == "accept":
        req.status = "accepted"
    elif action == "reject":
        req.status = "rejected"
        req.assigned_mechanic_id = None  # ✅ unassign mechanic
        flash(f"Request #{req.id} rejected. Admin can now reassign it.", "info")
    elif action == "start":
        req.status = "enroute"
    elif action == "complete":
        req.status = "completed"

    if comment:
        req.mechanic_response = comment

    db.session.commit()
    return redirect(url_for("mechanic_dashboard"))

# ---------- API ----------
@app.route('/api/mechanics')
def api_mechanics():
    mechanics = User.query.filter_by(role=Role.MECHANIC.value).all()
    out = []
    for m in mechanics:
        out.append({
            'id': m.id,
            'name': m.name,
            'lat': 28.7 + (m.id % 5) * 0.01,
            'lng': 77.1 + (m.id % 5) * 0.01,
            'phone': m.phone
        })
    return jsonify(out)


# ---------- MAIN ----------
if __name__ == '__main__':
    app.run(debug=True)

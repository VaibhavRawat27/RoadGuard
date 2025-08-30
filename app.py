import os, sqlite3, hashlib, secrets, json, time, csv, io, math, random
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file, jsonify, abort

APP_SECRET = os.environ.get("APP_SECRET", "dev-"+secrets.token_hex(16))

app = Flask(__name__)
app.config["SECRET_KEY"] = APP_SECRET
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "roadguard.db")

# --------- Database Helpers ---------
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        password_hash TEXT,
        role TEXT CHECK(role IN ('user','admin','worker')),
        verified INTEGER DEFAULT 0,
        otp TEXT,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS workshops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner_id INTEGER,
        description TEXT,
        latitude REAL,
        longitude REAL,
        status TEXT DEFAULT 'open',
        rating REAL DEFAULT 4.5,
        rating_count INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vehicle_info TEXT,
        service_type TEXT,
        photos TEXT,
        latitude REAL,
        longitude REAL,
        status TEXT DEFAULT 'submitted',
        assigned_worker_id INTEGER,
        workshop_id INTEGER,
        eta_minutes INTEGER,
        quoted_amount REAL,
        paid INTEGER DEFAULT 0,
        broadcasted INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        workshop_id INTEGER,
        request_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        audience TEXT,
        title TEXT,
        message TEXT,
        medium TEXT,
        created_at TEXT,
        read INTEGER DEFAULT 0
    )''')
    conn.commit()

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dlambda = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c

def ai_quote(service_type, dist):
    base = {"towing":1200,"battery":800,"puncture":300,"engine":2000,"diagnostic":500,"other":700}.get(service_type.lower(),700)
    return round(base*(1+min(dist/50.0,0.5)),2)

def notify(audience,title,message,user_id=None):
    conn=get_db();cur=conn.cursor()
    cur.execute("INSERT INTO notifications(user_id,audience,title,message,medium,created_at) VALUES(?,?,?,?,?,?)",
                (user_id,audience,title,message,"inapp",datetime.utcnow().isoformat()))
    conn.commit()

# --------- Auth Routes ---------
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"]; email=request.form["email"].lower(); phone=request.form["phone"]
        pwd=request.form["password"]; role=request.form.get("role","user")
        otp=str(random.randint(100000,999999))
        conn=get_db();cur=conn.cursor()
        try:
            cur.execute("INSERT INTO users(name,email,phone,password_hash,role,verified,otp,created_at) VALUES(?,?,?,?,?,0,?,?)",
                        (name,email,phone,hash_password(pwd),role,otp,datetime.utcnow().isoformat()))
            conn.commit()
            flash(f"OTP (simulated): {otp}","info"); session["pending_email"]=email
            return redirect(url_for("verify"))
        except sqlite3.IntegrityError: flash("Email/phone already used","danger")
    return render_template("register.html")

@app.route("/verify",methods=["GET","POST"])
def verify():
    email=session.get("pending_email")
    if not email: return redirect(url_for("login"))
    if request.method=="POST":
        otp=request.form["otp"]; conn=get_db();cur=conn.cursor()
        cur.execute("SELECT id,otp FROM users WHERE email=?",(email,));r=cur.fetchone()
        if r and r["otp"]==otp:
            cur.execute("UPDATE users SET verified=1,otp=NULL WHERE id=?",(r["id"],));conn.commit()
            flash("Verified! Please login","success"); return redirect(url_for("login"))
        else: flash("Wrong OTP","danger")
    return render_template("verify.html",email=email)

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"].lower(); pwd=request.form["password"]
        conn=get_db();cur=conn.cursor(); cur.execute("SELECT * FROM users WHERE email=?",(email,));u=cur.fetchone()
        if u and u["password_hash"]==hash_password(pwd) and u["verified"]:
            session["user_id"]=u["id"]; session["role"]=u["role"]
            return redirect(url_for(f"{u['role']}_dashboard"))
        flash("Invalid creds","danger")
    return render_template("login.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

# --------- Dashboards ---------
@app.route("/user")
def user_dashboard():
    if session.get("role")!="user": return abort(403)
    conn=get_db();cur=conn.cursor();cur.execute("SELECT * FROM workshops");workshops=cur.fetchall()
    return render_template("user_dashboard.html",workshops=workshops)

@app.route("/admin")
def admin_dashboard():
    if session.get("role")!="admin": return abort(403)
    conn=get_db();cur=conn.cursor();cur.execute("SELECT COUNT(*) c FROM requests");total=cur.fetchone()["c"]
    return render_template("admin_dashboard.html",total=total)

@app.route("/worker")
def worker_dashboard():
    if session.get("role")!="worker": return abort(403)
    return render_template("worker_dashboard.html")

# --------- Setup ---------
@app.before_first_request
def setup(): init_db()

if __name__=="__main__": app.run(debug=True)

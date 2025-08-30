from flask import Blueprint, request, session, jsonify
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

otp_bp = Blueprint('otp', __name__)

# Config: change these to your email credentials
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'rawatvaibhav27@gmail.com'
EMAIL_PASSWORD = 'xrwc dsid ggfh wgih'  # Use environment variables in production

# ----------------- Helper -----------------
def send_email(to_email, otp):
    """Send OTP to email."""
    subject = "Your OTP for RoadGuard Registration"
    body = f"Your OTP is: {otp}. Do not share it with anyone."
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [to_email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

# ----------------- Routes -----------------
@otp_bp.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json(force=True)
    email = data.get('email')
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    otp = f"{random.randint(100000, 999999)}"  # 6-digit OTP
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Store OTP in session
    otps = session.get('otps', {})
    otps[email] = {"otp": otp, "expires_at": expires_at.isoformat()}
    session['otps'] = otps
    session.modified = True  # Ensure session updates

    if send_email(email, otp):
        return jsonify({"success": True, "message": "OTP sent to your email"})
    else:
        return jsonify({"success": False, "message": "Failed to send OTP"})

@otp_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json(force=True)
    email = data.get('email')
    entered_otp = data.get('otp')

    if not email or not entered_otp:
        return jsonify({"success": False, "message": "Email and OTP required"}), 400

    otps = session.get('otps', {})
    otp_data = otps.get(email)

    if not otp_data:
        return jsonify({"success": False, "message": "No OTP found for this email"}), 400

    expires_at = datetime.fromisoformat(otp_data['expires_at'])
    if datetime.utcnow() > expires_at:
        otps.pop(email, None)
        session['otps'] = otps
        session.modified = True
        return jsonify({"success": False, "message": "OTP has expired"}), 400

    if otp_data['otp'] == str(entered_otp):
        otps.pop(email, None)
        session['otps'] = otps
        session.modified = True
        return jsonify({"success": True, "message": "OTP verified"})
    else:
        return jsonify({"success": False, "message": "Incorrect OTP"}), 400

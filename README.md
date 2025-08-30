# RoadGuard - Flask Roadside Assistance (Prototype)

Prototype Flask app with 3 roles: admin, user, mechanic.
Features:
- Register / Login with role selection (no SMS OTP implemented; placeholder)
- Users can raise service requests with location (uses Leaflet map)
- Admin can view pending requests and assign mechanics
- Mechanics see assigned requests, accept/reject, update status
- Simple SQLite database (Flask-SQLAlchemy)
- Map view using Leaflet + OpenStreetMap tiles (no API key required)

Notes & placeholders:
- OTP/SMS and payment gateway integrations are left as placeholders.
- For production, secure secret key, HTTPS, and proper user verification required.

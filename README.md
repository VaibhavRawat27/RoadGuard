# RoadGuard - Flask Roadside Assistance (Prototype)

Develop a smart, location-aware roadside assistance platform that connects stranded vehicle
owners with nearby mechanics or towing services in real time. The platform aims to reduce
response time, improve communication, and enhance the safety and reliability of breakdown
support, especially in remote or hazardous areas

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

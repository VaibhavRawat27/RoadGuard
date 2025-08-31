# RoadGuard — Flask Roadside Assistance

[View demo video](https://drive.google.com/drive/folders/1oRVjVz9Y09BMR4UBwB6HRafwexSLLNZH?usp=sharing)

> **RoadGuard** is a prototype location-aware roadside assistance platform built with Flask. It connects stranded vehicle owners to nearby mechanics or towing services in real time using a simple Leaflet/OpenStreetMap map view and a lightweight SQLite backend.

---

## Key idea

When a vehicle breaks down, a user can raise a service request with their current location. Admins assign available mechanics to requests. Mechanics can accept/reject and update request status. The platform is aimed at reducing response time, improving communication, and increasing safety for drivers in remote or hazardous areas.

---

## Target users

1. **Vehicle owners / Travelers** — people who may face unexpected breakdowns.
2. **Mechanic shop owners** — businesses that want to receive service requests.
3. **Mechanics / Employees** — individual technicians who fulfil assigned requests.

---

## Roles & demo accounts

- **Admin**
  - `admin@roadguard.local` / `admin`
- **User**
  - `vaibhavrwt27@gmail.com` / `123`
- **Mechanic**
  - `thestudiocityx@gmail.com` / `123`

> These are demo credentials in the prototype. Replace or remove before deploying.

---

## Features

- Register / Login with role selection (placeholder OTP flow — not implemented)
- Raise service requests with an interactive Leaflet map to pick location
- Admin dashboard to view pending requests and assign mechanics
- Mechanic dashboard to see assigned requests, accept/reject, and update status
- Simple status flow: **Pending → Assigned → Accepted → En Route → Completed / Cancelled**
- SQLite database using Flask-SQLAlchemy for easy local development
- Map view uses Leaflet + OpenStreetMap tiles (no API key required)

### Notes & placeholders
- OTP/SMS and payment gateway integrations are left as placeholders.
- Production deployment requires a secure `SECRET_KEY`, HTTPS, proper authentication, rate limiting, and audited third-party integrations.

---

## Screenshots


<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/2486b508-45fd-49c3-b3a5-fc3528ad539f" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/5dd44fc6-85ba-4059-8f6d-0bb10c7e7305" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/ed4eda97-82d5-4a24-8fdf-c60e58f4305f" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/e37038c5-92be-4598-92f1-ce79f0f78432" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/90576d5a-3c54-4993-9186-149e21b2ff4d" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/1db82075-64a2-46b9-a5f3-88c67caec74c" />

---

## Quick start (local development)

```bash
# 1. Clone the repo
git clone RoadGuard
cd RoadGuard

# 2. Create and activate a virtual environment (recommended)
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy/rename the example environment file and edit as needed
cp .env.example .env
# open .env and set SECRET_KEY and other values

# 5. Initialize the database
# (If the project provides a script or Flask-Migrate: use that. Otherwise the app will create sqlite file on first run.)
python app.py
# or
flask run

# 6. Open in your browser
# By default: http://127.0.0.1:5000
```

### Example `.env.example`

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=change-this-to-a-secure-random-value
DATABASE_URL=sqlite:///roadguard.db
```

---

## Project structure (example)

```
RoadGuard/
├─ app.py
├─ requirements.txt
├─ .env.example
├─ README.md
├─ templates/
├─ static/
│  ├─ css/
│  ├─ js/
│  └─ images/
├─ models.py
├─ extensions.py
└─ migrations/ (optional)
```

---

## Database

- Uses **SQLite** by default via Flask-SQLAlchemy for simplicity.
- Models exist for Users (with `role`), Requests (with location and status), and Assignments linking mechanics to requests.

If you want to switch to PostgreSQL or MySQL for production, set `DATABASE_URL` accordingly and run migrations.

---

## Mapping

- The map UI uses **Leaflet** with OpenStreetMap tiles. No API key is required.
- Users can pick their breakdown location by dropping a pin on the map — coordinates are saved to the request record.

---

## Admin workflow

1. Admin reviews **Pending** requests in the dashboard.
2. Admin assigns a mechanic (owner or employee) to a request.
3. Assigned mechanic receives the request in their dashboard.
4. Mechanic accepts or rejects and updates status through to **Completed**.

---

## Mechanic workflow

- See assigned requests, accept/reject, update status and add notes.
- Optionally update an ETA or mark the request as completed.

---

## Security & production considerations

- **SECRET_KEY**: replace the development secret with a secure random value.
- **HTTPS**: required for any production deployment, especially when handling credentials or payments.
- **User verification**: integrate real OTP/SMS flows with providers (Twilio, MessageBird, etc.) or use email verification.
- **Payment gateway**: if you add payments, integrate a secure provider and follow PCI compliance.
- **Environment**: use environment variables to store keys and credentials.
- **Database**: migrate from SQLite to a production-grade DB like PostgreSQL.
- **Logging & monitoring**: Sentry/Prometheus/Grafana as needed.

---

## Roadmap / Improvements

- Real OTP / SMS integration for phone verification
- Payment gateway for on-spot payments or advance deposits
- Real-time notifications (WebSockets / Firebase) for instant updates
- Geofencing and distance-based mechanic matching
- Ratings & reviews for mechanics
- Automated ETA calculation using routing APIs
- Admin analytics and reports (acceptance rate, average response time)

---

## License

This project is provided for educational and prototype use. Add a proper open-source license (MIT/Apache-2.0) if you plan to publish.

---

## Contact

If you'd like improvements, bug fixes, or help deploying, open an issue or contact the maintainer.

---

## Acknowledgement

I have used AI to build this project.

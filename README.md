# RoadGuard - Flask Roadside Assistance

View Video Here -> 

Develop a smart, location-aware roadside assistance platform that connects stranded vehicle
owners with nearby mechanics or towing services in real time. The platform aims to reduce
response time, improve communication, and enhance the safety and reliability of breakdown
support, especially in remote or hazardous areas

Target Users:
1. Vehicle Owners and Travelers: Individuals who drive personal or rental vehicles and may
face unexpected breakdowns.
2. Mechanics and Towing Service Providers (Owner of mechanic shop)
3. Mechanics or Employee of mechanic shop

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

## Snapshots:

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/2486b508-45fd-49c3-b3a5-fc3528ad539f" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/5dd44fc6-85ba-4059-8f6d-0bb10c7e7305" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/ed4eda97-82d5-4a24-8fdf-c60e58f4305f" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/e37038c5-92be-4598-92f1-ce79f0f78432" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/90576d5a-3c54-4993-9186-149e21b2ff4d" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/1db82075-64a2-46b9-a5f3-88c67caec74c" />

## Demo accounts:
admin@roadguard.local
admin

vaibhavrwt27@gmail.com
123

thestudiocityx@gmail.com
123

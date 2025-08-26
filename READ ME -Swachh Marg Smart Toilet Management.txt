 Swachh Marg: Smart Toilet Management System
📂 Folder Structure
SwachhMarg/
│
├── app.py                   # Flask backend (API endpoints & logic)
├── templates/ index.html    # Regional Dashboard (live monitoring UI)
               feedback.html  # Feedback submission portal (user input)             
├── static/ uploads         # the user feedback media will be save here    
         

 How to Run
1. Install Dependencies
Ensure you have Python 3.8+ and pip installed.
Install Flask and other required packages:


pip install flask


(If additional packages are required, they can be added into a requirements.txt file.)

2. Run the Backend Server
Start the Flask app:

python app.py


By default, it runs on:
 http://127.0.0.1:5000/

3. Open the Dashboards

Admin Dashboard (Monitoring):
Open index.html in a browser or via Flask route.
Shows:
 Real-time toilet sensor status (occupancy, odor, leaks, consumables)
 SLA compliance (cleanliness, consumables, response time)
 AI predictions for maintenance
 User feedback list

User Feedback Form:
Open feedback.html in a browser or via Flask route.
Allows public users to:
 Give rating (1–5 stars)
 Add comments/complaints
 Upload media (photo/video/voice note)
 Provide contact for follow-up

Submitted feedback automatically updates into the backend → visible in the dashboard.

 Operational Model

IoT Sensors → Backend:
Toilets have PIR, odor, soap, leak, and door sensors feeding into the backend via simulated or real devices.

Backend (Flask):

Exposes APIs:

/api/all_toilets → Live status for dashboard

/api/submit_feedback → Collects user feedback

Stores data (currently in-memory, can be extended to DB).

Frontend (HTML Dashboards):

index.html → Aggregates all toilet blocks into an accordion-style dashboard.

feedback.html → Simple form with rating, text, and media uploads.

 Key Features

24x7 monitoring of highway toilets.

SLA-linked AI decision-making (cleanliness, response time, consumables).

Real-time feedback collection from users.

Emergency button alerts with banner highlights.

Visual KPIs with PASS/FAIL indicators.


HOW TO USE:

Run backend (app.py).

Open index.html → Explore dashboards, SLA, AI predictions, user ratings.

Open feedback.html → Submit a test feedback → Confirm it appears in dashboard.

Check emergency simulation (toggle from JSON or code).

from flask import Flask, render_template, jsonify, request
import datetime
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- File Upload Config ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Feedback storage ---
FEEDBACK_DATABASE = [
    {"toilet_id": "NH44-A", "rating": 5, "comment": "Initial feedback: Very clean!", "media": "None", "contact": "demo@example.com"}
]

# --- Expanded Data Simulation ---
STAFF_ROSTER = {
    "Shift 1 (6AM-2PM)": {"cleaning": ["Karthik R.", "Priya M."], "security": "Muthu Pandi (M)"},
    "Shift 2 (2PM-10PM)": {"cleaning": ["Arun Kumar", "Lakshmi S."], "security": "Anitha Selvam (F)"},
    "Shift 3 (10PM-6AM)": {"cleaning": ["Anandan V.", "Sarala B."], "security": "Bala Murugan (M)"}
}
DISTRICT_DATA = {
    "Chennai Zone": [
        {"id": "NH44-A", "name": "Chennai Bypass"}, {"id": "NH32-B", "name": "ECR Toll Plaza"},
        {"id": "NH48-C", "name": "Sriperumbudur Hub"}, {"id": "NH75-B", "name": "Tindivanam Stretch"}
    ],
    "Coimbatore Zone": [
        {"id": "NH544-D", "name": "Coimbatore Gateway"}, {"id": "NH83-E", "name": "Tiruppur Hub"},
        {"id": "NH381-A", "name": "Avinashi-Tiruppur Road"}
    ],
    "Madurai Zone": [
        {"id": "NH85-F", "name": "Madurai Ring Road"}, {"id": "NH383-G", "name": "Dindigul-Natham Road"},
        {"id": "NH87-H", "name": "Rameswaram Link"}
    ]
}

def generate_status_and_tickets(sensors, occupancy_duration):
    tickets = []
    if sensors.get('emergency_button_pressed'): tickets.append('CRITICAL: EMERGENCY PRESSED')
    if occupancy_duration > 15: tickets.append('CRITICAL: Long Occupancy Alert')
    if sensors['door_status'] == 'LOCKED': tickets.append('ATTENTION: Door Locked')
    if sensors['water_leak_detected']: tickets.append('ATTENTION: Water Leak')
    status = "HEALTHY"
    reason = "All systems operational."
    if tickets:
        status = "CRITICAL" if any('CRITICAL' in t for t in tickets) else "ATTENTION"
        reason = " | ".join(tickets)
    return {"status": status, "reason": reason}

def generate_section_data():
    is_occupied = random.choice([True, False])
    occupancy_duration = random.randint(5, 20) if is_occupied else 0
    sensors = {
        "occupancy_status": "OCCUPIED" if is_occupied else "VACANT",
        "occupancy_duration_mins": occupancy_duration,
        "door_status": "OPEN", "footfall_count": random.randint(30, 150),
        "ammonia_ppm": round(random.uniform(1.0, 7.5), 1),
        "soap_level_percent": random.randint(10, 95), "paper_level_percent": random.randint(10, 95),
        "water_leak_detected": random.choice([True, False, False, False]),
        "emergency_button_pressed": random.choice([True, False, False, False, False])
    }
    decision = generate_status_and_tickets(sensors, occupancy_duration)
    return {"sensors": sensors, "decision": decision}

def generate_toilet_block_data(toilet_id, location_info):
    gents_data = generate_section_data()
    ladies_data = generate_section_data()
    block_status = "HEALTHY"
    if "CRITICAL" in [gents_data['decision']['status'], ladies_data['decision']['status']]: block_status = "CRITICAL"
    elif "ATTENTION" in [gents_data['decision']['status'], ladies_data['decision']['status']]: block_status = "ATTENTION"
    user_rating = round(random.uniform(2.5, 5.0), 1)
    sensor_score = int(100 - (gents_data['sensors']['ammonia_ppm'] + ladies_data['sensors']['ammonia_ppm']) * 5)
    final_cleanliness_score = int((sensor_score * 0.7) + ((user_rating / 5) * 100 * 0.3))
    relevant_feedback = [fb for fb in reversed(FEEDBACK_DATABASE) if fb['toilet_id'] == toilet_id][:3]
    return {
        "id": toilet_id, "location_name": location_info["name"], "block_status": block_status,
        "gents": gents_data, "ladies": ladies_data,
        "operations": {
            "staff_roster": STAFF_ROSTER,
            "last_cleaned_time": (datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 4))).strftime('%I:%M %p, %d-%b-%Y'),
            "user_feedbacks": relevant_feedback
        },
        "resources": {
            "water_used_liters": random.randint(1500, 3000),
            "solar_energy_generated_kwh": round(random.uniform(5, 25), 1),
            "energy_consumed_kwh": round(random.uniform(4, 15), 1)
        },
        "sla_status": {
            "cleanliness_score": max(50, final_cleanliness_score),
            "consumables_availability": min(gents_data['sensors']['soap_level_percent'], ladies_data['sensors']['paper_level_percent']),
            "response_time_mins": random.randint(15, 45) if block_status != "HEALTHY" else 0
        },
        "overall_rating": user_rating,
        "ai_predictions": [
            f"Flush System Health: {random.randint(85,99)}% (Check in {random.randint(5,10)} days)",
            f"Solar Panel Efficiency: {random.randint(90,99)}% (Clean in {random.randint(10,20)} days)"
        ],
        "geofence_logs": [
            f"{ (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(5, 20))).strftime('%I:%M %p') }: Alert sent to {random.randint(5,20)} vehicles in 2km radius.",
            f"{ (datetime.datetime.now() - datetime.timedelta(minutes=random.randint(25, 50))).strftime('%I:%M %p') }: Alert sent to {random.randint(5,20)} vehicles in 2km radius."
        ]
    }

@app.route('/api/all_toilets')
def get_all_toilets():
    all_data = {}
    for district, locations in DISTRICT_DATA.items():
        all_data[district] = [generate_toilet_block_data(loc["id"], loc) for loc in locations]
    return jsonify(all_data)

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    toilet_id = request.form.get('toilet_id')
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment', 'No comment provided.')
    contact = request.form.get('contact')
    media_file = request.files.get('media_file')
    media_url = "None"
    if media_file and allowed_file(media_file.filename):
        filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{media_file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        media_file.save(filepath)
        media_url = f"/{filepath}"
    new_feedback = {
        "toilet_id": toilet_id, "rating": rating, "comment": comment,
        "contact": contact, "media": media_url,
        "timestamp": datetime.datetime.now().strftime('%I:%M %p, %d-%b')
    }
    FEEDBACK_DATABASE.append(new_feedback)
    return jsonify({"status": "success", "message": "Feedback submitted!"})

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/feedback')
def feedback_page():
    flat_locations = {}
    for district, locs in DISTRICT_DATA.items():
        for loc in locs:
            flat_locations[loc["id"]] = {"name": loc["name"]}
    return render_template('feedback.html', locations=flat_locations)

if __name__ == '__main__':
    app.run(debug=True)

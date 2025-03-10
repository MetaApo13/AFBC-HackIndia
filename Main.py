from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dateutil import parser
import re
from hyperon import MeTTa  # Import Hyperon's MeTTa

app = Flask(__name__)
CORS(app)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize MeTTa
metta = MeTTa()


metta.run(r"""
    ;; Rule to process an NLP-based task input
    (rule (process-nlp-task $text)
        (extract-details $text ?title ?date ?time)
        (Task ?title "" ?date ?time none pending)
    )

    ;; Function to extract details from text
    (func (extract-details $text ?title ?date ?time)
        (let (?title (extract-title $text))
             (?date (extract-date $text))
             (?time (extract-time $text))
             (if (and ?title ?date ?time)
                 (return ?title ?date ?time)
                 (error "Invalid task input"))
        )
    )

    ;; Helper functions to extract specific components
    (func (extract-title $text)
        (regex-replace $text "(Remind me to | by \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})" "")
    )

    (func (extract-date $text)
        (regex-match $text "\\b\\d{4}-\\d{2}-\\d{2}\\b")
    )

    (func (extract-time $text)
        (regex-match $text "\\b\\d{2}:\\d{2}:\\d{2}\\b")
    )
""") # metta rule to process NLP-based task input

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default="none")  # none, low, medium, high
    status = db.Column(db.String(20), default="pending")  # pending, completed

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "date": self.date.isoformat(),
            "time": self.time.isoformat(),
            "priority": self.priority,
            "status": self.status
        }

# Priority Mapping
priority_order = {"high": 1, "medium": 2, "low": 3, "none": 4}

# Function to extract details using regex
def extract_task_details(text):
    date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', text)
    time_match = re.search(r'\b\d{2}:\d{2}:\d{2}\b', text)
    date = parser.parse(date_match.group()).date() if date_match else None
    time = parser.parse(time_match.group()).time() if time_match else None
    title = re.sub(r'Remind me to | by \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', text).strip()
    return title, date, time

# Get tasks sorted by priority > deadline
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    sorted_tasks = sorted(tasks, key=lambda task: (priority_order[task.priority], task.date, task.time))
    return jsonify([task.to_dict() for task in sorted_tasks])

# Create a task via NLP
@app.route("/tasks/nlp", methods=["POST"])
def process_natural_language_task():
    data = request.json
    user_input = data.get("text")
    description = data.get("description", None)
    priority = data.get("priority", "none")
    
    if priority not in priority_order:
        return jsonify({"error": "Invalid priority"}), 400
    
    title, date, time = extract_task_details(user_input)
    if not title:
        return jsonify({"error": "Title cannot be empty"}), 400
    if not date or not time:
        return jsonify({"error": "Invalid date or time format"}), 400
    if datetime.combine(date, time) < datetime.utcnow():
        return jsonify({"error": "Deadline must be in the future"}), 400
    
    new_task = Task(title=title, description=description, date=date, time=time, priority=priority)
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# Create a task manually
@app.route("/tasks/manual", methods=["POST"])
def create_manual_task():
    data = request.json
    title = data.get("title")
    description = data.get("description", "")
    date = data.get("date")
    time = data.get("time")
    priority = data.get("priority", "none")

    if not title or not date or not time:
        return jsonify({"error": "Title, date, and time are required"}), 400
    if priority not in priority_order:
        return jsonify({"error": "Invalid priority"}), 400

    try:
        date_obj = parser.parse(date).date()
        time_obj = parser.parse(time).time()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    if datetime.combine(date_obj, time_obj) < datetime.utcnow():
        return jsonify({"error": "Deadline must be in the future"}), 400

    new_task = Task(title=title, description=description, date=date_obj, time=time_obj, priority=priority)
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# Update a task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "date" in data:
        task.date = parser.parse(data["date"]).date()
    if "time" in data:
        task.time = parser.parse(data["time"]).time()
    if "priority" in data and data["priority"] in priority_order:
        task.priority = data["priority"]
    
    db.session.commit()
    return jsonify(task.to_dict())

# Delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200

# Mark task as done
@app.route("/tasks/<int:task_id>/done", methods=["PATCH"])
def mark_task_done(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task.status = "completed"
    db.session.commit()
    return jsonify(task.to_dict())

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)

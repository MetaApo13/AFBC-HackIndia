from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_apscheduler import APScheduler
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from hyperon import Metta
import pytz

app = Flask(__name__)
CORS(app)

metta =Metta()
# Database Config (Use SQLite or PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mail Config
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'
mail = Mail(app)

# APScheduler Setup
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # low, medium, high
    status = db.Column(db.String(20), default="pending")  # pending, completed, expired

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "deadline": self.deadline.isoformat(),
            "priority": self.priority,
            "status": self.status
        }

# Check Deadlines Function
def check_deadlines():
    with app.app_context():
        now = datetime.now(pytz.utc)
        tasks = Task.query.filter(Task.deadline <= now, Task.status == "pending").all()
        for task in tasks:
            task.status = "expired"
            send_notification(task)
        db.session.commit()

# Send Notification Function
def send_notification(task):
    msg = Message(
        subject="Task Overdue Notification",
        recipients=["recipient@example.com"],  # Replace with actual recipient
        body=f"Task '{task.title}' is overdue!\n\nDescription: {task.description}\nDeadline: {task.deadline}\nPriority: {task.priority}"
    )
    mail.send(msg)

scheduler.add_job(id="check_deadlines", func=check_deadlines, trigger="interval", minutes=1)

# Routes
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    # Sort tasks by priority and deadline
    priority_order = {"high": 1, "medium": 2, "low": 3}
    tasks.sort(key=lambda t: (priority_order[t.priority], t.deadline))
    return jsonify([task.to_dict() for task in tasks])

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),
        deadline=datetime.fromisoformat(data["deadline"]),
        priority=data["priority"]
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.json
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.deadline = datetime.fromisoformat(data["deadline"]) if "deadline" in data else task.deadline
    task.priority = data.get("priority", task.priority)
    task.status = data.get("status", task.status)
    db.session.commit()
    return jsonify(task.to_dict())

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database is created
    app.run(debug=True)

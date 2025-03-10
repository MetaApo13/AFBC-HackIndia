# Task Management API with NLP and MeTTa Integration

## 📌 Objective
This project is a **Flask-based Task Management API** that supports:

### Setting Up a Virtual Environment
Before installing dependencies, it's recommended to create a virtual environment. Run the following commands:

```sh
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

Once the virtual environment is activated, proceed with the dependency installation.
- **Natural Language Processing (NLP) for Task Creation** using regex and MeTTa.
- **Manual Task Creation** via API.
- **Task Sorting** based on **priority and deadline**.
- **Task Update, Completion, and Deletion**.

Although **MeTTa** is included, it is currently **not fully utilized** in processing tasks, but the groundwork is laid for integrating symbolic AI and rule-based reasoning.

---

## ⚡ What is MeTTa?
**MeTTa** (Meta Thought Architect) is a **symbolic AI language** developed by **Hyperon**. It enables pattern matching, rule-based transformations, and reasoning. In this project, MeTTa is used to **define NLP-based task extraction rules**.

Example MeTTa rule used in this project:
```metta
(rule (process-nlp-task $text)
    (extract-details $text ?title ?date ?time)
    (Task ?title "" ?date ?time none pending)
)
```
This helps extract **title, date, and time** from natural language task inputs.

---

## Prerequisites
Ensure you have Python installed. Depending on your system, you may use:
```sh
python3 --version  # For Linux/macOS
python --version   # For Windows
```

## 🚀 Running the Project Locally



### 1️⃣ Install Dependencies
 run:
```sh
pip install flask flask_sqlalchemy flask_cors python-dateutil hyperon
```

### 2️⃣ Run the Flask Server
```sh
python Main.py
```
The server will start on `http://127.0.0.1:5001/`

---

## 🛠️ API Endpoints

### 🔹 Get All Tasks (Sorted by Priority & Deadline)
**Endpoint:** `GET /tasks`
```sh
curl -X GET http://127.0.0.1:5001/tasks
```

### 🔹 Create a Task via NLP
**Endpoint:** `POST /tasks/nlp`
**Request Body:**
```json
{
    "text": "Remind me to submit report by 2025-03-12 14:00:00",
    "priority": "high"
}
```
**Test with cURL:**
```sh
curl -X POST http://127.0.0.1:5001/tasks/nlp \
     -H "Content-Type: application/json" \
     -d '{"text": "Remind me to submit report by 2025-03-12 14:00:00", "priority": "high"}'
```

### 🔹 Create a Task Manually
**Endpoint:** `POST /tasks/manual`
```json
{
    "title": "Prepare slides",
    "description": "For the Monday meeting",
    "date": "2025-03-10",
    "time": "09:00:00",
    "priority": "medium"
}
```

### 🔹 Update a Task
**Endpoint:** `PUT /tasks/{task_id}`
```json
{
    "title": "Updated Task Title",
    "priority": "low"
}
```

### 🔹 Delete a Task
**Endpoint:** `DELETE /tasks/{task_id}`
```sh
curl -X DELETE http://127.0.0.1:5001/tasks/1
```

### 🔹 Mark a Task as Completed
**Endpoint:** `PATCH /tasks/{task_id}/done`
```sh
curl -X PATCH http://127.0.0.1:5001/tasks/1/done
```

---

## 🏁 Next Steps
- **Enhance NLP Processing** using **MeTTa** instead of regex.
- **Build a Frontend** for easy task management.
- **Deploy the API** using Docker & Cloud Services.

---

✅ **Now, you can manage tasks efficiently using NLP-powered automation!** 🚀


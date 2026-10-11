# 🎓 SmartSched

### Machine Learning-Based Academic Task Scheduling System for College Students

SmartSched is an intelligent academic scheduling system designed to help college students organize assignments, exam preparation, practicals, projects, notes, presentations, and other academic tasks.

The system combines **Machine Learning** with deadline-aware scheduling logic to predict productive study periods and automatically generate a personalized academic schedule.

---

## ✨ Features

- 📅 Deadline-aware task scheduling
- 🤖 Machine Learning-based productivity prediction
- 🚨 Automatic urgency calculation
- ✂️ Long-task splitting into study sessions
- 🗓️ Multi-day academic scheduling
- ⏰ Student availability handling
- 🔀 Conflict-free time-slot selection
- 📊 Productivity score prediction
- 📈 Progress-aware remaining-work calculation
- 🌐 Web-based user interface

---

## 🧠 Machine Learning

SmartSched uses a **Random Forest Regressor** to predict a productivity score for candidate study periods.

### Model Inputs

- Task Category
- Subject
- Day of Week
- Start Hour
- Duration
- Difficulty
- Importance
- Hours Until Deadline

### Target

`productivity_score`

The predicted productivity score helps SmartSched select suitable study periods while the scheduling engine also considers deadlines, urgency, availability, and conflicts.

> **Note:** The current version uses a small synthetic dataset for prototype and academic demonstration purposes. Future versions can learn from real student productivity history for more personalized recommendations.

---

## ⚙️ How SmartSched Works

```text
Student Adds Academic Task
            ↓
Deadline & Remaining Work Analysis
            ↓
Urgency Calculation
            ↓
Long Task Splitting
            ↓
Available Time Slot Generation
            ↓
ML Productivity Prediction
            ↓
Deadline & Conflict Checking
            ↓
Best Time Slot Selection
            ↓
Personalized Weekly Schedule
```

---

## 🛠️ Tech Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Random Forest Regressor
- Joblib
- Flask
- HTML
- CSS
- JavaScript

---

## 📁 Project Structure

```text
SmartSched/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   └── student_tasks.csv
│
├── models/
│   └── smartsched_model.pkl
│
├── src/
│   ├── load_data.py
│   ├── preprocess.py
│   ├── train_model.py
│   ├── predict_best_time.py
│   ├── urgency.py
│   ├── deadline_utils.py
│   ├── task_splitter.py
│   ├── multiday_scheduler.py
│   └── smartsched_engine.py
│
└── static/
    ├── index.html
    └── style.css
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kaneezfatima28/SmartSched-ML.git
cd SmartSched-ML
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🤖 Train the ML Model

```bash
python src/train_model.py
```

The trained model is saved as:

```text
models/smartsched_model.pkl
```

---

## ▶️ Run SmartSched

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 📸 Screenshots

### Dashboard

Add your SmartSched dashboard screenshot here.

### Add Academic Task

Add your task-input screenshot here.

### Generated Smart Schedule

Add your final generated schedule screenshot here.

---

## 🔮 Future Improvements

- Collect real student productivity data
- Personalized model retraining
- User authentication
- Database integration
- Calendar integration
- Notifications and reminders
- Mobile application
- Improved productivity analytics
- Adaptive study and break recommendations

---

## 📌 Project Status

**Prototype / Academic Project**

SmartSched demonstrates how Machine Learning can be combined with scheduling algorithms to create a more personalized academic task-management system.

---

## 👨‍💻 Developer

Developed as a Machine Learning academic project.

---

⭐ If you find SmartSched useful, consider starring the repository!
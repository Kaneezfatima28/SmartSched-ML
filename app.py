# ============================================================
# SMARTSCHED WEB APPLICATION
# Flask Backend + Existing ML Scheduling Engine
# ============================================================

import sys
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, request


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
STATIC_DIR = ROOT_DIR / "static"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# IMPORT SMARTSCHED ENGINE
# ============================================================

from smartsched_engine import create_schedule


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    static_url_path="/static"
)


# ============================================================
# TEMPORARY TASK STORAGE
# ============================================================
# For now tasks are stored in memory.
# Restarting Flask will clear them.
# We can add SQLite later.

tasks = []


# ============================================================
# ALLOWED VALUES
# ============================================================

ALLOWED_CATEGORIES = {
    "Assignment",
    "Exam Study",
    "Practical",
    "Project",
    "Notes",
    "Revision",
    "Quiz Study",
    "Presentation",
    "Submission"
}

ALLOWED_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard"
}

ALLOWED_IMPORTANCE = {
    "Low",
    "Medium",
    "High"
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def serialize_task(task):
    """
    Convert Python task data into JSON-friendly data.
    """

    return {
        "name": task["name"],
        "task_category": task["task_category"],
        "subject": task["subject"],
        "deadline": task["deadline"].isoformat(),
        "duration": int(task["duration"]),
        "difficulty": task["difficulty"],
        "importance": task["importance"],
        "progress": int(task["progress"])
    }


def serialize_schedule_item(item):
    """
    Convert generated schedule data into JSON-friendly data.
    """

    return {
        "name": item["name"],
        "subject": item["subject"],
        "category": item["category"],

        "start": item["start"].isoformat(),
        "end": item["end"].isoformat(),

        "duration": int(item["duration"]),

        "urgency": int(item["urgency"]),
        "urgency_level": item["urgency_level"],

        "productivity": float(item["productivity"]),

        "deadline": item["deadline"].isoformat(),

        "session_number": int(
            item.get("session_number", 1)
        ),

        "total_sessions": int(
            item.get("total_sessions", 1)
        )
    }


def serialize_unscheduled_item(item):
    """
    Convert unscheduled work into JSON-friendly data.
    """

    deadline = item.get("deadline")

    if isinstance(deadline, datetime):
        deadline = deadline.isoformat()

    return {
        "name": item.get(
            "name",
            "Unknown Task"
        ),

        "session_duration": int(
            item.get(
                "session_duration",
                0
            )
        ),

        "deadline": deadline
    }


def renumber_sessions(schedule):
    """
    Fix session numbering AFTER the ML scheduler has chosen
    actual dates/times.

    Example:
        Monday    -> Session 1/4
        Tuesday   -> Session 2/4
        Wednesday -> Session 3/4
        Thursday  -> Session 4/4
    """

    sorted_schedule = sorted(
        schedule,
        key=lambda item: item["start"]
    )

    counters = {}

    for item in sorted_schedule:

        total_sessions = int(
            item.get(
                "total_sessions",
                1
            )
        )

        if total_sessions <= 1:
            item["session_number"] = 1
            continue

        # Use multiple fields so tasks with the same name
        # but different subjects are not mixed together.
        task_key = (
            item.get("name"),
            item.get("subject"),
            item.get("deadline")
        )

        counters[task_key] = (
            counters.get(task_key, 0) + 1
        )

        item["session_number"] = (
            counters[task_key]
        )

    return sorted_schedule


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    """
    Serve static/index.html
    """

    return app.send_static_file(
        "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health_check():

    return jsonify({
        "status": "ok",
        "application": "SmartSched",
        "message": "SmartSched backend is running."
    })


# ============================================================
# GET ALL TASKS
# ============================================================

@app.route("/api/tasks", methods=["GET"])
def get_tasks():

    return jsonify({
        "tasks": [
            serialize_task(task)
            for task in tasks
        ]
    })


# ============================================================
# ADD TASK
# ============================================================

@app.route("/api/tasks", methods=["POST"])
def add_task():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "error": "Task data is required."
            }), 400


        # ----------------------------------------------------
        # TASK NAME
        # ----------------------------------------------------

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()

        if not name:

            return jsonify({
                "error": "Task name is required."
            }), 400


        # ----------------------------------------------------
        # SUBJECT
        # ----------------------------------------------------

        subject = str(
            data.get(
                "subject",
                ""
            )
        ).strip()

        if not subject:

            return jsonify({
                "error": "Subject is required."
            }), 400


        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        task_category = data.get(
            "task_category",
            "Assignment"
        )

        if task_category not in ALLOWED_CATEGORIES:

            return jsonify({
                "error": "Invalid task category."
            }), 400


        # ----------------------------------------------------
        # DEADLINE
        # ----------------------------------------------------

        deadline_date = data.get(
            "deadline_date"
        )

        deadline_time = data.get(
            "deadline_time"
        )

        if not deadline_date:

            return jsonify({
                "error": "Deadline date is required."
            }), 400

        if not deadline_time:

            return jsonify({
                "error": "Deadline time is required."
            }), 400


        try:

            deadline = datetime.strptime(
                f"{deadline_date} {deadline_time}",
                "%Y-%m-%d %H:%M"
            )

        except ValueError:

            return jsonify({
                "error":
                    "Invalid deadline date or time."
            }), 400


        if deadline <= datetime.now():

            return jsonify({
                "error":
                    "Deadline must be in the future."
            }), 400


        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

        try:

            duration = int(
                data.get(
                    "duration",
                    120
                )
            )

        except (TypeError, ValueError):

            return jsonify({
                "error":
                    "Duration must be a number."
            }), 400


        if duration < 30:

            return jsonify({
                "error":
                    "Duration must be at least 30 minutes."
            }), 400


        if duration > 1200:

            return jsonify({
                "error":
                    "Duration cannot exceed 1200 minutes."
            }), 400


        # ----------------------------------------------------
        # DIFFICULTY
        # ----------------------------------------------------

        difficulty = data.get(
            "difficulty",
            "Medium"
        )

        if difficulty not in ALLOWED_DIFFICULTIES:

            return jsonify({
                "error":
                    "Invalid difficulty."
            }), 400


        # ----------------------------------------------------
        # IMPORTANCE
        # ----------------------------------------------------

        importance = data.get(
            "importance",
            "Medium"
        )

        if importance not in ALLOWED_IMPORTANCE:

            return jsonify({
                "error":
                    "Invalid importance."
            }), 400


        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        try:

            progress = int(
                data.get(
                    "progress",
                    0
                )
            )

        except (TypeError, ValueError):

            progress = 0


        progress = max(
            0,
            min(
                progress,
                100
            )
        )


        # ----------------------------------------------------
        # CREATE TASK
        # ----------------------------------------------------

        new_task = {
            "name": name,
            "task_category": task_category,
            "subject": subject,
            "deadline": deadline,
            "duration": duration,
            "difficulty": difficulty,
            "importance": importance,
            "progress": progress
        }


        tasks.append(
            new_task
        )


        return jsonify({
            "message":
                "Task added successfully.",

            "task":
                serialize_task(
                    new_task
                ),

            "tasks": [
                serialize_task(task)
                for task in tasks
            ]
        }), 201


    except Exception as error:

        print(
            "ERROR WHILE ADDING TASK:",
            error
        )

        return jsonify({
            "error":
                f"Unable to add task: {str(error)}"
        }), 500


# ============================================================
# DELETE TASK
# ============================================================

@app.route(
    "/api/tasks/<int:index>",
    methods=["DELETE"]
)
def delete_task(index):

    if (
        index < 0
        or index >= len(tasks)
    ):

        return jsonify({
            "error":
                "Task not found."
        }), 404


    removed_task = tasks.pop(
        index
    )


    return jsonify({
        "message":
            f"{removed_task['name']} removed.",

        "tasks": [
            serialize_task(task)
            for task in tasks
        ]
    })


# ============================================================
# CLEAR ALL TASKS
# ============================================================

@app.route(
    "/api/tasks",
    methods=["DELETE"]
)
def clear_tasks():

    tasks.clear()

    return jsonify({
        "message":
            "All tasks cleared.",

        "tasks": []
    })


# ============================================================
# GENERATE SMART SCHEDULE
# ============================================================

@app.route(
    "/api/generate",
    methods=["POST"]
)
def generate_schedule():

    if not tasks:

        return jsonify({
            "error":
                "Add at least one academic task first."
        }), 400


    try:

        current_time = datetime.now()


        # ----------------------------------------------------
        # CALL EXISTING SMARTSCHED ENGINE
        # ----------------------------------------------------

        schedule, unscheduled = (
            create_schedule(
                tasks,
                current_time
            )
        )


        # ----------------------------------------------------
        # CHRONOLOGICAL SESSION NUMBERS
        # ----------------------------------------------------

        schedule = renumber_sessions(
            schedule
        )


        # ----------------------------------------------------
        # SERIALIZE RESULTS
        # ----------------------------------------------------

        serialized_schedule = [
            serialize_schedule_item(item)
            for item in schedule
        ]


        serialized_unscheduled = [
            serialize_unscheduled_item(item)
            for item in unscheduled
        ]


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        total_sessions = len(
            serialized_schedule
        )


        total_minutes = sum(
            item["duration"]
            for item in serialized_schedule
        )


        if total_sessions > 0:

            average_productivity = sum(
                item["productivity"]
                for item in serialized_schedule
            ) / total_sessions

        else:

            average_productivity = 0


        critical_sessions = sum(
            1
            for item in serialized_schedule
            if item["urgency_level"]
            == "CRITICAL"
        )


        return jsonify({
            "message":
                "Smart schedule generated successfully.",

            "generated_at":
                current_time.isoformat(),

            "schedule":
                serialized_schedule,

            "unscheduled":
                serialized_unscheduled,

            "summary": {
                "total_sessions":
                    total_sessions,

                "total_minutes":
                    total_minutes,

                "total_hours":
                    round(
                        total_minutes / 60,
                        2
                    ),

                "average_productivity":
                    round(
                        average_productivity,
                        2
                    ),

                "critical_sessions":
                    critical_sessions,

                "unscheduled_sessions":
                    len(
                        serialized_unscheduled
                    )
            }
        })


    except Exception as error:

        print(
            "ERROR WHILE GENERATING SCHEDULE:",
            error
        )

        return jsonify({
            "error":
                "Unable to generate schedule.",

            "details":
                str(error)
        }), 500


# ============================================================
# 404 HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({
        "error":
            "Route not found."
    }), 404


# ============================================================
# START SMARTSCHED
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("SMARTSCHED WEB APPLICATION")
    print("=" * 60)
    print()
    print("Open this address in your browser:")
    print()
    print("http://127.0.0.1:5000")
    print()
    print("=" * 60)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
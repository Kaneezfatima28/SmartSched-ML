# ============================================================
# SMARTSCHED
# ML-Based Academic Task Scheduling System
# ============================================================

import sys
from pathlib import Path
from datetime import datetime, timedelta

import joblib
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from urgency import calculate_urgency, get_urgency_level
from deadline_utils import calculate_remaining_duration
from task_splitter import split_task_into_sessions


# ============================================================
# 1. LOAD ML MODEL
# ============================================================

MODEL_PATH = "models/smartsched_model.pkl"

model = joblib.load(MODEL_PATH)


# ============================================================
# 2. STUDENT AVAILABILITY
# ============================================================

WEEKDAY_AVAILABILITY = [
    ("06:00", "09:00"),
    ("16:00", "23:00")
]

WEEKEND_AVAILABILITY = [
    ("07:00", "12:00"),
    ("14:00", "23:00")
]


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def time_to_minutes(time_string):

    hour, minute = map(
        int,
        time_string.split(":")
    )

    return hour * 60 + minute


def get_availability(day_name):

    if day_name in ["Saturday", "Sunday"]:
        return WEEKEND_AVAILABILITY

    return WEEKDAY_AVAILABILITY


# ============================================================
# 4. GENERATE AVAILABLE 30-MINUTE SLOTS
# ============================================================

def generate_slots(current_time, end_date):

    slots = []

    current_date = current_time.date()

    while current_date <= end_date.date():

        day_name = current_date.strftime("%A")

        periods = get_availability(day_name)

        for start_time, end_time in periods:

            start_minutes = time_to_minutes(start_time)
            end_minutes = time_to_minutes(end_time)

            current_minutes = start_minutes

            while current_minutes < end_minutes:

                slot = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    current_minutes // 60,
                    current_minutes % 60
                )

                # Ignore past time
                if slot >= current_time:
                    slots.append(slot)

                current_minutes += 30

        current_date += timedelta(days=1)

    return slots


# ============================================================
# 5. ML PRODUCTIVITY PREDICTION
# ============================================================

def predict_productivity(task, slot):

    start_hour = (
        slot.hour
        + slot.minute / 60
    )

    hours_until_deadline = max(
        0,
        (
            task["deadline"] - slot
        ).total_seconds() / 3600
    )

    task_data = pd.DataFrame([{

        "task_category":
            task["task_category"],

        "subject":
            task["subject"],

        "day_of_week":
            slot.strftime("%A"),

        "start_hour":
            start_hour,

        "duration":
            task["session_duration"],

        "difficulty":
            task["difficulty"],

        "importance":
            task["importance"],

        "hours_until_deadline":
            hours_until_deadline
    }])

    prediction = model.predict(
        task_data
    )[0]

    return float(prediction)


# ============================================================
# 6. CHECK WHETHER SESSION FITS
# ============================================================

def session_fits(
    start_slot,
    duration,
    available_slot_set,
    occupied_slots,
    deadline
):

    slots_needed = (
        duration + 29
    ) // 30

    required_slots = []

    for i in range(slots_needed):

        slot = (
            start_slot
            + timedelta(minutes=i * 30)
        )

        # Must be inside student availability
        if slot not in available_slot_set:
            return None

        # Cannot overlap another task
        if slot in occupied_slots:
            return None

        # Must finish before deadline
        if (
            slot + timedelta(minutes=30)
            > deadline
        ):
            return None

        required_slots.append(slot)

    return required_slots


# ============================================================
# 7. PREPARE TASKS
# ============================================================

def prepare_tasks(tasks, current_time):

    prepared_sessions = []

    for task in tasks:

        # ----------------------------------------------------
        # Remaining work
        # ----------------------------------------------------

        remaining_minutes = (
            calculate_remaining_duration(
                task["duration"],
                task["progress"]
            )
        )

        if remaining_minutes <= 0:
            continue


        # ----------------------------------------------------
        # Deadline
        # ----------------------------------------------------

        hours_until_deadline = (
            task["deadline"]
            - current_time
        ).total_seconds() / 3600

        if hours_until_deadline <= 0:

            print(
                f"WARNING: Deadline already passed "
                f"for {task['name']}"
            )

            continue


        # ----------------------------------------------------
        # Urgency
        # ----------------------------------------------------

        urgency_score = calculate_urgency(
            hours_until_deadline,
            remaining_minutes,
            task["difficulty"],
            task["importance"],
            0
        )

        urgency_level = get_urgency_level(
            urgency_score
        )


        # ----------------------------------------------------
        # Categories that can be split
        # ----------------------------------------------------

        splittable_categories = [
            "Exam Study",
            "Quiz Study",
            "Revision",
            "Project",
            "Notes"
        ]


        if (
            task["task_category"]
            in splittable_categories
        ):

            sessions = (
                split_task_into_sessions(
                    remaining_minutes,
                    max_session=90,
                    min_session=30
                )
            )

        else:

            sessions = [
                remaining_minutes
            ]


        # ----------------------------------------------------
        # Create sessions
        # ----------------------------------------------------

        for session_number, duration in enumerate(
            sessions,
            start=1
        ):

            session = task.copy()

            session["session_duration"] = duration

            session["urgency_score"] = (
                urgency_score
            )

            session["urgency_level"] = (
                urgency_level
            )

            session["session_number"] = (
                session_number
            )

            session["total_sessions"] = (
                len(sessions)
            )

            prepared_sessions.append(
                session
            )


    # --------------------------------------------------------
    # Most urgent tasks first
    # --------------------------------------------------------

    prepared_sessions.sort(
        key=lambda x: (
            -x["urgency_score"],
            x["deadline"]
        )
    )

    return prepared_sessions


# ============================================================
# 8. CREATE SMART SCHEDULE
# ============================================================

def create_schedule(tasks, current_time):

    if not tasks:
        return [], []


    # --------------------------------------------------------
    # Latest deadline
    # --------------------------------------------------------

    latest_deadline = max(
        task["deadline"]
        for task in tasks
    )


    # --------------------------------------------------------
    # Generate calendar
    # --------------------------------------------------------

    available_slots = generate_slots(
        current_time,
        latest_deadline
    )

    available_slot_set = set(
        available_slots
    )


    # --------------------------------------------------------
    # Scheduling trackers
    # --------------------------------------------------------

    occupied_slots = set()

    schedule = []

    unscheduled = []

    # Tracks how many minutes a task has
    # already received on a particular day.
    daily_task_minutes = {}


    # --------------------------------------------------------
    # Prepare/split tasks
    # --------------------------------------------------------

    sessions = prepare_tasks(
        tasks,
        current_time
    )


    # ========================================================
    # SCHEDULE EACH SESSION
    # ========================================================

    for task in sessions:

        options = []


        for start_slot in available_slots:

            # ------------------------------------------------
            # Cannot start after deadline
            # ------------------------------------------------

            if start_slot >= task["deadline"]:
                continue


            # ------------------------------------------------
            # Limit same split task per day
            # ------------------------------------------------

            day_key = (
                task["name"],
                start_slot.date()
            )

            already_scheduled = (
                daily_task_minutes.get(
                    day_key,
                    0
                )
            )

            max_daily_task_minutes = 120


            if (
                task["total_sessions"] > 1
                and
                already_scheduled
                + task["session_duration"]
                > max_daily_task_minutes
            ):
                continue


            # ------------------------------------------------
            # Check whether task fits
            # ------------------------------------------------

            required_slots = session_fits(
                start_slot,
                task["session_duration"],
                available_slot_set,
                occupied_slots,
                task["deadline"]
            )


            if required_slots is None:
                continue


            # ------------------------------------------------
            # ML productivity score
            # ------------------------------------------------

            productivity = predict_productivity(
                task,
                start_slot
            )


            options.append({

                "start":
                    start_slot,

                "slots":
                    required_slots,

                "productivity":
                    productivity
            })


        # ====================================================
        # PICK BEST AVAILABLE SLOT
        # ====================================================

        if options:

            best = max(
                options,
                key=lambda x:
                    x["productivity"]
            )


            # ------------------------------------------------
            # Occupy selected slots
            # ------------------------------------------------

            for slot in best["slots"]:
                occupied_slots.add(slot)


            # ------------------------------------------------
            # Update daily task workload
            # ------------------------------------------------

            day_key = (
                task["name"],
                best["start"].date()
            )

            daily_task_minutes[day_key] = (
                daily_task_minutes.get(
                    day_key,
                    0
                )
                + task["session_duration"]
            )


            # ------------------------------------------------
            # End time
            # ------------------------------------------------

            end_time = (
                best["start"]
                + timedelta(
                    minutes=
                    task["session_duration"]
                )
            )


            # ------------------------------------------------
            # Add task to final schedule
            # ------------------------------------------------

            schedule.append({

                "name":
                    task["name"],

                "subject":
                    task["subject"],

                "category":
                    task["task_category"],

                "start":
                    best["start"],

                "end":
                    end_time,

                "duration":
                    task["session_duration"],

                "urgency":
                    task["urgency_score"],

                "urgency_level":
                    task["urgency_level"],

                "productivity":
                    best["productivity"],

                "deadline":
                    task["deadline"],

                "session_number":
                    task["session_number"],

                "total_sessions":
                    task["total_sessions"]
            })


        # ====================================================
        # COULD NOT SCHEDULE
        # ====================================================

        else:

            unscheduled.append(
                task
            )


    # --------------------------------------------------------
    # Sort final schedule chronologically
    # --------------------------------------------------------

    schedule.sort(
        key=lambda x:
            x["start"]
    )

    return schedule, unscheduled


# ============================================================
# 9. DISPLAY FINAL SCHEDULE
# ============================================================

def display_schedule(
    schedule,
    unscheduled
):

    print("\n" + "=" * 70)

    print(
        "              SMARTSCHED WEEKLY ACADEMIC PLAN"
    )

    print("=" * 70)


    if not schedule:

        print(
            "\nNo tasks could be scheduled."
        )


    current_day = None


    for item in schedule:

        item_day = (
            item["start"].date()
        )


        # ----------------------------------------------------
        # New day heading
        # ----------------------------------------------------

        if item_day != current_day:

            current_day = item_day

            print(
                "\n"
                + "-" * 70
            )

            print(
                item["start"].strftime(
                    "%A, %d %B %Y"
                )
            )

            print(
                "-" * 70
            )


        # ----------------------------------------------------
        # Time
        # ----------------------------------------------------

        print(
            "\n"
            + item["start"].strftime(
                "%H:%M"
            )
            + " - "
            + item["end"].strftime(
                "%H:%M"
            )
        )


        # ----------------------------------------------------
        # Task
        # ----------------------------------------------------

        print(
            item["name"]
        )


        # ----------------------------------------------------
        # Session number
        # ----------------------------------------------------

        if item["total_sessions"] > 1:

            print(
                "Session:",
                f"{item['session_number']}"
                f"/{item['total_sessions']}"
            )


        print(
            "Subject:",
            item["subject"]
        )


        print(
            "Urgency:",
            f"{item['urgency']}/100",
            f"({item['urgency_level']})"
        )


        print(
            "Predicted Productivity:",
            f"{item['productivity']:.2f}/10"
        )


        print(
            "Deadline:",
            item["deadline"].strftime(
                "%d %b %Y %H:%M"
            )
        )


    # ========================================================
    # UNSCHEDULED WORK
    # ========================================================

    if unscheduled:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "WARNING - UNSCHEDULED WORK"
        )

        print(
            "=" * 70
        )


        for task in unscheduled:

            print(
                "\n"
                + task["name"]
            )

            print(
                "Required:",
                task["session_duration"],
                "minutes"
            )

            print(
                "Deadline:",
                task["deadline"].strftime(
                    "%d %b %Y %H:%M"
                )
            )


    print(
        "\n"
        + "=" * 70
    )


# ============================================================
# 10. TEST SMARTSCHED
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Fixed test time
    # --------------------------------------------------------

    current_time = datetime(
        2026,
        10,
        12,
        6,
        0
    )


    # --------------------------------------------------------
    # Student tasks
    # --------------------------------------------------------

    tasks = [

        # ====================================================
        # ML ASSIGNMENT
        # ====================================================

        {
            "name":
                "ML Assignment",

            "task_category":
                "Assignment",

            "subject":
                "Machine Learning",

            "deadline":
                datetime(
                    2026,
                    10,
                    13,
                    23,
                    59
                ),

            "duration":
                120,

            "difficulty":
                "Hard",

            "importance":
                "High",

            "progress":
                0
        },


        # ====================================================
        # WAD PRACTICAL
        # ====================================================

        {
            "name":
                "WAD Practical",

            "task_category":
                "Practical",

            "subject":
                "Web Development",

            "deadline":
                datetime(
                    2026,
                    10,
                    14,
                    17,
                    0
                ),

            "duration":
                90,

            "difficulty":
                "Medium",

            "importance":
                "High",

            "progress":
                0
        },


        # ====================================================
        # WC EXAM STUDY
        # ====================================================

        {
            "name":
                "WC Exam Study",

            "task_category":
                "Exam Study",

            "subject":
                "Wireless Communication",

            "deadline":
                datetime(
                    2026,
                    10,
                    16,
                    9,
                    0
                ),

            "duration":
                360,

            "difficulty":
                "Hard",

            "importance":
                "High",

            "progress":
                0
        },


        # ====================================================
        # DBMS NOTES
        # ====================================================

        {
            "name":
                "DBMS Notes",

            "task_category":
                "Notes",

            "subject":
                "DBMS",

            "deadline":
                datetime(
                    2026,
                    10,
                    18,
                    23,
                    59
                ),

            "duration":
                120,

            "difficulty":
                "Easy",

            "importance":
                "Low",

            "progress":
                0
        }
    ]


    # ========================================================
    # GENERATE SCHEDULE
    # ========================================================

    schedule, unscheduled = (
        create_schedule(
            tasks,
            current_time
        )
    )


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    display_schedule(
        schedule,
        unscheduled
    )
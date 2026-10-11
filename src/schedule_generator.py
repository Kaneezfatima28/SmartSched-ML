import sys
from pathlib import Path
from datetime import datetime, timedelta

import joblib
import pandas as pd

sys.path.append(str(Path(__file__).parent))

from urgency import calculate_urgency, get_urgency_level


# ---------------------------------
# Load ML model
# ---------------------------------

model = joblib.load("models/smartsched_model.pkl")


# ---------------------------------
# Student tasks
# ---------------------------------

tasks = [
    {
        "name": "ML Assignment",
        "task_category": "Assignment",
        "subject": "Machine Learning",
        "day_of_week": "Monday",
        "duration": 120,
        "difficulty": "Hard",
        "importance": "High",
        "hours_until_deadline": 8,
        "progress": 20
    },
    {
        "name": "WAD Practical",
        "task_category": "Practical",
        "subject": "Web Development",
        "day_of_week": "Monday",
        "duration": 90,
        "difficulty": "Medium",
        "importance": "High",
        "hours_until_deadline": 30,
        "progress": 0
    },
    {
        "name": "WC Exam Study",
        "task_category": "Exam Study",
        "subject": "Wireless Communication",
        "day_of_week": "Monday",
        "duration": 120,
        "difficulty": "Hard",
        "importance": "High",
        "hours_until_deadline": 72,
        "progress": 10
    },
    {
        "name": "DBMS Notes",
        "task_category": "Notes",
        "subject": "DBMS",
        "day_of_week": "Monday",
        "duration": 60,
        "difficulty": "Easy",
        "importance": "Low",
        "hours_until_deadline": 120,
        "progress": 50
    }
]


# ---------------------------------
# Time helpers
# ---------------------------------

def time_to_minutes(time_string):

    dt = datetime.strptime(
        time_string,
        "%H:%M"
    )

    return dt.hour * 60 + dt.minute


def minutes_to_time(minutes):

    hours = minutes // 60
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


# ---------------------------------
# Student availability
# ---------------------------------

available_periods = [
    ("06:00", "09:00"),
    ("16:00", "23:00")
]


# ---------------------------------
# Generate 30-minute slots
# ---------------------------------

available_slots = []

for start, end in available_periods:

    start_minutes = time_to_minutes(start)
    end_minutes = time_to_minutes(end)

    current = start_minutes

    while current < end_minutes:

        available_slots.append(current)

        current += 30


# ---------------------------------
# ML productivity prediction
# ---------------------------------

def predict_productivity(task, start_minutes):

    # Our current model was trained using hour values.
    # 16:30 therefore becomes 16.5.
    start_hour = start_minutes / 60

    task_data = pd.DataFrame([{
        "task_category":
            task["task_category"],

        "subject":
            task["subject"],

        "day_of_week":
            task["day_of_week"],

        "start_hour":
            start_hour,

        "duration":
            task["duration"],

        "difficulty":
            task["difficulty"],

        "importance":
            task["importance"],

        "hours_until_deadline":
            task["hours_until_deadline"]
    }])

    return model.predict(task_data)[0]


# ---------------------------------
# Calculate urgency
# ---------------------------------

for task in tasks:

    task["urgency_score"] = calculate_urgency(
        task["hours_until_deadline"],
        task["duration"],
        task["difficulty"],
        task["importance"],
        task["progress"]
    )

    task["urgency_level"] = get_urgency_level(
        task["urgency_score"]
    )


# ---------------------------------
# Most urgent first
# ---------------------------------

tasks.sort(
    key=lambda x: x["urgency_score"],
    reverse=True
)


# ---------------------------------
# Scheduling
# ---------------------------------

occupied_slots = set()

schedule = []


for task in tasks:

    # Number of 30-minute slots needed
    slots_required = (
        task["duration"] + 29
    ) // 30

    possible_options = []


    for start_slot in available_slots:

        required_slots = [
            start_slot + (i * 30)
            for i in range(slots_required)
        ]


        # All required slots must exist
        if not all(
            slot in available_slots
            for slot in required_slots
        ):
            continue


        # No overlap
        if any(
            slot in occupied_slots
            for slot in required_slots
        ):
            continue


        productivity = predict_productivity(
            task,
            start_slot
        )


        possible_options.append({
            "start": start_slot,
            "slots": required_slots,
            "productivity": productivity
        })


    # ---------------------------------
    # Select best option
    # ---------------------------------

    if possible_options:

        best = max(
            possible_options,
            key=lambda x:
                x["productivity"]
        )


        for slot in best["slots"]:
            occupied_slots.add(slot)


        start = best["start"]

        end = (
            start
            + slots_required * 30
        )


        schedule.append({
            "name": task["name"],
            "start": start,
            "end": end,
            "urgency": task["urgency_score"],
            "level": task["urgency_level"],
            "productivity":
                best["productivity"]
        })


    else:

        schedule.append({
            "name": task["name"],
            "start": None,
            "end": None,
            "urgency": task["urgency_score"],
            "level": task["urgency_level"],
            "productivity": None
        })


# ---------------------------------
# Sort final schedule
# ---------------------------------

scheduled = [
    x for x in schedule
    if x["start"] is not None
]

unscheduled = [
    x for x in schedule
    if x["start"] is None
]

scheduled.sort(
    key=lambda x: x["start"]
)


# ---------------------------------
# Display
# ---------------------------------

print("\n" + "=" * 60)

print(
    "             SMARTSCHED - STUDENT SCHEDULE"
)

print("=" * 60)


for item in scheduled:

    print(
        "\n"
        + minutes_to_time(item["start"])
        + " - "
        + minutes_to_time(item["end"])
    )

    print(item["name"])

    print(
        f"Urgency: "
        f"{item['urgency']}/100 "
        f"({item['level']})"
    )

    print(
        f"Predicted Productivity: "
        f"{item['productivity']:.2f}/10"
    )


print("\n09:00 - 16:00")
print("COLLEGE")


if unscheduled:

    print("\n" + "=" * 60)
    print("UNSCHEDULED TASKS")
    print("=" * 60)

    for item in unscheduled:

        print(
            item["name"],
            "-",
            item["level"]
        )


print("\n" + "=" * 60)
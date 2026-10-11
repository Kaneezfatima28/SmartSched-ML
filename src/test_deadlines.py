from datetime import datetime

from deadline_utils import (
    calculate_hours_until_deadline,
    is_deadline_passed
)


current_time = datetime(
    2026, 10, 11, 16, 0
)


tasks = [
    {
        "name": "ML Assignment",
        "deadline": "2026-10-12 23:59"
    },

    {
        "name": "WAD Practical",
        "deadline": "2026-10-14 17:00"
    },

    {
        "name": "WC Exam",
        "deadline": "2026-10-16 09:00"
    },

    {
        "name": "DBMS Notes",
        "deadline": "2026-10-18 23:59"
    }
]


for task in tasks:

    hours = calculate_hours_until_deadline(
        task["deadline"],
        current_time
    )

    passed = is_deadline_passed(
        task["deadline"],
        current_time
    )

    print("\n", task["name"])

    print(
        "Deadline:",
        task["deadline"]
    )

    print(
        "Hours Remaining:",
        round(hours, 1)
    )

    print(
        "Passed:",
        passed
    )
from datetime import datetime


def calculate_hours_until_deadline(deadline, current_time=None):

    if current_time is None:
        current_time = datetime.now()

    if isinstance(deadline, str):
        deadline = datetime.strptime(
            deadline,
            "%Y-%m-%d %H:%M"
        )

    difference = deadline - current_time

    hours = difference.total_seconds() / 3600

    return max(0, hours)


def is_deadline_passed(deadline, current_time=None):

    if current_time is None:
        current_time = datetime.now()

    if isinstance(deadline, str):
        deadline = datetime.strptime(
            deadline,
            "%Y-%m-%d %H:%M"
        )

    return deadline < current_time


def calculate_remaining_duration(
    total_duration,
    progress
):

    progress = max(
        0,
        min(progress, 100)
    )

    remaining = total_duration * (
        (100 - progress) / 100
    )

    return round(remaining)

def check_deadline_risk(
    remaining_minutes,
    hours_until_deadline
):

    available_minutes = (
        hours_until_deadline * 60
    )

    if remaining_minutes > available_minutes:

        return "IMPOSSIBLE"

    ratio = (
        remaining_minutes
        / available_minutes
    )

    if ratio >= 0.75:
        return "CRITICAL"

    elif ratio >= 0.50:
        return "HIGH"

    elif ratio >= 0.25:
        return "MEDIUM"

    else:
        return "LOW"

if __name__ == "__main__":

    # Fixed test time so everyone gets
    # predictable results.
    current = datetime(
        2026, 10, 11, 16, 0
    )

    deadline = "2026-10-13 23:59"

    hours = calculate_hours_until_deadline(
        deadline,
        current
    )

    print(
        "Hours until deadline:",
        round(hours, 2)
    )

    print(
        "Deadline passed:",
        is_deadline_passed(
            deadline,
            current
        )
    )
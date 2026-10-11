from datetime import datetime, timedelta


# ============================================================
# SMARTSCHED - MULTI-DAY CALENDAR ENGINE
# ============================================================


# ------------------------------------------------------------
# 1. Convert HH:MM to minutes
# ------------------------------------------------------------

def time_to_minutes(time_string):
    hour, minute = map(int, time_string.split(":"))
    return hour * 60 + minute


# ------------------------------------------------------------
# 2. Convert minutes to HH:MM
# ------------------------------------------------------------

def minutes_to_time(minutes):
    hour = minutes // 60
    minute = minutes % 60

    return f"{hour:02d}:{minute:02d}"


# ------------------------------------------------------------
# 3. Student availability
# ------------------------------------------------------------

WEEKDAY_AVAILABILITY = [
    ("06:00", "09:00"),
    ("16:00", "23:00")
]

WEEKEND_AVAILABILITY = [
    ("07:00", "12:00"),
    ("14:00", "23:00")
]


# ------------------------------------------------------------
# 4. Generate slots for one day
# ------------------------------------------------------------

def generate_day_slots(date):

    day_name = date.strftime("%A")

    if day_name in ["Saturday", "Sunday"]:
        periods = WEEKEND_AVAILABILITY
    else:
        periods = WEEKDAY_AVAILABILITY

    slots = []

    for start_time, end_time in periods:

        start = time_to_minutes(start_time)
        end = time_to_minutes(end_time)

        current = start

        while current < end:

            slot_datetime = datetime(
                date.year,
                date.month,
                date.day,
                current // 60,
                current % 60
            )

            slots.append(slot_datetime)

            current += 30

    return slots


# ------------------------------------------------------------
# 5. Generate multi-day calendar
# ------------------------------------------------------------

def generate_calendar(
    start_date,
    number_of_days=7
):

    calendar = {}

    for offset in range(number_of_days):

        current_date = (
            start_date
            + timedelta(days=offset)
        )

        calendar[current_date.date()] = (
            generate_day_slots(current_date)
        )

    return calendar


# ------------------------------------------------------------
# 6. Get slots before a deadline
# ------------------------------------------------------------

def get_slots_before_deadline(
    calendar,
    deadline
):

    valid_slots = []

    for date, slots in calendar.items():

        for slot in slots:

            if slot < deadline:
                valid_slots.append(slot)

    return valid_slots


# ------------------------------------------------------------
# 7. Display calendar
# ------------------------------------------------------------

def display_calendar(calendar):

    print("\n" + "=" * 60)
    print("          SMARTSCHED MULTI-DAY CALENDAR")
    print("=" * 60)

    for date, slots in calendar.items():

        day_name = date.strftime("%A")

        print(
            f"\n{day_name} "
            f"{date.strftime('%d %B %Y')}"
        )

        if not slots:
            print("No available slots")
            continue

        # Group consecutive slots into periods
        period_start = slots[0]
        previous = slots[0]

        for slot in slots[1:]:

            difference = (
                slot - previous
            ).total_seconds() / 60

            if difference != 30:

                period_end = (
                    previous
                    + timedelta(minutes=30)
                )

                print(
                    f"  "
                    f"{period_start.strftime('%H:%M')}"
                    f" - "
                    f"{period_end.strftime('%H:%M')}"
                )

                period_start = slot

            previous = slot

        period_end = (
            previous
            + timedelta(minutes=30)
        )

        print(
            f"  "
            f"{period_start.strftime('%H:%M')}"
            f" - "
            f"{period_end.strftime('%H:%M')}"
        )

    print("\n" + "=" * 60)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Fixed date for testing
    start_date = datetime(
        2026,
        10,
        12
    )

    # Generate one week
    calendar = generate_calendar(
        start_date=start_date,
        number_of_days=7
    )

    display_calendar(calendar)


    # --------------------------------------------------------
    # Test deadline
    # --------------------------------------------------------

    assignment_deadline = datetime(
        2026,
        10,
        13,
        20,
        0
    )

    valid_slots = (
        get_slots_before_deadline(
            calendar,
            assignment_deadline
        )
    )


    print(
        "\nAssignment Deadline:",
        assignment_deadline.strftime(
            "%d %B %Y %H:%M"
        )
    )

    print(
        "Available 30-minute slots "
        "before deadline:",
        len(valid_slots)
    )

    print(
        "Available study time:",
        len(valid_slots) * 30,
        "minutes"
    )
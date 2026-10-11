# ============================================
# SmartSched - Task Splitter
# ============================================
#
# Purpose:
# Splits large academic tasks into manageable
# study sessions and distributes them across
# multiple days.
#
# Example:
# 360 minutes of exam study
# -> 90 min Monday
# -> 90 min Tuesday
# -> 90 min Wednesday
# -> 90 min Thursday
# ============================================


# --------------------------------------------
# 1. Split task into smaller sessions
# --------------------------------------------

def split_task_into_sessions(
    total_minutes,
    max_session=90,
    min_session=30
):
    """
    Split a large task into manageable sessions.

    Example:
    300 minutes -> [90, 90, 90, 30]
    """

    if total_minutes <= 0:
        return []

    sessions = []
    remaining = total_minutes

    while remaining > 0:

        # Full session
        if remaining >= max_session:
            session = max_session

        # Remaining time is large enough
        # to become its own session
        elif remaining >= min_session:
            session = remaining

        # Very small leftover
        else:
            if sessions:
                sessions[-1] += remaining
            else:
                sessions.append(remaining)

            break

        sessions.append(session)
        remaining -= session

    return sessions


# --------------------------------------------
# 2. Distribute sessions across days
# --------------------------------------------

def distribute_sessions_across_days(
    sessions,
    days,
    max_daily_minutes=120
):
    """
    Distribute study sessions across days.

    The function tries to avoid putting too
    much study for the same task on one day.
    """

    if not days:
        return {}

    schedule = {
        day: []
        for day in days
    }

    daily_totals = {
        day: 0
        for day in days
    }

    day_index = 0

    for session in sessions:

        placed = False
        attempts = 0

        while attempts < len(days):

            day = days[day_index]

            # Check whether the session fits
            if (
                daily_totals[day] + session
                <= max_daily_minutes
            ):

                schedule[day].append(session)

                daily_totals[day] += session

                placed = True

                # Move to next day
                day_index = (
                    day_index + 1
                ) % len(days)

                break

            # Try another day
            day_index = (
                day_index + 1
            ) % len(days)

            attempts += 1

        # Could not place the session
        if not placed:
            print(
                f"WARNING: {session}-minute "
                f"session could not be placed."
            )

    return schedule


# --------------------------------------------
# 3. Calculate total scheduled minutes
# --------------------------------------------

def calculate_total_scheduled(schedule):
    """
    Calculate total minutes that were
    successfully distributed.
    """

    total = 0

    for sessions in schedule.values():
        total += sum(sessions)

    return total


# --------------------------------------------
# 4. Display study plan
# --------------------------------------------

def display_study_plan(schedule):

    print("\n" + "=" * 45)
    print("        SMARTSCHED STUDY PLAN")
    print("=" * 45)

    for day, sessions in schedule.items():

        print(f"\n{day}")

        if not sessions:
            print("  No session")
            continue

        for number, duration in enumerate(
            sessions,
            start=1
        ):
            print(
                f"  Session {number}: "
                f"{duration} minutes"
            )

        print(
            "  Total:",
            sum(sessions),
            "minutes"
        )

    print("\n" + "=" * 45)


# --------------------------------------------
# 5. Main test
# --------------------------------------------

if __name__ == "__main__":

    # Example:
    # Student needs 6 hours of preparation
    # for an upcoming exam.

    total_study_minutes = 360

    available_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday"
    ]

    print(
        "Total study required:",
        total_study_minutes,
        "minutes"
    )


    # ----------------------------------------
    # Split the large study task
    # ----------------------------------------

    sessions = split_task_into_sessions(
        total_minutes=total_study_minutes,
        max_session=90,
        min_session=30
    )

    print(
        "Generated sessions:",
        sessions
    )


    # ----------------------------------------
    # Distribute sessions
    # ----------------------------------------

    study_plan = (
        distribute_sessions_across_days(
            sessions=sessions,
            days=available_days,
            max_daily_minutes=120
        )
    )


    # ----------------------------------------
    # Display result
    # ----------------------------------------

    display_study_plan(
        study_plan
    )


    # ----------------------------------------
    # Verify scheduled time
    # ----------------------------------------

    scheduled_minutes = (
        calculate_total_scheduled(
            study_plan
        )
    )

    print(
        "Required minutes:",
        total_study_minutes
    )

    print(
        "Scheduled minutes:",
        scheduled_minutes
    )


    if scheduled_minutes == total_study_minutes:

        print(
            "\nSUCCESS: All study time "
            "has been scheduled."
        )

    else:

        remaining = (
            total_study_minutes
            - scheduled_minutes
        )

        print(
            "\nWARNING:",
            remaining,
            "minutes still need scheduling."
        )
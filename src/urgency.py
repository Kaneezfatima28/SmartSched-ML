def calculate_urgency(
    hours_until_deadline,
    duration,
    difficulty,
    importance,
    progress=0
):
    score = 0

    # ---------------------------------
    # 1. Deadline score (max 45)
    # ---------------------------------

    if hours_until_deadline <= 6:
        score += 45

    elif hours_until_deadline <= 12:
        score += 40

    elif hours_until_deadline <= 24:
        score += 35

    elif hours_until_deadline <= 48:
        score += 28

    elif hours_until_deadline <= 72:
        score += 20

    elif hours_until_deadline <= 168:
        score += 10

    else:
        score += 5


    # ---------------------------------
    # 2. Importance score (max 25)
    # ---------------------------------

    importance_scores = {
        "Low": 5,
        "Medium": 15,
        "High": 25
    }

    score += importance_scores.get(
        importance,
        10
    )


    # ---------------------------------
    # 3. Difficulty score (max 15)
    # ---------------------------------

    difficulty_scores = {
        "Easy": 5,
        "Medium": 10,
        "Hard": 15
    }

    score += difficulty_scores.get(
        difficulty,
        5
    )


    # ---------------------------------
    # 4. Remaining work (max 15)
    # ---------------------------------

    remaining_fraction = (
        100 - progress
    ) / 100

    remaining_minutes = (
        duration * remaining_fraction
    )

    if remaining_minutes >= 180:
        score += 15

    elif remaining_minutes >= 120:
        score += 12

    elif remaining_minutes >= 60:
        score += 8

    else:
        score += 4


    # Maximum 100
    return min(score, 100)


def get_urgency_level(score):

    if score >= 80:
        return "CRITICAL"

    elif score >= 60:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"


# ---------------------------------
# Test
# ---------------------------------

if __name__ == "__main__":

    tasks = [
        {
            "name": "ML Assignment",
            "deadline": 8,
            "duration": 120,
            "difficulty": "Hard",
            "importance": "High",
            "progress": 20
        },

        {
            "name": "WAD Practical",
            "deadline": 30,
            "duration": 90,
            "difficulty": "Medium",
            "importance": "High",
            "progress": 0
        },

        {
            "name": "WC Exam Study",
            "deadline": 72,
            "duration": 300,
            "difficulty": "Hard",
            "importance": "High",
            "progress": 10
        },

        {
            "name": "DBMS Notes",
            "deadline": 120,
            "duration": 60,
            "difficulty": "Easy",
            "importance": "Low",
            "progress": 50
        }
    ]


    for task in tasks:

        score = calculate_urgency(
            task["deadline"],
            task["duration"],
            task["difficulty"],
            task["importance"],
            task["progress"]
        )

        level = get_urgency_level(score)

        print(
            task["name"],
            "->",
            score,
            level
        )


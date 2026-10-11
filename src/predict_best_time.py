import joblib
import pandas as pd


# ---------------------------------
# 1. Load trained model
# ---------------------------------

model = joblib.load(
    "models/smartsched_model.pkl"
)

print("SmartSched model loaded successfully!")


# ---------------------------------
# 2. Example student task
# ---------------------------------

task = {
    "task_category": "Assignment",
    "subject": "Machine Learning",
    "day_of_week": "Monday",
    "duration": 120,
    "difficulty": "Hard",
    "importance": "High",
    "hours_until_deadline": 24
}


# ---------------------------------
# 3. Hours we want to test
# ---------------------------------

candidate_hours = [
    6, 7, 8,
    16, 17, 18, 19, 20, 21, 22
]


# ---------------------------------
# 4. Test task at every hour
# ---------------------------------

results = []

for hour in candidate_hours:

    task_data = pd.DataFrame([{
        "task_category": task["task_category"],
        "subject": task["subject"],
        "day_of_week": task["day_of_week"],
        "start_hour": hour,
        "duration": task["duration"],
        "difficulty": task["difficulty"],
        "importance": task["importance"],
        "hours_until_deadline":
            task["hours_until_deadline"]
    }])

    predicted_score = model.predict(task_data)[0]

    results.append({
        "hour": hour,
        "predicted_productivity":
            predicted_score
    })


# ---------------------------------
# 5. Convert results to dataframe
# ---------------------------------

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="predicted_productivity",
    ascending=False
)


# ---------------------------------
# 6. Display all predictions
# ---------------------------------

print("\nPRODUCTIVITY PREDICTIONS")
print("--------------------------------")

for _, row in results_df.iterrows():

    hour = int(row["hour"])
    score = row["predicted_productivity"]

    print(
        f"{hour:02d}:00  ->  "
        f"{score:.2f}/10"
    )


# ---------------------------------
# 7. Find best time
# ---------------------------------

best = results_df.iloc[0]

best_hour = int(best["hour"])
best_score = best["predicted_productivity"]


print("\n--------------------------------")
print("SMARTSCHED RECOMMENDATION")
print("--------------------------------")

print(
    f"Best Time: {best_hour:02d}:00"
)

print(
    f"Predicted Productivity: "
    f"{best_score:.2f}/10"
)
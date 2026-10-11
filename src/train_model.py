import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ---------------------------------
# 1. Load dataset
# ---------------------------------

df = pd.read_csv("data/student_tasks.csv")

print("Dataset loaded!")
print("Total records:", len(df))


# ---------------------------------
# 2. Define features and target
# ---------------------------------

features = [
    "task_category",
    "subject",
    "day_of_week",
    "start_hour",
    "duration",
    "difficulty",
    "importance",
    "hours_until_deadline"
]

X = df[features]

y = df["productivity_score"]


# ---------------------------------
# 3. Define categorical/numerical
# ---------------------------------

categorical_features = [
    "task_category",
    "subject",
    "day_of_week",
    "difficulty",
    "importance"
]

numerical_features = [
    "start_hour",
    "duration",
    "hours_until_deadline"
]


# ---------------------------------
# 4. Preprocessing
# ---------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "num",
            "passthrough",
            numerical_features
        )
    ]
)


# ---------------------------------
# 5. Create ML model
# ---------------------------------

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# ---------------------------------
# 6. Build complete pipeline
# ---------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ---------------------------------
# 7. Split dataset
# ---------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# ---------------------------------
# 8. Train model
# ---------------------------------

print("\nTraining model...")

pipeline.fit(X_train, y_train)

print("Training completed!")


# ---------------------------------
# 9. Make predictions
# ---------------------------------

predictions = pipeline.predict(X_test)


# ---------------------------------
# 10. Evaluate
# ---------------------------------

mae = mean_absolute_error(
    y_test,
    predictions
)

mse = mean_squared_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("\nMODEL PERFORMANCE")
print("-------------------------")

print("MAE:", round(mae, 2))
print("MSE:", round(mse, 2))
print("R2 Score:", round(r2, 2))


# ---------------------------------
# 11. Compare actual vs predicted
# ---------------------------------

results = pd.DataFrame({
    "Actual": y_test.values,
    "Predicted": predictions
})

print("\nActual vs Predicted")
print("-------------------------")

print(results)


# ---------------------------------
# 12. Save trained model
# ---------------------------------

os.makedirs("models", exist_ok=True)

joblib.dump(
    pipeline,
    "models/smartsched_model.pkl"
)

print("\nModel saved successfully!")
print("models/smartsched_model.pkl")
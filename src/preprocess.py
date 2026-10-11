import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

# -----------------------------
# 1. Load dataset
# -----------------------------

df = pd.read_csv("data/student_tasks.csv")

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)


# -----------------------------
# 2. Select features
# -----------------------------

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

# Target
y = df["productivity_score"]


# -----------------------------
# 3. Define feature types
# -----------------------------

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


# -----------------------------
# 4. Create preprocessor
# -----------------------------

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


# -----------------------------
# 5. Split dataset
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# -----------------------------
# 6. Transform training data
# -----------------------------

X_train_processed = preprocessor.fit_transform(X_train)

X_test_processed = preprocessor.transform(X_test)


# -----------------------------
# 7. Display results
# -----------------------------

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

print("\nOriginal number of features:")
print(X.shape[1])

print("\nFeatures after encoding:")
print(X_train_processed.shape[1])

print("\nPreprocessing completed successfully!")
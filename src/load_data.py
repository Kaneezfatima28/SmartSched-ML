import pandas as pd

df = pd.read_csv("data/student_tasks.csv")

print("SmartSched Dataset")
print("------------------")

print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing Values:")
print(df.isnull().sum())
#!/usr/bin/env python
# convert_dataset_time.py
# Converts the 'Time' column from seconds since midnight to HH:MM format

import pandas as pd
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_ROOT, "Backend", "data", "main.csv")
BACKUP_PATH = os.path.join(PROJECT_ROOT, "Backend", "data", "main_backup.csv")

print(f"Loading dataset from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

print(f"Original dataset shape: {df.shape}")
print(f"Sample Time values (seconds): {df['Time'].head(10).tolist()}")

# Backup original
df.to_csv(BACKUP_PATH, index=False)
print(f"Backup saved to {BACKUP_PATH}")

# Convert seconds since midnight to HH:MM format
def seconds_to_time(seconds):
    """Convert seconds since midnight to HH:MM format"""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"

df['Time'] = df['Time'].apply(seconds_to_time)

print(f"\nConverted Time values (HH:MM format): {df['Time'].head(10).tolist()}")

# Save updated dataset
df.to_csv(DATA_PATH, index=False)
print(f"\nDataset updated and saved to {DATA_PATH}")
print("Done!")

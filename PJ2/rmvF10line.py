import pandas as pd

# Read the CSV file while skipping the first 10 rows
file_path = 'd2.csv'
data = pd.read_csv(file_path, skiprows=10)

# Save the result to a new CSV file (or overwrite the existing one)
output_path = 'd2a.csv'
data.to_csv(output_path, index=False)

print(f"First 10 lines removed, saved to {output_path}")
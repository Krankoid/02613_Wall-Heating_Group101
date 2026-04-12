import os
import pandas as pd
import matplotlib.pyplot as plt

# Paths
DATA_PATH = "tasks/task12/results.csv"
OUTPUT_DIR = "tasks/task12"
TXT_FILE = os.path.join(OUTPUT_DIR, "analysis.txt")
FIG_FILE = os.path.join(OUTPUT_DIR, "mean_temp_histogram.png")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(DATA_PATH)

plt.figure(figsize=(8, 5))
plt.hist(df["mean_temp"], bins=30, edgecolor="black")
plt.xlabel("Mean temperature [°C]")
plt.ylabel("Number of buildings")
plt.title("Distribution of mean temperatures")
plt.tight_layout()
plt.savefig(FIG_FILE, dpi=300)
plt.show()

lines = []

lines.append(f"Number of buildings: {len(df)}")

avg_mean_temp = df["mean_temp"].mean()
lines.append(f"Average mean temperature: {avg_mean_temp:.3f} °C")

avg_std_temp = df["std_temp"].mean()
lines.append(f"Average temperature standard deviation: {avg_std_temp:.3f} °C")

n_above_18 = (df["pct_above_18"] >= 50.0).sum()
lines.append(f"Buildings with at least 50% area above 18°C: {n_above_18}")

n_below_15 = (df["pct_below_15"] >= 50.0).sum()
lines.append(f"Buildings with at least 50% area below 15°C: {n_below_15}")

for line in lines:
    print(line)

with open(TXT_FILE, "w") as f:
    f.write("\n".join(lines))
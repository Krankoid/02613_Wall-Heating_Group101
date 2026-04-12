import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results.csv")

plt.figure(figsize=(8, 5))
plt.hist(df["mean_temp"], bins=30, edgecolor="black")
plt.xlabel("Mean temperature [°C]")
plt.ylabel("Number of buildings")
plt.title("Distribution of mean temperatures")
plt.tight_layout()
plt.savefig("mean_temperature_histogram.png", dpi=300)
plt.show()

avg_mean_temp = df["mean_temp"].mean()
print(f"Average mean temperature: {avg_mean_temp:.3f} °C")

avg_std_temp = df["std_temp"].mean()
print(f"Average temperature standard deviation: {avg_std_temp:.3f} °C")

n_above_18 = (df["pct_above_18"] >= 0.5).sum()
print(f"Buildings with at least 50% area above 18°C: {n_above_18}")

n_below_15 = (df["pct_below_15"] >= 0.5).sum()
print(f"Buildings with at least 50% area below 15°C: {n_below_15}")
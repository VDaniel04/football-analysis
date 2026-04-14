# ========================
# IMPORTS
# ========================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ========================
# SETTINGS
# ========================
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# ========================
# LOAD DATA
# ========================
df = pd.read_csv("results.csv")

# ========================
# FEATURE ENGINEERING
# ========================

# Convert date and extract year
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

# Total goals per match
df["total_goals"] = df["home_score"] + df["away_score"]

# Goal difference (match balance indicator)
df["goal_diff"] = abs(df["home_score"] - df["away_score"])

# High scoring matches (>3 goals)
df["high_scoring"] = df["total_goals"] > 3

# Match result
def result(row):
    if row["home_score"] > row["away_score"]:
        return "home_win"
    elif row["home_score"] < row["away_score"]:
        return "away_win"
    else:
        return "draw"

df["result"] = df.apply(result, axis=1)

# Match type (balance classification)
def match_type(diff):
    if diff <= 1:
        return "balanced"
    elif diff <= 3:
        return "medium"
    else:
        return "one-sided"

df["match_type"] = df["goal_diff"].apply(match_type)

# Exciting matches (balanced + high scoring)
df["exciting"] = (df["goal_diff"] <= 1) & (df["total_goals"] >= 3)

# ========================
# BASIC ANALYSIS
# ========================

print("Dataset shape:", df.shape)
print("Max date:", df["date"].max())

# Goal distribution insight
percentage = (df["high_scoring"].sum() / len(df)) * 100
print(f"{percentage:.2f}% of matches have more than 3 goals")

# ========================
# TEAM ANALYSIS
# ========================

# Filter reliable teams
team_stats = df.groupby("home_team").agg({
    "home_score": "mean",
    "home_team": "count"
})

team_stats.columns = ["avg_goals", "matches"]
team_stats = team_stats[team_stats["matches"] > 50]

print("\nTop scoring teams (home):")
print(team_stats.sort_values("avg_goals", ascending=False).head(10))

# High scoring rate per team
team_high_scoring = df.groupby("home_team").agg({
    "high_scoring": "mean",
    "home_team": "count"
})

team_high_scoring.columns = ["high_scoring_rate", "matches"]
team_high_scoring = team_high_scoring[team_high_scoring["matches"] > 200]

print("\nTop exciting teams:")
print(team_high_scoring.sort_values("high_scoring_rate", ascending=False).head(10))

# Balanced matches per team
balanced_rate = df.groupby("home_team").agg({
    "match_type": lambda x: (x == "balanced").mean(),
    "home_team": "count"
})

balanced_rate.columns = ["balanced_rate", "matches"]
balanced_rate = balanced_rate[balanced_rate["matches"] > 200]

print("\nMost balanced teams:")
print(balanced_rate.sort_values("balanced_rate", ascending=False).head(10))

# Dominance (average goal difference)
dominance = df.groupby("home_team").agg({
    "goal_diff": "mean",
    "home_team": "count"
})

dominance.columns = ["avg_goal_diff", "matches"]
dominance = dominance[dominance["matches"] > 200]

print("\nMost dominant teams:")
print(dominance.sort_values("avg_goal_diff", ascending=False).head(10))

# ========================
# VISUALIZATION
# ========================

# Goals distribution
plt.hist(df["total_goals"])
plt.xlabel("Goals per match")
plt.ylabel("Number of matches")
plt.title("Goals Distribution")
plt.savefig("images/goals_distribution.png")
plt.close()

# Goals over time
goals_per_year = df.groupby("year")["total_goals"].mean()

plt.plot(goals_per_year)
plt.xlabel("Year")
plt.ylabel("Average goals")
plt.title("Goals Evolution Over Time")
plt.savefig("images/goals_over_time.png")
plt.close()

# Result distribution
sns.countplot(x="result", data=df)
plt.title("Match Result Distribution")
plt.savefig("images/result_distribution.png")
plt.close()

# Match type distribution
sns.countplot(x="match_type", data=df)
plt.title("Match Type Distribution")
plt.savefig("images/match_type_distribution.png")
plt.close()

# ========================
# TEAM EVOLUTION (WOW ANALYSIS)
# ========================

team = "Brazil"

team_matches = df[(df["home_team"] == team) | (df["away_team"] == team)].copy()

# Extract team goals correctly
team_matches["team_goals"] = team_matches.apply(
    lambda row: row["home_score"] if row["home_team"] == team else row["away_score"],
    axis=1
)

team_yearly = team_matches.groupby("year")["team_goals"].mean()

plt.plot(team_yearly)
plt.title(f"Goal Evolution - {team}")
plt.xlabel("Year")
plt.ylabel("Goals per match")
plt.savefig("images/team_evolution.png")
plt.close()

print("\nAnalysis complete. Check the images folder for visualizations.")
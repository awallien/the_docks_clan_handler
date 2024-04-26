import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

def sort_by_year_month(monthyear):
    month = monthyear[0]
    year = monthyear[1]

    month_num = months[month]

    return year, month_num

df = pd.read_csv("C:\\Users\\aswal\\Documents\\projects\\osrs_skill_calc\\cache\\cache_db.csv")
df.reset_index()
df["Parent"] = df["Parent"].fillna(0)

monthyear_to_players = {}


for index, row in df.iterrows():
    name = row["Member"]
    date = row["Joined"]

    if row["Parent"]:
        continue

    _,month,year = date.split("-")

    monthyear = (month,year)

    if monthyear not in monthyear_to_players:
        monthyear_to_players[monthyear] = [name]
    else:
        monthyear_to_players[monthyear].append(name)

monthyears = sorted(monthyear_to_players.keys(), key=sort_by_year_month)

x = []
y = []

for year in ["2022", "2023"]:
    for month in months.keys():
        if month == "Dec" and year == "2023":
            continue
        x.append(month + "-" + year)
        y.append(len(monthyear_to_players.get((month,year), [])))

#y = [sum(y[:i+1]) for i in range(len(y))]

fig, ax = plt.subplots()

"""
y_avg = [y[i] if i == 0 else (y[i] + sum(y[:i])) / (i + 1) for i in range(len(y))]
ax.plot(x,y_avg, color="red")
ax.bar(x, y, align="center")
ax.set_ylabel("Number of players")
ax.set_xlabel("Month-Year")
plt.xticks(x, labels=x, rotation='vertical', fontsize=7.5)
ax.set_title("Total Number of Unique Players in \"The Docks\" Clan")
plt.subplots_adjust(bottom=0.15)
for bars in ax.containers:
    ax.bar_label(bars)
plt.text(len(x)+2, y_avg[-1], 'Avg:\n{:.5f}'.format(y_avg[-1]), ha='center', va='top', color='red')
plt.legend()
plt.show()
"""
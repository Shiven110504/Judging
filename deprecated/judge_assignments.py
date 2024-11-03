#!/usr/bin/env python3
import math
import random
import pandas as pd
import string

# Generate random judges' names
first_names = ['John', 'Jane', 'Mary', 'James', 'Patricia', 'Michael', 'Linda', 'Robert', 'Elizabeth', 'William', 'Jessica', 'David', 'Sarah', 'Thomas']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson']

# Select 14 random first and last names
judges = [(random.choice(first_names), random.choice(last_names)) for _ in range(14)]
judges_df = pd.DataFrame(judges, columns=['judgeFirstName', 'judgeLastName'])

# Save to CSV
judges_df.to_csv('judges.csv', index=False)

# Generate 90 rows of random 3-letter words
three_letter_words = [''.join(random.choices(string.ascii_lowercase, k=3)) for _ in range(90)]

# Create a DataFrame with numbers from 1 to 90
numbers = list(range(1, 91))
words_numbers_df = pd.DataFrame({'teamName': three_letter_words, 'tableNumber': numbers})

# Save words and numbers DataFrame to a CSV file
words_numbers_df.to_csv('words_numbers.csv', index=False)

# Number of times each team wants to be judged
x = 3

# read in a csv for team names (teamName, tableNumber)
teams = pd.read_csv('words_numbers.csv')
num_teams = len(teams)
print(num_teams)
# read in a csv for judges (judgeFirstName, judgeLastName)
judges = pd.read_csv('judges.csv')
num_judges = len(judges)
print(num_judges)

# Calculate judges per batch
judges_per_batch = num_judges // x

# Calculate teams per judge
teams_per_judge = math.ceil(num_teams / judges_per_batch)

# Calculate total slots needed
total_slots = judges_per_batch * teams_per_judge

# Calculate number of empty slots
num_remaining_teams = num_teams - ((teams_per_judge - 1) * judges_per_batch)

# Create an empty assignment matrix
assignments = []

# Assign teams to judges in batches
for _ in range(x):
    team_numbers = list(range(1, num_teams + 1))
    random.shuffle(team_numbers)
    n = num_remaining_teams
    for _ in range(judges_per_batch):
        slot = []
        for i in range(teams_per_judge):
            if i != teams_per_judge - 1:
                slot.append(team_numbers.pop(0))
            else:
                if n > 0:
                    slot.append(team_numbers.pop(0))
                    n -= 1

        assignments.append(slot)

# calculate how many judges were not included
not_assigned = num_judges - len(assignments)

for i in range(not_assigned):
    slot = []
    for j in range(teams_per_judge - 1):
        # find the judge with the most teams
        max_team_index = assignments.index(max(assignments, key=len))
        # take a random team from the judge with the most teams
        team = random.choice(assignments[max_team_index])

        satisfied = False
        while not satisfied:
            # check if this team is already assigned to the current judge
            if team not in slot:
                slot.append(team)
                # remove the team from the judge with the most teams
                assignments[max_team_index].remove(team)
                # assignments[max_team_index].append(-1)

                satisfied = True
            else:
                team = random.choice(assignments[max_team_index])

                

    assignments.append(slot)

# Create a Pandas DataFrame
df = pd.DataFrame(assignments)
df.index.name = 'Judge'

# replace NaN with -1
df = df.fillna(-1)

# make all int
df = df.astype(int)

# find the most teams a judge has
max_teams = df.apply(lambda x: x[x != -1].count(), axis=1).max()

df.columns = [f'Slot {i+1}' for i in range(max_teams)]

# replace the team numbers with team names and table numbers
for i in range(max_teams):
    df[f'Slot {i+1}'] = df[f'Slot {i+1}'].apply(lambda x: f'{teams.loc[x-1, "teamName"]} (Table {teams.loc[x-1, "tableNumber"]})' if x != -1 else 'No team for this time slot')

# add a column on the left called judge id, starting from 1001
df.insert(0, 'Judge ID', range(1001, 1001 + len(df)))

# replace the judge numbers with judge names
df.index = df.index.map(lambda x: f'{judges.loc[x, "judgeFirstName"]} {judges.loc[x, "judgeLastName"]}')

df

# Save the DataFrame to a CSV file
df.to_csv('assignments.csv')
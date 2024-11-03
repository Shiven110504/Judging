#!/usr/bin/env python3
import pandas as pd

# Load the data
points = pd.read_csv('points.csv')
teams = pd.read_csv('teams.csv')

# Standardize the points for each judge
points['standardizedPoints'] = points.groupby('judgeNumber')['points'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# Group by tableNumber, calculate the average standardized points and count how many judges saw each team
points_grouped = points.groupby('tableNumber').agg(
    standardizedPoints=('standardizedPoints', 'mean'),
    judgeCount=('judgeNumber', 'nunique')  # Count the unique judges
).reset_index()

# Sort by points in ascending order
sorted_points = points_grouped.sort_values(by='standardizedPoints', ascending=False)

# Add in the team names
# Assuming 'teams' is another DataFrame with a 'teamName' column and an index corresponding to 'tableNumber'
sorted_points = sorted_points.merge(teams[['tableNumber', 'teamName']], on='tableNumber', how='left')

# Reset the index
sorted_points = sorted_points.reset_index(drop=True)

# Display the final sorted DataFrame
sorted_points

# save the sorted points to a csv
sorted_points.to_csv('aggregated_and_sorted_points.csv')
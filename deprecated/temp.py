#!/usr/bin/env python3
import math
import random
import pandas as pd
import string

# Generate random judges' names
first_names = ['John', 'Jane', 'Mary', 'James', 'Patricia', 'Michael', 'Linda', 'Robert', 'Elizabeth', 'William', 'Jessica', 'David', 'Sarah', 'Thomas']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson']

# Select 14 random first and last names
num_judges = int(input("Enter number of judges: "))
judges = [(random.choice(first_names), random.choice(last_names)) for _ in range(num_judges)]
judges_df = pd.DataFrame(judges, columns=['judgeFirstName', 'judgeLastName'])

# Save to CSV
judges_df.to_csv('judges.csv', index=False)

# Get user input for number of rooms and total projects
total_projects = int(input("Enter total number of projects: "))
num_rooms = int(input("Enter number of rooms: "))

# Adjust the project generation
three_letter_words = [''.join(random.choices(string.ascii_lowercase, k=3)) for _ in range(total_projects)]
numbers = list(range(1, total_projects + 1))
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

# Dynamic room creation
projects_per_room = math.ceil(total_projects / num_rooms)
rooms = []
for i in range(num_rooms):
    start_idx = i * projects_per_room + 1
    end_idx = min((i + 1) * projects_per_room + 1, total_projects + 1)
    rooms.append(list(range(start_idx, end_idx)))

# Calculate assignments per judge
teams_per_judge = math.ceil((num_teams * x) / num_judges)
teams_per_phase = math.ceil(teams_per_judge / num_rooms)

# Initialize assignments list
assignments = []

# Divide judges evenly across rooms
judges_per_room = [num_judges // num_rooms + (1 if x < num_judges % num_rooms else 0) 
                  for x in range(num_rooms)]
initial_room_assignments = []
for room_idx in range(num_rooms):
    initial_room_assignments.extend([room_idx] * judges_per_room[room_idx])
random.shuffle(initial_room_assignments)

def get_available_teams(room_teams, current_slot_assignments, required_judgings, project_counts):
    """Get teams that can be assigned in current slot"""
    available = []
    for team in room_teams:
        if (team not in current_slot_assignments and 
            project_counts.get(team, 0) < required_judgings):
            available.append(team)
    return available

# Initialize project counting
project_counts = {i: 0 for i in range(1, total_projects + 1)}
assignments = []


def create_balanced_assignments():
    project_counts = {i: 0 for i in range(1, total_projects + 1)}
    judge_counts = {i: 0 for i in range(num_judges)}
    assignments = []
    
    # Calculate target number of projects per judge
    total_judgings = total_projects * x
    target_per_judge = total_judgings // num_judges
    
    for judge_id in range(num_judges):
        judge_assignments = []
        start_room = initial_room_assignments[judge_id]
        remaining_assignments = target_per_judge
        
        # For each phase
        for phase in range(num_rooms):
            current_room = (start_room + phase) % num_rooms
            room_teams = rooms[current_room].copy()
            slots_this_phase = min(teams_per_phase, remaining_assignments)
            
            for slot in range(slots_this_phase):
                current_slot = len(judge_assignments)
                current_slot_assignments = set()
                
                for prev_judge_assignments in assignments:
                    if current_slot < len(prev_judge_assignments):
                        current_slot_assignments.add(prev_judge_assignments[current_slot])
                
                available_teams = get_available_teams(
                    room_teams,
                    current_slot_assignments,
                    x,
                    project_counts
                )
                
                if not available_teams:
                    for other_room in rooms:
                        if other_room != rooms[current_room]:
                            available_teams = get_available_teams(
                                other_room,
                                current_slot_assignments,
                                x,
                                project_counts
                            )
                            if available_teams:
                                break
                
                if available_teams:
                    # Prioritize teams with fewer judgings
                    team = min(available_teams, key=lambda t: project_counts[t])
                    judge_assignments.append(team)
                    project_counts[team] += 1
                    judge_counts[judge_id] += 1
                    remaining_assignments -= 1
                    if team in room_teams:
                        room_teams.remove(team)
                else:
                    judge_assignments.append(-1)
        
        assignments.append(judge_assignments)
    
    # Redistribute any remaining required judgings
    while min(project_counts.values()) < x:
        for judge_id, judge_assignments in enumerate(assignments):
            if judge_counts[judge_id] < target_per_judge + 2:  # Allow slight overload
                for team, count in project_counts.items():
                    if count < x:
                        judge_assignments.append(team)
                        project_counts[team] += 1
                        judge_counts[judge_id] += 1
                        break
    
    return assignments

def create_and_verify_assignments(total_projects, num_rooms, x, teams, judges):
    """Create assignments and verify they meet all requirements"""
    # Create DataFrame from assignments
    assignments = create_balanced_assignments()
    df = pd.DataFrame(assignments)
    df.index.name = 'Judge'
    
    # Format DataFrame
    df = df.fillna(-1)
    df = df.astype(int)
    max_teams = df.apply(lambda x: x[x != -1].count(), axis=1).max()
    df.columns = [f'Slot {i+1}' for i in range(max_teams)]
    
    # Replace numbers with team names and table numbers
    for i in range(max_teams):
        df[f'Slot {i+1}'] = df[f'Slot {i+1}'].apply(
            lambda x: f'{teams.loc[x-1, "teamName"]} (Table {teams.loc[x-1, "tableNumber"]})' 
            if x != -1 else 'No team for this time slot'
        )
    
    # Add judge information
    df.insert(0, 'Judge ID', range(1001, 1001 + len(df)))
    df.index = df.index.map(lambda x: f'{judges.loc[x, "judgeFirstName"]} {judges.loc[x, "judgeLastName"]}')
    
    # Verify assignments
    judging_issues = verify_judging_count(df, total_projects, x)
    simultaneous_issues = verify_simultaneous_judging(df)
    workload_issues = verify_judge_workload(df)
    
    return df, (judging_issues or simultaneous_issues or workload_issues)

def verify_judge_workload(df):
    """Verify each judge has approximately equal number of assignments"""
    judge_counts = {}
    for idx in df.index:
        # Count non-empty slots for each judge
        count = df.loc[idx].apply(lambda x: x != 'No team for this time slot' if isinstance(x, str) else False).sum() - 1  # Subtract 1 to account for Judge ID column
        judge_counts[idx] = count
    
    avg_load = sum(judge_counts.values()) / len(judge_counts)
    max_deviation = 2  # Allow up to 2 projects difference
    
    issues = []
    for judge, count in judge_counts.items():
        if abs(count - avg_load) > max_deviation:
            issues.append(f"Judge {judge} has {count} projects (average is {avg_load:.1f})")
    
    return issues


def verify_judging_count(df, total_projects, required_judgings):
    """Verify each project is judged exactly required_judgings times"""
    # Extract project numbers from the slot strings
    project_counts = {}
    for col in df.columns:
        if col.startswith('Slot'):
            for cell in df[col]:
                if cell != 'No team for this time slot':
                    table_num = int(cell.split('Table ')[-1].strip(')'))
                    project_counts[table_num] = project_counts.get(table_num, 0) + 1
    
    # Check if any project is not judged exactly x times
    issues = []
    for i in range(1, total_projects + 1):
        count = project_counts.get(i, 0)
        if count != required_judgings:
            issues.append(f"Project {i} is judged {count} times (should be {required_judgings})")
    
    return issues

def verify_simultaneous_judging(df):
    """Verify no project is judged by multiple judges in the same slot"""
    issues = []
    for col in df.columns:
        if col.startswith('Slot'):
            # Get all projects in this slot
            slot_projects = df[col].tolist()
            # Extract table numbers
            table_numbers = []
            for proj in slot_projects:
                if proj != 'No team for this time slot':
                    table_num = int(proj.split('Table ')[-1].strip(')'))
                    table_numbers.append(table_num)
            # Check for duplicates
            seen = set()
            duplicates = set()
            for num in table_numbers:
                if num in seen:
                    duplicates.add(num)
                seen.add(num)
            if duplicates:
                issues.append(f"In {col}, projects at tables {duplicates} are being judged simultaneously")
    
    return issues

# Replace the assignment creation and verification section with retry logic
max_attempts = 10
attempt = 1
success = False

while attempt <= max_attempts and not success:
    print(f"\nAttempt {attempt} of {max_attempts}")
    df, has_issues = create_and_verify_assignments(total_projects, num_rooms, x, teams, judges)
    
    if not has_issues:
        print("All verifications passed successfully!")
        success = True
    else:
        print("\nWarning: Issues found in assignments:")
        judging_issues = verify_judging_count(df, total_projects, x)
        simultaneous_issues = verify_simultaneous_judging(df)
        workload_issues = verify_judge_workload(df)
        
        for issue in judging_issues:
            print("- " + issue)
        for issue in simultaneous_issues:
            print("- " + issue)
        for issue in workload_issues:
            print("- " + issue)
        
        if attempt == max_attempts:
            print("\nFailed to generate valid assignments after maximum attempts")
        else:
            print("\nRetrying assignment generation...")
    
    attempt += 1

# Save the final DataFrame to CSV
df.to_csv('assignments.csv')
print("Saved assignments to 'assignments.csv'")
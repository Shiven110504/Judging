#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
import math
import random
import pandas as pd
import string

@dataclass
class Project:
    name: str
    table_number: int

@dataclass
class Judge:
    first_name: str
    last_name: str
    judge_id: int

@dataclass
class Room:
    room_id: int
    projects: List[int]

class JudgingSystem:
    def __init__(self, num_judges: int, total_projects: int, num_rooms: int, judgings_per_project: int = 3, demo_mode: bool = False):
        self.num_judges = num_judges
        self.total_projects = total_projects
        self.num_rooms = num_rooms
        self.judgings_per_project = judgings_per_project
        self.demo_mode = demo_mode
        
        self.judges = self._initialize_judges()
        self.projects = self._initialize_projects()
        self.rooms = self._create_rooms()
        
    def _initialize_judges(self) -> List[Judge]:
        if self.demo_mode:
            return self._generate_demo_judges()
        return self._load_judges_from_csv()
    
    def _initialize_projects(self) -> List[Project]:
        if self.demo_mode:
            return self._generate_demo_projects()
        return self._load_projects_from_csv()
    
    def _generate_demo_judges(self) -> List[Judge]:
        first_names = ['John', 'Jane', 'Mary', 'James', 'Patricia', 'Michael', 'Linda', 'Robert', 'Elizabeth', 'William', 'Jessica', 'David', 'Sarah', 'Thomas']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson']
        judges = []
        for i in range(self.num_judges):
            judge = Judge(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                judge_id=1001 + i
            )
            judges.append(judge)
        return judges
    
    def _generate_demo_projects(self) -> List[Project]:
        projects = []
        for i in range(self.total_projects):
            project = Project(
                name=''.join(random.choices(string.ascii_lowercase, k=3)),
                table_number=i + 1
            )
            projects.append(project)
        return projects
    
    def _load_judges_from_csv(self) -> List[Judge]:
        df = pd.read_csv('judges.csv')
        judges = []
        for i, row in df.iterrows():
            judge = Judge(
                first_name=row['judgeFirstName'],
                last_name=row['judgeLastName'],
                judge_id=1001 + i
            )
            judges.append(judge)
        return judges
    
    def _load_projects_from_csv(self) -> List[Project]:
        df = pd.read_csv('words_numbers.csv')
        projects = []
        for _, row in df.iterrows():
            project = Project(
                name=row['teamName'],
                table_number=row['tableNumber']
            )
            projects.append(project)
        return projects
    
    def _create_rooms(self) -> List[Room]:
        projects_per_room = math.ceil(self.total_projects / self.num_rooms)
        rooms = []
        for i in range(self.num_rooms):
            start_idx = i * projects_per_room + 1
            end_idx = min((i + 1) * projects_per_room + 1, self.total_projects + 1)
            room = Room(
                room_id=i + 1,
                projects=list(range(start_idx, end_idx))
            )
            rooms.append(room)
        return rooms

class AssignmentGenerator:
    def __init__(self, system: JudgingSystem):
        self.system = system
        self.assignments = []
        self.project_counts = {i: 0 for i in range(1, system.total_projects + 1)}
        self.judge_counts = {i: 0 for i in range(system.num_judges)}
        
        # Calculate total judgings needed
        self.total_judgings = system.total_projects * system.judgings_per_project
        
        # Calculate base and extra assignments per judge
        self.base_per_judge = self.total_judgings // system.num_judges
        self.extra_assignments = self.total_judgings % system.num_judges
        
        # Calculate judge distribution across rooms
        self.judges_per_room = [system.num_judges // system.num_rooms + 
                              (1 if x < system.num_judges % system.num_rooms else 0) 
                              for x in range(system.num_rooms)]
        
        # Initial room assignments for judges
        self.initial_room_assignments = []
        for room_idx in range(system.num_rooms):
            self.initial_room_assignments.extend([room_idx] * self.judges_per_room[room_idx])
        random.shuffle(self.initial_room_assignments)
        
        # Calculate assignments per phase
        self.max_per_judge = self.base_per_judge + (1 if self.extra_assignments > 0 else 0)
        self.teams_per_phase = math.ceil(self.max_per_judge / system.num_rooms)

    def _get_target_assignments(self, judge_id: int) -> int:
        # First extra_assignments judges get one extra assignment
        return self.base_per_judge + (1 if judge_id < self.extra_assignments else 0)

    def _create_balanced_assignments(self):
        for judge_id in range(self.system.num_judges):
            judge_assignments = []
            start_room = self.initial_room_assignments[judge_id]
            target_assignments = self._get_target_assignments(judge_id)
            remaining_assignments = target_assignments
            
            for phase in range(self.system.num_rooms):
                current_room = (start_room + phase) % self.system.num_rooms
                room_teams = self.system.rooms[current_room].projects.copy()
                slots_this_phase = min(self.teams_per_phase, remaining_assignments)
                
                for slot in range(slots_this_phase):
                    current_slot = len(judge_assignments)
                    current_slot_assignments = set()
                    
                    for prev_judge_assignments in self.assignments:
                        if current_slot < len(prev_judge_assignments):
                            current_slot_assignments.add(prev_judge_assignments[current_slot])
                    
                    available_teams = self._get_available_teams(room_teams, current_slot_assignments)
                    
                    if not available_teams:
                        for other_room in self.system.rooms:
                            if other_room.projects != room_teams:
                                available_teams = self._get_available_teams(
                                    other_room.projects,
                                    current_slot_assignments
                                )
                                if available_teams:
                                    break
                    
                    if available_teams:
                        team = min(available_teams, key=lambda t: self.project_counts[t])
                        judge_assignments.append(team)
                        self.project_counts[team] += 1
                        self.judge_counts[judge_id] += 1
                        remaining_assignments -= 1
                        if team in room_teams:
                            room_teams.remove(team)
                    else:
                        judge_assignments.append(-1)
            
            self.assignments.append(judge_assignments)

    def _get_available_teams(self, room_teams: List[int], current_slot_assignments: Set[int]) -> List[int]:
        """
        Returns a list of teams that are available to be judged in the current slot.
        A team is available if:
        1. It's in the current room's team list
        2. It's not already being judged in this time slot
        3. It hasn't reached its maximum number of judgings
        """
        available = []
        for team in room_teams:
            if (team not in current_slot_assignments and 
                self.project_counts.get(team, 0) < self.system.judgings_per_project):
                available.append(team)
        return available

    def _create_assignment_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame(self.assignments)
        df.index.name = 'Judge'
        
        # Format DataFrame
        df = df.fillna(-1)
        df = df.astype(int)
        max_teams = df.apply(lambda x: x[x != -1].count(), axis=1).max()
        df.columns = [f'Slot {i+1}' for i in range(max_teams)]
        
        # Replace numbers with team names and table numbers
        for i in range(max_teams):
            df[f'Slot {i+1}'] = df[f'Slot {i+1}'].apply(
                lambda x: f'{self.system.projects[x-1].name} (Table {self.system.projects[x-1].table_number})' 
                if x != -1 else 'No team for this time slot'
            )
        
        # Add judge information
        df.insert(0, 'Judge ID', range(1001, 1001 + len(df)))
        df.index = df.index.map(lambda x: f'{self.system.judges[x].first_name} {self.system.judges[x].last_name}')
        
        return df

    def generate_assignments(self) -> pd.DataFrame:
        self._create_balanced_assignments()
        return self._create_assignment_dataframe()

class AssignmentVerifier:
    def __init__(self, df: pd.DataFrame, system: JudgingSystem):
        self.df = df
        self.system = system
    
    def _verify_judging_count(self) -> List[str]:
        project_counts = {}
        for col in self.df.columns:
            if col.startswith('Slot'):
                for cell in self.df[col]:
                    if cell != 'No team for this time slot':
                        table_num = int(cell.split('Table ')[-1].strip(')'))
                        project_counts[table_num] = project_counts.get(table_num, 0) + 1
        
        issues = []
        for i in range(1, self.system.total_projects + 1):
            count = project_counts.get(i, 0)
            if count != self.system.judgings_per_project:
                issues.append(f"Project {i} is judged {count} times (should be {self.system.judgings_per_project})")
        
        return issues
    
    def _verify_simultaneous_judging(self) -> List[str]:
        issues = []
        for col in self.df.columns:
            if col.startswith('Slot'):
                slot_projects = self.df[col].tolist()
                table_numbers = []
                for proj in slot_projects:
                    if proj != 'No team for this time slot':
                        table_num = int(proj.split('Table ')[-1].strip(')'))
                        table_numbers.append(table_num)
                seen = set()
                duplicates = set()
                for num in table_numbers:
                    if num in seen:
                        duplicates.add(num)
                    seen.add(num)
                if duplicates:
                    issues.append(f"In {col}, projects at tables {duplicates} are being judged simultaneously")
        return issues
    
    def _verify_judge_workload(self) -> List[str]:
        # Exclude 'Judge ID' column
        assignment_columns = [col for col in self.df.columns if col.startswith('Slot')]
        # Calculate the count of assignments for each judge
        judge_counts = self.df[assignment_columns].apply(
            lambda row: row[row != 'No team for this time slot'].count(), axis=1
        ).to_dict()

        avg_load = sum(judge_counts.values()) / len(judge_counts)
        max_deviation = 2

        issues = []
        for judge, count in judge_counts.items():
            if abs(count - avg_load) > max_deviation:
                issues.append(f"Judge {judge} has {count} projects (average is {avg_load:.1f})")

        return issues
    
    def verify_all(self) -> Tuple[bool, List[str]]:
        issues = []
        issues.extend(self._verify_judging_count())
        issues.extend(self._verify_simultaneous_judging())
        issues.extend(self._verify_judge_workload())
        return len(issues) == 0, issues

def main():
    # Get input parameters
    num_judges = int(input("Enter number of judges: "))
    total_projects = int(input("Enter total number of projects: "))
    num_rooms = int(input("Enter number of rooms: "))
    demo_mode = input("Run in demo mode? (y/n): ").lower() == 'y'
    
    # Initialize system
    system = JudgingSystem(num_judges, total_projects, num_rooms, demo_mode=demo_mode)
    
    # Generate and verify assignments with retries
    max_attempts = 10
    attempt = 1
    success = False
    
    while attempt <= max_attempts and not success:
        print(f"\nAttempt {attempt} of {max_attempts}")
        
        generator = AssignmentGenerator(system)
        df = generator.generate_assignments()
        
        verifier = AssignmentVerifier(df, system)
        success, issues = verifier.verify_all()
        
        if success:
            print("All verifications passed successfully!")
        else:
            print("\nWarning: Issues found in assignments:")
            for issue in issues:
                print("- " + issue)
            
            if attempt == max_attempts:
                print("\nFailed to generate valid assignments after maximum attempts")
            else:
                print("\nRetrying assignment generation...")
        
        attempt += 1
    
    # Save final assignments
    if success:
        # Save final assignments
        df.to_csv('assignments.csv')
        print("Saved assignments to 'assignments.csv'")
    else:
        print("No valid assignments could be generated.")

if __name__ == "__main__":
    main()
# Judging System Assignment Generator

This project is a Python application designed to generate balanced and fair assignment schedules for judges to evaluate projects in a competition or fair setting. It ensures that each project is judged a specified number of times, judges have balanced workloads, and no project is judged by multiple judges simultaneously.

## Table of Contents
- [Features](#features)
- [Usage](#usage)
- [Input Requirements](#input-requirements)
- [Algorithm Logic](#algorithm-logic)
- [Output Format](#output-format)
- [Bottlenecks and Drawbacks](#bottlenecks-and-drawbacks)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Customization](#customization)
- [License](#license)

## Features

- **Dynamic Judge and Project Allocation**: Supports any number of judges, projects, and rooms.
- **Balanced Assignments**: Ensures that each project is judged the specified number of times and that judges have balanced workloads.
- **Conflict Avoidance**: Prevents a project from being judged by multiple judges at the same time.
- **Room Distribution**: Distributes judges across rooms and rotates them to ensure exposure to different projects.
- **Verification System**: Validates the generated assignments for correctness and fairness.
- **Demo Mode**: Allows running the application without external CSV files, using randomly generated judges and projects.
- **CSV Export**: Exports the final assignments to a CSV file for easy distribution and review.

## Usage

The application is intended for organizers of events where projects (e.g., science fairs, hackathons) need to be evaluated by a panel of judges. By inputting the number of judges, projects, and rooms, the system generates a schedule that:
  
  - Assigns judges to projects fairly.
  - Ensures each project is evaluated a consistent number of times.
  - Balances the workload among judges.
  - Prevents scheduling conflicts.

## Input Requirements

The application requires the following inputs:

1. **Number of Judges**: Total number of judges available for the event.
2. **Total Number of Projects**: Total number of projects that need to be evaluated.
3. **Number of Rooms**: Number of rooms where projects are displayed.
4. **Demo Mode**: Option to run in demo mode (`y` or `n`).

### CSV Files (Non-Demo Mode)

If not running in demo mode, the application expects two CSV files in the working directory:

- `judges.csv`: Contains the first and last names of the judges.
  - Columns: `judgeFirstName`, `judgeLastName`
  
- `words_numbers.csv`: Contains the project names and their corresponding table numbers.
  - Columns: `teamName`, `tableNumber`

## Algorithm Logic

### JudgingSystem Class

#### Initialization
Sets up the system based on input parameters.

#### Judge Initialization
  - In demo mode, generates random judge names.
  - In non-demo mode, loads judges from `judges.csv`.

#### Project Initialization
  - In demo mode, generates random project names and table numbers.
  - In non-demo mode, loads projects from `words_numbers.csv`.

#### Room Creation
Distributes projects evenly across the specified number of rooms.

### AssignmentGenerator Class

#### Initialization
  - Calculates the total number of judgings needed.
  - Determines the base number of assignments per judge and extra assignments to distribute.
  - Calculates how judges are distributed across rooms.
  - Determines the maximum number of assignments per judge and teams per phase.

#### Assignment Generation (_create_balanced_assignments)
Iterates over each judge to create their schedule. Rotates judges through different rooms to ensure exposure to various projects. Assigns projects to judges while:
  
  - Ensuring no project exceeds the maximum number of judgings.
  - Avoiding assigning a project to multiple judges in the same time slot.
  - Balancing workloads among judges.

#### Helper Methods
  - `_get_target_assignments`: Determines the total assignments a judge should have.
  - `_get_available_teams`: Retrieves a list of projects available for assignment in the current slot.

#### DataFrame Creation (_create_assignment_dataframe)
Formats the assignments into a pandas DataFrame. Replaces project IDs with project names and table numbers. Adds judge information for clarity.

### AssignmentVerifier Class

#### Verification Methods
  - `_verify_judging_count`: Checks that each project is judged the correct number of times.
  - `_verify_simultaneous_judging`: Ensures no project is scheduled to be judged by multiple judges at the same time.
  - `_verify_judge_workload`: Confirms that judge workloads are balanced within an acceptable deviation.

#### Verification Process (verify_all)
Runs all verification methods and aggregates any issues found.

### Main Function

1. **User Input**: Prompts the user for input parameters.
2. **System Initialization**: Creates an instance of JudgingSystem.
3. **Assignment Generation and Verification**:
   - Attempts to generate valid assignments up to a maximum number of attempts (default 10).
   - If valid assignments are generated, saves them to a CSV file.
   - If not, informs the user that valid assignments could not be generated.

## Output Format

The final output is a CSV file named `assignments.csv`, containing the assignment schedule. The CSV includes:

- **Judge ID**: Unique identifier for each judge.
- **Judge Name**: Full name of the judge (index column).
  
Each column represents a time slot. Entries include:
  
  - Project name and table number assigned to each judge for that slot.
  
If no assignment is available for a slot, it is indicated as “No team for this time slot”.

### Sample Output

```csv
Judge ID,Slot 1,Slot 2,Slot 3,Slot 4
1001,Alpha (Table 1),Delta (Table 4),Echo (Table 5),No team for this time slot
1002,Bravo (Table 2),Charlie (Table 3),Foxtrot (Table 6),Golf (Table 7)
```

## Bottlenecks and Drawbacks

### Performance with Large Inputs
The algorithm may experience performance issues with a very high number of judges or projects due to increased computational complexity.

### Randomization
The assignment relies on randomization, which may lead to non-deterministic outcomes between runs.

### Limited Conflict Resolution
The algorithm tries to resolve conflicts by searching other rooms if no available teams are found in the current room, which may not always find a solution.

### Maximum Attempts
The system retries assignment generation up to a fixed number of attempts (default 10). In complex scenarios, this may not be sufficient to find a valid assignment.

## Installation

### Prerequisites
- Python 3.x
- Required Python packages:
    ```bash
    pip install pandas
    ```

## Running the Application

1. Clone or Download the Repository: Ensure all code files are in your working directory.

2. Prepare CSV Files (Non-Demo Mode):
   Ensure `judges.csv` and `words_numbers.csv` are present in your working directory with correct formatting.

3. Run the Application:
    ```bash
    python3 assignment_generator.py
    ```

4. Provide Input When Prompted:
   - Number of Judges: Enter an integer value.
   - Total Number of Projects: Enter an integer value.
   - Number of Rooms: Enter an integer value.
   - Demo Mode: Enter `y` or `n`.

5. Review Output:
   The application will attempt to generate valid assignments:
   - If successful, assignments are saved to `assignments.csv`.
   - If unsuccessful after maximum attempts, it will inform you that valid assignments could not be generated.

## Customization

### Adjusting Judgings per Project
By default, each project is judged three times. To adjust this:

```python
system = JudgingSystem(num_judges, total_projects, num_rooms,
                       judgings_per_project=desired_number,
                       demo_mode=demo_mode)
```

### Changing Maximum Attempts
If valid assignments are not being generated within default attempts, increase `max_attempts` in `main()` function:

```python
max_attempts = desired_number_of_attempts
```

## License

This project is licensed under the MIT License – see LICENSE file for details.

---

Note: Ensure that CSV files used in non-demo mode are correctly formatted with accurate data to prevent runtime errors. Consider implementing exception handling around file operations for robustness.

from hyperon import MeTTa

# Initialize MeTTa AI Engine
metta = MeTTa()

# Function to add a task dynamically
def add_task():
    name = input("Enter Task Name: ")
    deadline = input("Enter Deadline (YYYY-MM-DD, optional): ") or None
    priority = input("Enter Priority (low, medium, high): ").lower() or "medium"
    before = input("Enter a Task that this should be done before (optional): ") or None
    # Construct MeTTa rule
    task_def = f'(-> (task "{name}")'
    if deadline:
        task_def += f' (deadline "{deadline}")'
    if priority:
        task_def += f' (priority {priority})'
    if before:
        task_def += f' (before "{before}")'
    task_def += ')'

    # Store in MeTTa
    metta.run(task_def)
    print(f"\nTask '{name}' added successfully!\n")

# Function to get ordered task list based on dependencies
def get_task_order():
    result = metta.run('(query (task ?task) (before ?dependency))')
    
    if result:
        print("\nOptimal Task Sequence:")
        ordered_tasks = set()
        for item in result:
            ordered_tasks.add(item[1])
            ordered_tasks.add(item[2])
            print(f" - {item[1]} should be done before {item[2]}")
        
        print("\nOverall Task Order:", " → ".join(ordered_tasks))
    else:
        print("\nNo dependencies found. Tasks can be done in any order.")

# Function to recommend next best task
def get_next_task():
    recommendation = metta.run('(query (task ?task) (priority high))')
    if recommendation:
        print(f"\nRecommended Next Task: {recommendation[0][1]}")
    else:
        print("\nNo high-priority tasks found. Proceed with available tasks.")

# Main Program
print("\nWelcome to Smart To-Do Task Scheduler with MeTTa\n")

while True:
    print("\nOptions:")
    print("1. Add Task")
    print("2. View Task Order")
    print("3. Get Next Best Task")
    print("4. Exit")

    choice = input("\nEnter your choice (1-4): ")

    if choice == "1":
        add_task()
    elif choice == "2":
        get_task_order()
    elif choice == "3":
        get_next_task()
    elif choice == "4":
        print("\nExiting... Have a productive day!")
        break
    else:
        print("\nInvalid choice! Please enter a number between 1 and 4.")

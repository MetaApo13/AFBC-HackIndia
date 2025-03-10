from hyperon import MeTTa  # Placeholder for future AI-powered automation

from datetime import datetime

class Task:
    def __init__(self, name, due_date, priority, dependencies=None):
        """
        Initializes a new task.
        :param name: Task name
        :param due_date: Due date (YYYY-MM-DD format)
        :param priority: low, medium, high
        :param dependencies: List of other task names that must be completed first
        """
        self.name = name
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d")
        self.priority = priority
        self.dependencies = dependencies if dependencies else []

    def __repr__(self):
        deps = ", ".join(self.dependencies) if self.dependencies else "None"
        return f"{self.name} | Due: {self.due_date.date()} | Priority: {self.priority} | Dependencies: {deps}"

class SmartTodo:
    def __init__(self):
        self.tasks = []

    def add_task(self, name, due_date, priority, dependencies=None):
        """Adds a new task to the list."""
        new_task = Task(name, due_date, priority, dependencies)
        self.tasks.append(new_task)
        print(f"✅ Task '{name}' added successfully!\n")

    def view_tasks(self, sort_by="name"):
        """Displays tasks sorted by name, due date, priority, or dependencies."""
        if not self.tasks:
            print("📭 No tasks found!\n")
            return

        if sort_by == "name":
            self.tasks.sort(key=lambda t: t.name.lower())
        elif sort_by == "due_date":
            self.tasks.sort(key=lambda t: t.due_date)
        elif sort_by == "priority":
            priority_order = {"high": 1, "medium": 2, "low": 3}
            self.tasks.sort(key=lambda t: priority_order[t.priority])
        elif sort_by == "dependencies":
            self.tasks.sort(key=lambda t: len(t.dependencies))

        print("\n📌 Your To-Do List:")
        for idx, task in enumerate(self.tasks, 1):
            print(f"{idx}. {task}")

    def remove_task(self, name):
        """Removes a task by name."""
        self.tasks = [task for task in self.tasks if task.name != name]
        print(f"❌ Task '{name}' removed!\n")

def main():
    todo = SmartTodo()

    while True:
        print("\nOptions:")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Remove Task")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            name = input("Enter Task Name: ").strip()
            due_date = input("Enter Due Date (YYYY-MM-DD): ").strip()
            priority = input("Enter Priority (low, medium, high): ").strip().lower()
            dependencies = input("Enter Dependencies (comma-separated, or leave blank): ").strip()
            dependencies = [d.strip() for d in dependencies.split(",")] if dependencies else []
            
            todo.add_task(name, due_date, priority, dependencies)

        elif choice == "2":
            sort_option = input("Sort by name, due_date, priority, or dependencies? ").strip().lower()
            todo.view_tasks(sort_by=sort_option if sort_option in ["name", "due_date", "priority", "dependencies"] else "name")

        elif choice == "3":
            name = input("Enter Task Name to Remove: ").strip()
            todo.remove_task(name)

        elif choice == "4":
            print("Exiting... ✅")
            break

        else:
            print("Invalid choice. Please enter a valid option.\n")

if __name__ == "__main__":
    main()

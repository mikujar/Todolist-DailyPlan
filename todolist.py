import json

# Represents a task with title, category, estimated time, due date, completion status, and subtasks.
class Task:
    def __init__(self,title, category, estimated_time, due_date):
        self.title = title
        self.category = category
        self.estimated_time = estimated_time
        self.due_date = due_date
        self.completed = False
        self.subtasks = []

    # Mark this task as completed.
    def mark_completed(self):
        self.completed = True

    # Add a subtask to this task.
    def add_subtask(self, subtask):
        self.subtasks.append(subtask)

    # Calculate completion progress as percentage based on subtasks or task completion.
    def get_progress(self):
        if self.subtasks:
            completed_subtasks = 0
            for subtask in self.subtasks:
                if subtask.completed:
                    completed_subtasks += 1
            return completed_subtasks/len(self.subtasks) * 100
        else:
            if self.completed:
                return 100
            else:
                return 0

    # Convert task and subtasks into a dictionary for JSON serialization.
    def to_dict(self):
        return {
            "title": self.title,
            "category": self.category,
            "estimated_time": self.estimated_time,
            "due_date": self.due_date,
            "completed": self.completed,
            "subtasks": [sub.to_dict() for sub in self.subtasks]
        }

    # Create a Task instance from a dictionary (deserialization).
    @staticmethod
    def from_dict(data):
        task = Task(
            title=data.get("title", "Untitled"),
            category=data.get("category", "Uncategorized"),
            estimated_time=data.get("estimated_time", 0),
            due_date=data.get("due_date", None)
        )
        task.completed = data.get("completed", False)
        task.subtasks = [Task.from_dict(sub) for sub in data.get("subtasks", [])]
        return task

    # String representation showing title, due date, and estimated time.
    def __str__(self):
        return f"{self.title} {self.due_date} {self.estimated_time}min"

# Manages a collection of tasks, providing operations like add, delete, mark, and save/load.
class TaskManager:
    def __init__(self):
        self.tasks = []

    # Calculate average progress across all tasks.
    def get_overall_progress(self):
        if not self.tasks:
            return 0
        sum_progress = 0
        for task in self.tasks:
            sum_progress += task.get_progress()
        return sum_progress/len(self.tasks)

    # Print all tasks and subtasks with their completion status and overall progress.
    def list_tasks(self):
        if not self.tasks:
            print("No tasks found")
            return
        for index, task in enumerate(self.tasks, 1):
            if task.completed == True:
                status = "[✓]"
            else:
                status = "[ ]"
            print(f"{status}{index} {task}")
            for subindex, subtask in enumerate(task.subtasks, 1):
                if subtask.completed == True:
                    status = "[✓]"
                else:
                    status = "[ ]"
                print(f"   {status}{index}.{subindex} {subtask}")
        print(f"Progress: {self.get_overall_progress():.2f}%")

    # Add a new task to the list.
    def add_task(self, task):
        self.tasks.append(task)

    # Add a subtask to a specific task by index.
    def add_subtask(self, index, subtask):
        self.tasks[index].add_subtask(subtask)

    # Mark a task or subtask as completed based on index string (e.g., '1' or '1.1').
    def mark_completed(self, index):
        parts = index.split(".")
        task_index = int(parts[0]) - 1
        if len(parts) == 1:
            self.tasks[task_index].mark_completed()
        elif len(parts) == 2:
            subtask_index = int(parts[1]) - 1
            self.tasks[task_index].subtasks[subtask_index].mark_completed()

    # Mark a task or subtask as uncompleted based on index string.
    def mark_uncompleted(self, index):
        parts = index.split(".")
        task_index = int(parts[0]) - 1
        if len(parts) == 1:
            self.tasks[task_index].completed = False
        elif len(parts) == 2:
            subtask_index = int(parts[1]) - 1
            self.tasks[task_index].subtasks[subtask_index].completed = False

    # Delete a task or subtask based on index string.
    def delete_task(self, index):
        parts = index.split(".")
        task_index = int(parts[0]) - 1
        if len(parts) == 1:
            self.tasks.pop(task_index)
        if len(parts) == 2:
            subtask_index = int(parts[1]) - 1
            self.tasks[task_index].subtasks.pop(subtask_index)

    # Save all tasks to a JSON file.
    def save_file(self, filename="tasks.json"):
        data = [task.to_dict() for task in self.tasks]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Load tasks from a JSON file, or start with empty if file not found.
    def load_file(self, filename="tasks.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = [Task.from_dict(task_dict) for task_dict in data]
        except FileNotFoundError:
            self.tasks = []

# Main interactive loop for the to-do list application.
def main():
    todolist = TaskManager()
    todolist.load_file()

    while True:
        print("\n=== To-Do List ===")
        todolist.list_tasks()
        print()
        print("1. Add a task")
        print("2. Add a subtask")
        print("3. Mark completed")
        print("4. Mark uncompleted")
        print("5. Delete a task")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter your task's title: ")
            category = input("Enter your task's category: ")
            estimated_time = input("Enter your task's estimated time[min]: ")
            due_date = input("Enter your task's due date: ")
            task = Task(title, category, estimated_time, due_date)
            todolist.add_task(task)
            todolist.save_file()
            continue
        elif choice == "2":
            index = input("Enter your task's index: ")
            title = input("Enter your subtask's title: ")
            estimated_time = input("Enter your subtask's estimated time[min]: ")
            due_date = input("Enter your subtask's due date: ")
            task = todolist.tasks[int(index)-1]
            subtask = Task(title, task.category, estimated_time, due_date)
            todolist.add_subtask(int(index)-1, subtask)
            todolist.save_file()
            continue
        elif choice == "3":
            index = input("Enter your task's index [like 1 or 1.1]: ")
            todolist.mark_completed(index)
            todolist.list_tasks()
            todolist.save_file()
            continue
        elif choice == "4":
            index = input("Enter your task's index [like 1 or 1.1]: ")
            todolist.mark_uncompleted(index)
            todolist.list_tasks()
            todolist.save_file()
            continue
        elif choice == "5":
            index = input("Enter your task's index [like 1 or 1.1]: ")
            todolist.delete_task(index)
            todolist.list_tasks()
            todolist.save_file()
            continue
        elif choice == "6":
            break


if __name__ == "__main__":
    main()
from todolist import Task, TaskManager
import json,os

class TimeBlock:
    # Represents a block of time with a category and assigned tasks
    def __init__(self, time_range, category):
        self.time_range = time_range
        self.category = category
        self.assigned_tasks = []  # List of (task, start_time, end_time)

    def __str__(self):
        output = f"{self.time_range} ({self.category}):"
        for task, start, end in self.assigned_tasks:
            output += f"\n  {start}-{end} {task.title}"
        return output

class DailyPlanner:
    # Manages daily planning based on a template and task manager
    def __init__(self, task_manager, template, mode):
        self.task_manager = task_manager
        self.template = template  # dict like {"08:00–10:00": "Study", ...}
        self.mode = mode

    def _parse_duration(self, time_range):
        # Calculate duration in minutes from time range string
        start, end = time_range.split("-")
        h1, m1 = map(int, start.split(":"))
        h2, m2 = map(int, end.split(":"))
        return (h2 * 60 + m2) - (h1 * 60 + m1)

    def _minutes_to_time(self, base_minutes):
        # Convert minutes since midnight to HH:MM string
        h = base_minutes // 60
        m = base_minutes % 60
        return f"{h:02d}:{m:02d}"

    def generate_plan(self, mode):
        # Generate a daily plan with tasks assigned to time blocks
        if mode == "normal":
            multiplier = 1.25
        elif mode == "relaxed":
            multiplier = 1.5
        plan = []

        for time_range, category in self.template.items():
            block = TimeBlock(time_range, category)
            time_available = self._parse_duration(time_range)
            start_str, _ = time_range.split("-")
            h, m = map(int, start_str.split(":"))
            current_minutes = h * 60 + m

            time_remaining = time_available
            for task in self.task_manager.tasks:
                if task.category == category and not task.completed:
                    est = int(task.estimated_time) * multiplier
                    if time_remaining >= est:
                        start_time = self._minutes_to_time(current_minutes)
                        end_time = self._minutes_to_time(current_minutes + int(est))
                        block.assigned_tasks.append((task, start_time, end_time))
                        current_minutes += int(est)
                        time_remaining -= est

            plan.append(block)

        return plan

    @staticmethod
    def collect_template_from_input():
        # Collect time template from user input
        print("Please enter time template（enter space to exit）")
        print("Format：08:00-10:00 Study")

        template = {}
        while True:
            line = input("> ").strip()
            if not line:
                break
            try:
                time_range, category = line.split()
                if "-" not in time_range:
                    print("Format should be HH:MM-HH:MM")
                    continue
                template[time_range] = category
            except ValueError:
                print("Format should be HH:MM-HH:MM")
            return template

def main():
    # Main program flow: load or create template, load tasks, generate and print plan
    if os.path.exists("template.json"):
        use_saved = input("Use saved template？[y/n]: ").strip().lower()
        if use_saved == "y":
            with open("template.json", "r", encoding="utf-8") as f:
                template = json.load(f)
        else:
            template = DailyPlanner.collect_template_from_input()
            with open("template.json", "w", encoding="utf-8") as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
    else:
        template = DailyPlanner.collect_template_from_input()

        with open("template.json", "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=2)

    mode = input("Please choose a mode[normal or relaxed]:")
    todolist = TaskManager()
    todolist.load_file()
    dailyplan = DailyPlanner(todolist,template,mode).generate_plan(mode)

    print("=== Daily Plan ===")
    for block in dailyplan:
        print(block)

if __name__ == "__main__":
    main()
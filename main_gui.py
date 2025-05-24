import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from todolist import Task,TaskManager
from dailyplan import DailyPlanner

# Load tasks
with open("tasks.json", "r", encoding="utf-8") as f:
    data = json.load(f)
tasks = [Task.from_dict(task_dict) for task_dict in data]

def save_tasks_to_json():
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2, ensure_ascii=False)

def get_overall_progress():
    if not tasks:
        return 0
    return sum(t.get_progress() for t in tasks) / len(tasks)

def on_toggle(task, var):
    if var.get():
        task.mark_completed()
    else:
        task.completed = False
    save_tasks_to_json()
    update_progress()
    print(f"{task.title} status updated")

root = ttk.Window(themename="flatly")
root.title("Todolist + DailyPlan by HejiaC")
root.geometry("500x500+100+100")
root.configure(bg="#ffffff")

tabs = ttk.Notebook(root)
todo_tab = ttk.Frame(tabs)
plan_tab = ttk.Frame(tabs)
tabs.add(todo_tab, text="To-Do List")
tabs.add(plan_tab, text="Daily Plan")
tabs.pack(fill=BOTH, expand=True)

# Top progress bar
top_frame = ttk.Frame(todo_tab, padding=10)
top_frame.pack(fill=X)

progress_var = ttk.DoubleVar()
progress_bar = ttk.Progressbar(top_frame, variable=progress_var, length=400, bootstyle="danger-striped")
progress_bar.pack(side=LEFT, padx=10)
progress_label = ttk.Label(top_frame, text="0.0%", foreground="red")
progress_label.pack(side=LEFT)

def update_progress():
    percent = get_overall_progress()
    progress_var.set(percent)
    progress_label.config(text=f"{percent:.1f}%")

v = []

# To-Do list frame with scrollable canvas
container_frame = ttk.Frame(todo_tab)
container_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

canvas = ttk.Canvas(container_frame)
canvas.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = ttk.Scrollbar(container_frame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)

# Create an interior frame inside the canvas
list_frame = ttk.Labelframe(canvas, text="To-Do List", padding=10)

# Add the interior frame to the canvas
canvas.create_window((0, 0), window=list_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

list_frame.bind("<Configure>", on_frame_configure)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

for i, task in enumerate(tasks):
    var = ttk.IntVar(value=task.completed)
    v.append(var)
    cb = ttk.Checkbutton(
        list_frame,
        text=f"{i+1}. {task.title} ({task.estimated_time}min)  Due: {task.due_date}",
        variable=var,
        bootstyle="success",
        command=lambda t=task, v=var: on_toggle(t, v)
    )
    cb.pack(anchor="w", padx=10, pady=3)

    for j, sub in enumerate(task.subtasks):
        svar = ttk.IntVar(value=sub.completed)
        v.append(svar)
        scb = ttk.Checkbutton(
            list_frame,
        text=f"{i+1}.{j+1} {sub.title} ({sub.estimated_time}min)  Due: {sub.due_date}",
            variable=svar,
            bootstyle="success",
            command=lambda t=sub, v=svar: on_toggle(t, v)
        )
        scb.pack(anchor="w", padx=30, pady=1)

# Add main task dialog
def show_add_task_dialog():
    dialog = ttk.Toplevel(root)
    dialog.title("Add Task")
    dialog.geometry("300x300")

    ttk.Label(dialog, text="Title:").pack(pady=5)
    title_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=title_var).pack()

    ttk.Label(dialog, text="Category:").pack(pady=5)
    category_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=category_var).pack()

    ttk.Label(dialog, text="Estimated Time (min):").pack(pady=5)
    time_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=time_var).pack()

    ttk.Label(dialog, text="Due Date:").pack(pady=5)
    date_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=date_var).pack()

    def submit():
        title = title_var.get()
        category = category_var.get() or "General"
        est = time_var.get()
        due = date_var.get()
        if not title or not est:
            return
        new_task = Task(title, category, est, due)
        tasks.append(new_task)
        save_tasks_to_json()
        dialog.destroy()
        refresh_tasks()

    ttk.Button(dialog, text="Add", bootstyle="success", command=submit).pack(pady=10)

# Add subtask dialog
def show_add_subtask_dialog():
    if not tasks:
        return
    dialog = ttk.Toplevel(root)
    dialog.title("Add Subtask")
    dialog.geometry("300x300")

    ttk.Label(dialog, text="Task Index (e.g. 1):").pack(pady=5)
    parent_index_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=parent_index_var).pack()

    ttk.Label(dialog, text="Subtask Title:").pack(pady=5)
    title_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=title_var).pack()

    ttk.Label(dialog, text="Estimated Time (min):").pack(pady=5)
    time_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=time_var).pack()

    ttk.Label(dialog, text="Due Date:").pack(pady=5)
    date_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=date_var).pack()

    def submit():
        try:
            idx = int(parent_index_var.get()) - 1
            if idx < 0 or idx >= len(tasks):
                return
            parent_task = tasks[idx]
            subtask = Task(title_var.get(), parent_task.category, time_var.get(), date_var.get())
            parent_task.add_subtask(subtask)
            save_tasks_to_json()
            dialog.destroy()
            refresh_tasks()
        except:
            return

    ttk.Button(dialog, text="Add Subtask", bootstyle="success", command=submit).pack(pady=10)

# Delete task dialog
def show_delete_task_dialog():
    dialog = ttk.Toplevel(root)
    dialog.title("Delete Task")
    dialog.geometry("300x120")

    ttk.Label(dialog, text="Enter Task Number to Delete (e.g. 1 or 1.1):").pack(pady=5)
    task_num_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=task_num_var).pack()

    def submit():
        task_num = task_num_var.get().strip()
        if not task_num:
            return
        try:
            if '.' in task_num:
                main_idx_str, sub_idx_str = task_num.split('.', 1)
                main_idx = int(main_idx_str) - 1
                sub_idx = int(sub_idx_str) - 1
                if 0 <= main_idx < len(tasks):
                    if 0 <= sub_idx < len(tasks[main_idx].subtasks):
                        del tasks[main_idx].subtasks[sub_idx]
                    else:
                        return
                else:
                    return
            else:
                main_idx = int(task_num) - 1
                if 0 <= main_idx < len(tasks):
                    del tasks[main_idx]
                else:
                    return
            save_tasks_to_json()
            refresh_tasks()
            dialog.destroy()
        except:
            return

    ttk.Button(dialog, text="Delete", bootstyle="danger", command=submit).pack(pady=10)

# Display buttons in one row
button_frame = ttk.Frame(todo_tab)
button_frame.pack(pady=10)

ttk.Button(
    button_frame,
    text="Add Task",
    bootstyle="info",
    command=show_add_task_dialog
).pack(side=LEFT, padx=5)

ttk.Button(
    button_frame,
    text="Add Subtask",
    bootstyle="info",
    command=show_add_subtask_dialog
).pack(side=LEFT, padx=5)

ttk.Button(
    button_frame,
    text="Delete Task",
    bootstyle="danger",
    command=show_delete_task_dialog
).pack(side=LEFT, padx=5)

# Read template.json
try:
    with open("template.json", "r", encoding="utf-8") as f:
        template = json.load(f)
except FileNotFoundError:
    template = {}

# Bind mode
mode_var = ttk.StringVar(value="normal")

# Mode selection row
mode_frame = ttk.Frame(plan_tab)
mode_frame.pack(fill=X, pady=5, padx=10)

ttk.Label(mode_frame, text="Mode:").pack(side=LEFT, padx=5)
ttk.Radiobutton(mode_frame, text="Normal ", variable=mode_var, value="normal").pack(side=LEFT)
ttk.Radiobutton(mode_frame, text="Relax ", variable=mode_var, value="relaxed").pack(side=LEFT)
ttk.Button(mode_frame, text="Generate Plan", bootstyle="info", command=lambda: show_daily_plan()).pack(side=RIGHT, padx=10)

def show_add_template_dialog():
    dialog = ttk.Toplevel(root)
    dialog.title("Add Template")
    dialog.geometry("400x200")

    # Add Entry input fields
    ttk.Label(dialog, text="Timeblock (e.g. 08:00-09:00):").pack(pady=5)
    period_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=period_var).pack()

    ttk.Label(dialog, text="Category (e.g. Study):").pack(pady=5)
    category_var = ttk.StringVar()
    ttk.Entry(dialog, textvariable=category_var).pack()

    # Extendable: add more Entry fields

    def submit():
        # Collect input, assemble as template dictionary
        period = period_var.get().strip()
        category = category_var.get().strip()
        if not period or not category:
            return
        # Read existing template (keep pure dict structure)
        try:
            with open("template.json", "r", encoding="utf-8") as f:
                current_template = json.load(f)
        except FileNotFoundError:
            current_template = {}
        # Only save period: category to dict
        current_template[period] = category
        # Save to template.json, keep pure period: category structure
        with open("template.json", "w", encoding="utf-8") as f:
            json.dump(current_template, f, indent=2, ensure_ascii=False)
        global template
        template.clear()
        template.update(current_template)
        dialog.destroy()

    ttk.Button(dialog, text="Save Template", bootstyle="success", command=submit).pack(pady=20)

# Add "Add Template" button to the mode row, same line as Generate Plan button
add_template_button = ttk.Button(mode_frame, text="Add Template", bootstyle="info", command=show_add_template_dialog)
add_template_button.pack(side=LEFT, padx=20)

# Text area
plan_text = ttk.ScrolledText(plan_tab, width=60, height=20, font=(12))
plan_text.pack(fill=BOTH, expand=True, padx=10, pady=5)

# Function to generate plan
def show_daily_plan():
    plan_text.delete("1.0", "end")
    dailyplan = DailyPlanner(TaskManager(), template, mode_var.get())
    dailyplan.task_manager.load_file()
    plan = dailyplan.generate_plan(mode=mode_var.get())
    for block in plan:
        plan_text.insert("end", str(block) + "\n\n")

# Display template content on GUI startup
update_progress()
show_daily_plan()

# Refresh task list and progress bar
def refresh_tasks():
    # Clear list_frame
    for widget in list_frame.winfo_children():
        widget.destroy()
    v.clear()
    for i, task in enumerate(tasks):
        var = ttk.IntVar(value=task.completed)
        v.append(var)
        cb = ttk.Checkbutton(
            list_frame,
            text=f"{i+1}. {task.title} ({task.estimated_time}min)  Due: {task.due_date}",
            variable=var,
            bootstyle="success",
            command=lambda t=task, v=var: on_toggle(t, v)
        )
        cb.pack(anchor="w", padx=10, pady=3)

        for j, sub in enumerate(task.subtasks):
            svar = ttk.IntVar(value=sub.completed)
            v.append(svar)
            scb = ttk.Checkbutton(
                list_frame,
                text=f"{i+1}.{j+1} {sub.title} ({sub.estimated_time}min)  Due: {sub.due_date}",
                variable=svar,
                bootstyle="success",
                command=lambda t=sub, v=svar: on_toggle(t, v)
            )
            scb.pack(anchor="w", padx=30, pady=1)
    update_progress()

root.mainloop()

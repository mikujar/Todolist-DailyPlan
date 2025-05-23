# Todolist-DailyPlan
COMP9001 Final Project
# 🧠 Structured To-Do Planner

I'm building a **To-Do List application** with structured logic and smart daily planning.

---

## ✅ Core Task Logic

- 🗂️ **Tasks can have subtasks** (optional)
- 📊 **Progress Calculation**:
  - If a task has subtasks → Progress = percentage of completed subtasks
  - If no subtasks → Treated as a binary task: 0% (incomplete) or 100% (complete)

---

## 📈 Overall Progress

- The system shows **overall progress** as the **average of all top-level tasks' progress**

---

## 🏷️ Task Metadata

Each task includes:

- 📚 **Category**: e.g. `Study`, `Work`, `Life`
- ⏱️ **Estimated time** to complete (in minutes)
- 📅 **Optional due date**

---

## 📅 Daily Planning Feature

### 🧠 Idea:

User defines a **daily template** like:

| Time            | Category |
|-----------------|----------|
| 08:00–10:00     | Study    |
| 10:00–12:00     | Creative |
| 14:00–16:00     | Work     |
| 20:00–21:30     | Life     |

---

### ⚙️ Planning Logic:

- 🗃️ Each task has a `category` and `estimated duration`
- 🧮 Apply **realism multiplier**:
  - Normal mode: ×1.25
  - Relaxed mode: ×1.5
- ⛓️ Match tasks into template blocks based on category
- 🗓️ Auto-generate a realistic daily **schedule**

---

## 🧰 Technologies & Topics Covered

- 🧱 **Object-Oriented Programming** (`Task`, `TaskManager`)
- 🔧 Modular functions and design
- 📚 Lists, nested data, control flow
- ⏳ Time formatting and logic
- 💾 *(Optional)* File I/O (e.g. JSON saving/loading)
- 🖼️ *(Optional)* Simple GUI using `tkinter`

---

> 💡 This project balances structured data modeling with real-life task planning — and it's beginner-friendly yet open for expansion!

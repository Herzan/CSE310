"""
Task Manager CLI
-----------------
A simple command-line task manager that stores tasks in a local
SQLite database. Supports adding, listing, completing, editing,
and deleting tasks, plus filtering by status and priority.

Run with: python task_manager.py
"""

import sqlite3
import sys
from datetime import datetime

DB_FILE = "tasks.db"


def get_connection():
    """Open (and create if needed) the SQLite database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Create the tasks table if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'medium',
            due_date TEXT,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task(title, priority="medium", due_date=None):
    """Insert a new task into the database and return its new id."""
    if not title.strip():
        raise ValueError("Task title cannot be empty.")

    priority = priority.lower()
    if priority not in ("low", "medium", "high"):
        raise ValueError("Priority must be low, medium, or high.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tasks (title, priority, due_date, completed, created_at)
           VALUES (?, ?, ?, 0, ?)""",
        (title.strip(), priority, due_date, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def list_tasks(show_completed=True, priority_filter=None):
    """
    Return a list of tasks (as sqlite3.Row objects), optionally filtered
    by completion status and/or priority. Results are ordered so that
    incomplete, high-priority tasks show up first.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if not show_completed:
        query += " AND completed = 0"

    if priority_filter:
        query += " AND priority = ?"
        params.append(priority_filter.lower())

    query += """
        ORDER BY completed ASC,
                 CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                 due_date IS NULL, due_date ASC
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def complete_task(task_id):
    """Mark a task as completed. Returns True if a row was updated."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed


def delete_task(task_id):
    """Delete a task by id. Returns True if a row was removed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed


def edit_task(task_id, title=None, priority=None, due_date=None):
    """Update one or more fields on an existing task."""
    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    params = []
    if title is not None:
        fields.append("title = ?")
        params.append(title.strip())
    if priority is not None:
        priority = priority.lower()
        if priority not in ("low", "medium", "high"):
            raise ValueError("Priority must be low, medium, or high.")
        fields.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        fields.append("due_date = ?")
        params.append(due_date)

    if not fields:
        conn.close()
        return False

    params.append(task_id)
    cursor.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed


def format_task_row(row):
    """Turn a sqlite3.Row task into a single readable display line."""
    status = "[x]" if row["completed"] else "[ ]"
    due = f" (due {row['due_date']})" if row["due_date"] else ""
    return f"{row['id']:>3} {status} ({row['priority']:<6}) {row['title']}{due}"


def print_tasks(rows):
    """Print a list of task rows, or a friendly message if there are none."""
    if not rows:
        print("No tasks found.")
        return
    for row in rows:
        print(format_task_row(row))


def prompt_menu():
    """Display the main menu and return the user's raw choice string."""
    print("\n=== Task Manager ===")
    print("1. Add task")
    print("2. List all tasks")
    print("3. List incomplete tasks")
    print("4. Complete a task")
    print("5. Edit a task")
    print("6. Delete a task")
    print("7. Filter by priority")
    print("8. Quit")
    return input("Choose an option (1-8): ").strip()


def handle_add():
    """Collect input from the user and add a new task."""
    title = input("Task title: ")
    priority = input("Priority (low/medium/high) [medium]: ") or "medium"
    due_date = input("Due date (YYYY-MM-DD) [optional]: ") or None
    try:
        new_id = add_task(title, priority, due_date)
        print(f"Added task #{new_id}.")
    except ValueError as e:
        print(f"Error: {e}")


def handle_complete():
    """Collect a task id from the user and mark it complete."""
    try:
        task_id = int(input("Task id to complete: "))
    except ValueError:
        print("Please enter a valid number.")
        return
    if complete_task(task_id):
        print(f"Task #{task_id} marked complete.")
    else:
        print(f"No task found with id {task_id}.")


def handle_delete():
    """Collect a task id from the user and delete it."""
    try:
        task_id = int(input("Task id to delete: "))
    except ValueError:
        print("Please enter a valid number.")
        return
    if delete_task(task_id):
        print(f"Task #{task_id} deleted.")
    else:
        print(f"No task found with id {task_id}.")


def handle_edit():
    """Collect updated fields from the user and apply them to a task."""
    try:
        task_id = int(input("Task id to edit: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    title = input("New title (leave blank to keep current): ") or None
    priority = input("New priority (leave blank to keep current): ") or None
    due_date = input("New due date (leave blank to keep current): ") or None

    try:
        if edit_task(task_id, title, priority, due_date):
            print(f"Task #{task_id} updated.")
        else:
            print(f"No task found with id {task_id}, or nothing to update.")
    except ValueError as e:
        print(f"Error: {e}")


def handle_filter():
    """Collect a priority level from the user and list matching tasks."""
    priority = input("Filter by priority (low/medium/high): ").strip().lower()
    if priority not in ("low", "medium", "high"):
        print("Please enter low, medium, or high.")
        return
    print_tasks(list_tasks(priority_filter=priority))


def main():
    """Run the interactive task manager loop."""
    init_db()

    actions = {
        "1": handle_add,
        "2": lambda: print_tasks(list_tasks()),
        "3": lambda: print_tasks(list_tasks(show_completed=False)),
        "4": handle_complete,
        "5": handle_edit,
        "6": handle_delete,
        "7": handle_filter,
    }

    while True:
        choice = prompt_menu()
        if choice == "8":
            print("Goodbye!")
            sys.exit(0)
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, please pick 1-8.")


if __name__ == "__main__":
    main()

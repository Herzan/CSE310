# Overview

As a software engineer, I wanted to get hands-on practice using a relational
database from a Python program instead of just storing data in memory or in a
flat file. This project is a command-line **Task Manager** that lets a user
add, list, edit, complete, and delete tasks. Every task (title, priority,
due date, and completion status) is persisted in a local **SQLite** database
file (`tasks.db`), so tasks are still there the next time the program runs.

The purpose of writing this software was to practice:
- Designing a simple relational schema (a single `tasks` table)
- Writing parameterized SQL queries (INSERT, SELECT, UPDATE, DELETE) safely
- Separating data-access functions from the user-interface loop
- Basic input validation and error handling in a CLI

[Software Demo Video]({PASTE_YOUR_VIDEO_LINK_HERE_OR_DELETE_THIS_LINE})

# Relational Database

I used **SQLite** (via Python's built-in `sqlite3` module), so the database
is a single file, `tasks.db`, created automatically the first time the
program runs.

There is one table:

**tasks**
| Column      | Type    | Description                          |
|-------------|---------|---------------------------------------|
| id          | INTEGER | Primary key, auto-incremented         |
| title       | TEXT    | The task description                  |
| priority    | TEXT    | 'low', 'medium', or 'high'            |
| due_date    | TEXT    | Optional due date (YYYY-MM-DD)        |
| completed   | INTEGER | 0 = not done, 1 = done                |
| created_at  | TEXT    | Timestamp the task was created        |

# Development Environment

- **Language:** Python 3
- **Database:** SQLite (via the built-in `sqlite3` library — no external
  install needed)
- **Editor:** {Fill in: VS Code, PyCharm, etc.}
- **Tools used:** Python standard library only (`sqlite3`, `datetime`, `sys`)

# Useful Websites

{Fill in with sites you actually used while building/debugging this.}

- [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite official site](https://www.sqlite.org/index.html)
- [Real Python – Data Management with SQLite and Python](https://realpython.com/python-sqlite-sqlalchemy/)

# Future Work

{Fill in with real, honest next steps once you've run and tested the code.}

- Add a `search` command to find tasks by keyword
- Add unit tests using `pytest` and an in-memory database
- Add categories/tags for tasks in addition to priority
- Support exporting the task list to CSV

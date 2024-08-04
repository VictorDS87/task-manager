import curses
import sqlite3
from datetime import datetime

# TaskManager Doc
# all functions require the "stdscr" parameter, which comes from curses, the library used to make the terminal more dynamic
# functions 
# 1 - __init__ (initialize the database)
# 2 - create_table (create table sqlite)
# 2 - choices (showing the options and redirecting to the specific function)
# 4 - new_task (create new task and add task in sql )
# 5 - view_tasks (Pulls tasks from the database and displays them, with 3 more filter options within the function,
#     being completed, in progress and all. Show description of selected task )
# 6 - edit_task (Shows all tasks and allows you to click on one to edit (starting from scratch) the task title and description)
# 7 - mark_task_completed (Displays all tasks in progress and allows you to change the status of the selected one to completed)
# 8 - mark_task_uncompleted (Displays all tasks completed and allows you to change the status of the selected one to in progress)
# 9 - remove_task (displays all tasks and allows you to select one to remove)


class TaskManager:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
            ''')

    def choices(self, stdscr):
        stdscr.clear()
        
        options = [
            "New Task", 
            "View Tasks", 
            "Edit Task", 
            "Mark Task as Completed", 
            "Mark Task as Uncompleted", 
            "Remove Task", 
            "Exit"
        ]
        
        current_option = 0

        curses.curs_set(0)
        
        while True:
            stdscr.clear()
            
            for idx, option in enumerate(options):
                if idx == current_option:
                    stdscr.addstr(idx, 0, option, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx, 0, option)
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(options) - 1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 0:
                    self.new_task(stdscr)
                elif current_option == 1:
                    self.view_tasks(stdscr)
                elif current_option == 2:
                    self.edit_task(stdscr)
                elif current_option == 3:
                    self.mark_task_completed(stdscr)
                elif current_option == 4:
                    self.mark_task_uncompleted(stdscr)
                elif current_option == 5:
                    self.remove_task(stdscr)
                elif current_option == 6:
                    break


            stdscr.refresh()

    def new_task(self, stdscr):
        curses.echo()
        # get title task
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the title new task: ")
        task = stdscr.getstr().decode('utf-8')
        if not task.strip():
            stdscr.addstr(1, 0, f"Enter a character for the task to be created.")
            stdscr.getch()
            return

        # get description task
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the description new task: ")
        description = stdscr.getstr().decode('utf-8')

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with self.conn:
            self.conn.execute('INSERT INTO tasks (title, description, created_at) VALUES (?, ?, ?)', (task, description, created_at))
        
        stdscr.addstr(1, 0, f"Task '{task}' added. Press any key to return to menu.")
        stdscr.getch()
        curses.noecho()

    def view_tasks(self, stdscr):
        stdscr.clear()
        
        # Custom options for filtering
        filter_options = ["All Tasks", "Completed Tasks", "In Progress Tasks"]
        current_filter = 0

        curses.curs_set(0)
        
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, "Select a filter:")
            
            for idx, option in enumerate(filter_options):
                if idx == current_filter:
                    stdscr.addstr(idx + 1, 0, option, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, option)
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_filter > 0:
                current_filter -= 1
            elif key == curses.KEY_DOWN and current_filter < len(filter_options) - 1:
                current_filter += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                break

        filter_choice = filter_options[current_filter]
        
        # Fetch tasks based on filter choice
        cursor = self.conn.cursor()
        if filter_choice == "All Tasks":
            cursor.execute('SELECT id, title, completed FROM tasks')
        elif filter_choice == "Completed Tasks":
            cursor.execute('SELECT id, title, completed FROM tasks WHERE completed = 1')
        elif filter_choice == "In Progress Tasks":
            cursor.execute('SELECT id, title, completed FROM tasks WHERE completed = 0')

        tasks = cursor.fetchall()
        
        if not tasks:
            stdscr.clear()
            stdscr.addstr(0, 0, "No tasks available. Press any key to return to menu.")
            stdscr.getch()
            return
        
        # Show tasks with their status and show description of selected task
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a task:")
        current_option = 0

        while True:
            stdscr.clear()
            for idx, (task_id, title, completed) in enumerate(tasks):
                status = "Completed" if completed else "In progress"
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, f"{title} - ({status})", curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, f"{title} - ({status})")
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(tasks) - 1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                task_id = tasks[current_option][0]
                cursor.execute('SELECT description FROM tasks WHERE id = ?', (task_id,))
                task_description = cursor.fetchone()[0]
                
                stdscr.clear()
                stdscr.addstr(0, 0, f"Description: {task_description}")
                stdscr.addstr(1, 0, "Press any key to return to menu.")
                stdscr.refresh()
                stdscr.getch()
                break

            stdscr.refresh()

    def edit_task(self, stdscr):
        curses.echo()
        stdscr.clear()
        
        # Get the list of tasks to edit
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM tasks')
        tasks = cursor.fetchall()
        
        if not tasks:
            stdscr.clear()
            stdscr.addstr(0, 0, "No tasks available to edit. Press any key to return to menu.")
            stdscr.getch()
            return
        
        # select a task to edit
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a task to edit:")
        current_option = 0

        while True:
            stdscr.clear()
            for idx, (task_id, title) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, title, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, title)
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(tasks) - 1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                task_id = tasks[current_option][0]
                break

        # Get new title and description
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the new title for the task: ")
        new_title = stdscr.getstr().decode('utf-8')
        
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the new description for the task: ")
        new_description = stdscr.getstr().decode('utf-8')

        # Update the task in the database
        with self.conn:
            self.conn.execute('UPDATE tasks SET title = ?, description = ? WHERE id = ?', (new_title, new_description, task_id))

        stdscr.clear()
        stdscr.addstr(0, 0, f"Task '{new_title}' updated successfully.")
        stdscr.addstr(1, 0, "Press any key to return to menu.")
        stdscr.refresh()
        stdscr.getch()


    def mark_task_completed(self, stdscr):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM tasks WHERE completed = 0')
        tasks = cursor.fetchall()
        
        if not tasks:
            stdscr.clear()
            stdscr.addstr(0, 0, "No tasks available to mark. Press any key to return to menu.")
            stdscr.getch()
            return
        
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a task to mark as completed:")
        current_option = 0

        while True:
            stdscr.clear()
            for idx, (task_id, title) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, title, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, title)
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(tasks) - 1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                task_id = tasks[current_option][0]
                with self.conn:
                    self.conn.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
                stdscr.addstr(len(tasks) + 2, 0, f"Task '{tasks[current_option][1]}' marked as completed. Press any key to return to menu.")
                stdscr.refresh()
                stdscr.getch()
                break

            stdscr.refresh()

    def mark_task_uncompleted(self, stdscr):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM tasks WHERE completed = 1')
        tasks = cursor.fetchall()
        
        if not tasks:
            stdscr.clear()
            stdscr.addstr(0, 0, "No tasks available to mark. Press any key to return to menu.")
            stdscr.getch()
            return
        
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a task to mark as uncompleted:")
        current_option = 0

        while True:
            stdscr.clear()
            for idx, (task_id, title) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, title, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, title)
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(tasks) - 1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                task_id = tasks[current_option][0]
                with self.conn:
                    self.conn.execute('UPDATE tasks SET completed = 0 WHERE id = ?', (task_id,))
                stdscr.addstr(len(tasks) + 2, 0, f"Task '{tasks[current_option][1]}' marked as uncompleted. Press any key to return to menu.")
                stdscr.refresh()
                stdscr.getch()
                break

            stdscr.refresh()

    def remove_task(self, stdscr):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM tasks')
        tasks = cursor.fetchall()
        
        if not tasks:
            stdscr.clear()
            stdscr.addstr(0, 0, "No tasks available to remove. Press any key to return to menu.")
            stdscr.getch()
            return
        
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a task to remove:")
        current_option = 0

        while True:
            stdscr.clear()
            for idx, (task_id, title) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, title, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, title)
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_option > 0:
                current_option -= 1
            elif key == curses.KEY_DOWN and current_option < len(tasks) - 1:
                current_option += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                task_id = tasks[current_option][0]
                with self.conn:
                    self.conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                stdscr.addstr(len(tasks) + 2, 0, f"Task '{tasks[current_option][1]}' removed. Press any key to return to menu.")
                stdscr.refresh()
                stdscr.getch()
                break

            stdscr.refresh()

if __name__ == "__main__":
    main = TaskManager()
    curses.wrapper(main.choices)

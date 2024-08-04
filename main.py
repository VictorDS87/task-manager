import curses
import sqlite3
from datetime import datetime

# RaskManager Doc
# all functions require the "stdscr" parameter, which comes from curses, the library used to make the terminal more dynamic
# functions 
# 1 - __init__ (initialize the database)
# 2 - create_table (create table sqlite)
# 2 - choices (showing the options and redirecting to the specific function)
# 4 - new_task (create new task and add task in sql )
# 5 - view_tasks (Pulls tasks from the database and displays them, with 3 more filter options within the function, being completed, in progress and all )
# 6 - mark_task_completed (Displays all tasks in progress and allows you to change the status of the selected one to completed)
# 7 - mark_task_uncompleted (Displays all tasks completed and allows you to change the status of the selected one to in progress)
# 9 - remove_task (displays all tasks and allows you to select one to remove)


class RaskManager:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    self.mark_task_completed(stdscr)
                elif current_option == 3:
                    self.mark_task_uncompleted(stdscr)
                elif current_option == 4:
                    self.remove_task(stdscr)
                elif current_option == 5:
                    break


            stdscr.refresh()

    def new_task(self, stdscr):
        curses.echo()
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the new task: ")
        task = stdscr.getstr().decode('utf-8')
        if task.strip():
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with self.conn:
                self.conn.execute('INSERT INTO tasks (description, created_at) VALUES (?, ?)', (task, created_at))
            
            stdscr.addstr(1, 0, f"Task '{task}' added. Press any key to return to menu.")
            stdscr.getch()
            curses.noecho()
            return
        stdscr.addstr(1, 0, f"Enter a character for the task to be created.")
        stdscr.getch()

    def view_tasks(self, stdscr):
        stdscr.clear()
        
        # custom options for filtering
        filter_options = ["All Tasks", "Completed Tasks", "Incomplete Tasks"]
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
        
        if filter_choice == "All Tasks":
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, description, completed FROM tasks')
        elif filter_choice == "Completed Tasks":
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, description, completed FROM tasks WHERE completed = 1')
        elif filter_choice == "Incomplete Tasks":
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, description, completed FROM tasks WHERE completed = 0')

        tasks = cursor.fetchall()
        
        if not tasks:
            stdscr.clear()
            stdscr.addstr(0, 0, "No tasks available. Press any key to return to menu.")
        else:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Tasks ({filter_choice}):")
            for idx, (task_id, description, completed) in enumerate(tasks, start=1):
                status = " - (Completed)" if completed else " - (In progress)"
                stdscr.addstr(idx, 0, f"{idx}. {description}{status}")
            stdscr.addstr(len(tasks) + 1, 0, "Press any key to return to menu.")
        
        stdscr.getch()

    def mark_task_completed(self, stdscr):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, description FROM tasks WHERE completed = 0')
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
            for idx, (task_id, description) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, description, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, description)
            
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
        cursor.execute('SELECT id, description FROM tasks WHERE completed = 1')
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
            for idx, (task_id, description) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, description, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, description)
            
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
        cursor.execute('SELECT id, description FROM tasks')
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
            for idx, (task_id, description) in enumerate(tasks):
                if idx == current_option:
                    stdscr.addstr(idx + 1, 0, description, curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, description)
            
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
    main = RaskManager()
    curses.wrapper(main.choices)

#!/usr/bin/python
#
########################
# timetxt.py ---- V0.9 #
########################
#
# Copyright 2009 Carl Sverre
#
# This file is part of Time.txt.
#
# Time.txt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Time.txt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Time.txt.  If not, see <http://www.gnu.org/licenses/>.

import optparse
import fileinput
import re
import datetime
import time
import math
import shutil
import os
from os.path import exists as file_exists
import sqlite3
from operator import attrgetter

# CONFIG
TASK_FILE = '/home/carl/dropbox/tasks/time.txt'
DATABASE = '/home/carl/databases/time_database.sqlite3'

cat_starter = '+'
default_category = 'uncategorized'

# VARIABLES
tasks = []
comments = []   # Comments will be moved to beginning of file

line_pattern = '^\[(?P<num>.*)\] \[(?P<status>.)\] \[(?P<time>\d+:\d+)\] \[(?P<session>\d+:\d+)\] \[(?P<task>.*?)\](?: \[(?P<start_time>.*)\])?'
line_format  = '[{num:d}] [{stat}] [{time}] [{session}] [{task}]'
start_time_format = '%H:%M %d:%m:%Y'

stdout_format_meta = '[{num:d}] [{msg}]'
stdout_format_gen = ' [{text}]' 
stdout_cat_format = cat_starter+' {category}'

# TASK CLASS
class Task:
    def __init__(self, line=None, task="", num=0, cat=""):
        """
        Creates a task object by parsing
        a line out of the task file
        
        line -- a line to parse
        """
        self.time_total = datetime.timedelta()
        self.session_time = datetime.timedelta()
        self.running = False
        self.category = ""

        if line:
            self.parse_line(line)
            self.category = cat
        elif task:
            self.num = num
            self.task = self.parse_task(task)
        else:
            self.task = ""
            self.num = 0
        
    def parse_line(self, line):
        """
        Parses a line formatted like so:
        [status] [00:00] [task here]
        
        line -- line to be parsed
        """
        s = re.search(line_pattern, line)
        status = s.group('status')
        self.num = int(s.group('num'))
        t = s.group('time').split(':')
        session_time = s.group('session').split(':')
        task = s.group('task')

        self.time_total = datetime.timedelta(hours=   int(t[0]),
                                             minutes= int(t[1]))
        self.session_time = datetime.timedelta(hours=      int(session_time[0]),
                                                    minutes=    int(session_time[1]))
        self.task = task

        if status == 'x':
            self.running = True
            self.time_start = datetime.datetime.strptime(s.group('start_time'), start_time_format)
        else:
            self.running = False

    def parse_task(self, task):
        """
        Parses a task for its category

        task -- task to be parsed
        """

        for word in task.split(' '):
            if word.startswith(cat_starter):
                self.set_category(word)
                task=re.sub('\s?\+'+word.strip(cat_starter)+'\s?','',task)
                return task

        self.category = default_category
        return task

    def set_category(self, category):
        self.category = category.strip(cat_starter)

    def start(self):
        if self.running:
            print("Error: Task already running")
            return

        self.running = True
        self.time_start = datetime.datetime.now()

    def stop(self):
        if not self.running:
            print("Error: Task already stopped")
            return

        self.running = False

        self.update_total_time()

    def seralize(self):
        now = datetime.datetime.now()
        if self.running:
            status = 'x'
            self.update_total_time()
            now = ' ['+now.strftime(start_time_format)+']'
        else:
            status = ' '
            now = ""
        
        formatted_time = format_timedelta(self.time_total)
        formatted_session_time = format_timedelta(self.session_time)

        return line_format.format(num=self.num, stat=status, time=formatted_time, session=formatted_session_time, task=self.task) + now

    def formatted_running(self):
        if self.running:
            return 'running'
        return 'stopped'

    def update_total_time(self):
        if self.running:
            now = datetime.datetime.now()
            difference = now - self.time_start
            self.time_total = self.time_total + difference
            self.session_time = self.session_time + difference

    def get_total_time(self):
        return format_timedelta(self.time_total)

    def get_session_time(self):
        return format_timedelta(self.session_time)

    def clear_session_time(self):
        self.session_time = datetime.timedelta()

    def session_time_seconds(self):
        return timedelta_to_seconds(self.time_total)

    def insert_into_sqlite3(self,conn):
        c = conn.execute("""
            INSERT INTO tasks (description,category,total_time,last_updated,time_added)
            VALUES (?,?,?,datetime('now','localtime'),datetime('now','localtime'));""",
            (
                self.task,
                self.category,
                self.session_time_seconds()
            )
        )
        return c.lastrowid

# UTIL
def load():
    """
    Loads the task list
    """

    last_category = default_category

    for line in fileinput.input(TASK_FILE):
        t = line.strip()
        if not t: continue
        if t.startswith('#'):
            comments.append(t+'\n')
            continue
        if t.startswith(cat_starter):
            last_category = t.lstrip(cat_starter+' ')
            continue
        tasks.append(Task(line=t, cat=last_category))

def save(copy=False):
    """
    Saves all the tasks
    """

    categories = create_categories_list()

    # Create temp file
    temp_filename = '/tmp/time.%s.txt' % os.getpid()
    temp = open(temp_filename, 'w')

    # Write out comments
    for comment in comments:
        temp.write(comment)
    temp.write('\n')

    for category,task_list in categories:
        temp.write(cat_starter + ' ' + category + '\n')
        for task in task_list:
            temp.write(task.seralize() + '\n')
        temp.write('\n')

    # Close and then move temp file to task_file (apply changes)
    temp.close()
    if copy:
        shutil.move(temp.name, TASK_FILE + ".bak")
    else:
        shutil.move(temp.name, TASK_FILE)

def create_categories_list():
    tasks.sort(key=attrgetter('category'))
    
    categories = []
    for task in tasks:
        found = False
        for category,task_list in categories:
            if task.category == category:
                task_list.append(task)
                found = True
                break
        if found: continue
        categories.append((task.category,[task]))

    # sort the task lists
    for category,task_list in categories:
        task_list.sort(compare_task_nums)

    return categories

def compare_task_nums(t,t2):
    return t.num-t2.num

def prompt(question):
    print(question)
    ans = raw_input("[y/n] ")
    if ans == 'y':
        return True 
    elif ans == 'n':
        return False

def format_timedelta(td):
    hours = td.days * 24
    minutes = math.floor(td.seconds / 60)
    hours = hours + math.floor(minutes / 60)
    minutes = minutes % 60
    return str(int(hours)).zfill(2) + ":" + str(int(minutes)).zfill(2)

def timedelta_to_seconds(td):
    return (td.days * 24 * 60 * 60) + td.seconds

def stdout_format(num, task, message, time=None, session=None):
    string = stdout_format_meta.format(num=num, msg=message)
    if time:
        string += stdout_format_gen.format(text=time)
    if session:
        string += stdout_format_gen.format(text=session)
    string += stdout_format_gen.format(text=task)
    print(string)

def get_args(parser):
    """
    returns a list of rargs for callback functions
    the rargs are the args between the callback option
    and the next option

    parser -- the parser instance from the callback option
    """

    ret_list = []
    for arg in parser.rargs:
        if arg[:2] == '--' and len(arg) > 2:
            break
        if arg[:1] == '-' and len(arg) > 1:
            break
        ret_list.append(arg)
    del parser.rargs[:len(ret_list)]
    return ret_list

# CALLBACKS
def add(option,opt,value,parser):
    load()

    task_str = value.strip()
    if not task_str:
        print("Error: No task description")

    n=0
    for t in sorted(tasks,compare_task_nums):
        if t.num == n:
            n=t.num+1

    task_obj = Task(task=task_str, num=n)

    stdout_format(task_obj.num, task_obj.task, 'added to '+task_obj.category)
    tasks.append(task_obj)
    save()


def remove(option,opt,value,parser):
    global tasks
    load()

    which = int(value)
    if which == -1:
        if prompt("Remove All Tasks?"):
            print("Removed all tasks")
            tasks = []
            save()
        return

    for i,task in enumerate(tasks):
        if which == task.num:
            stdout_format(task.num, task.task, 'removed from '+task.category)
            del tasks[i]
            save()

def start(option,opt,value,parser):
    load()

    which = int(value)
    for i,task in enumerate(tasks):
        if which == task.num:
            stdout_format(task.num, task.task, 'started')
            tasks[i].start()
            save()

def stop(option,opt,value,parser):
    load()

    which = int(value)
    for i,task in enumerate(tasks):
        if which == task.num:
            task.update_total_time()
            stdout_format(task.num, task.task, 'stopped', task.get_total_time(), task.get_session_time())
            tasks[i].stop()
            save()

def list(option,opt,value,parser):
    load()

    args = get_args(parser)
    categories = create_categories_list()

    search_cat = ''
    if args:
        search_cat = args[0].lower()

    for category,task_list in categories:
        if (search_cat != '') and (category.lower() != search_cat):
            continue

        print(stdout_cat_format.format(category=category))
        for task in task_list:
            task.update_total_time()
            stdout_format(task.num,task.task,task.formatted_running(), task.get_total_time(), session=task.get_session_time())
        print('')

def total_time(option,opt,value,parser):
    load()

    total = datetime.timedelta()
    total_session = datetime.timedelta()
    for task in tasks:
        total += task.time_total
        total_session += task.session_time
    
    print("Total time on list: " + format_timedelta(total))
    print("Total time this session: " + format_timedelta(total_session))

def update_database(option, opt, value, parser):
    """
    This function updates a sqlite database with the latest
    session data.
    """
    load()

    save(True);         # Save a copy of the current task.txt file
    
    init_database = False
    if not file_exists(DATABASE):
        init_database = True

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    if init_database:
        conn.executescript("""
                        CREATE TABLE sessions(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            time_added DATE,
                            total_session_time INTEGER
                        );
                        CREATE TABLE tasks(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            description TEXT,
                            category TEXT,
                            total_time INTEGER,
                            last_updated DATE,
                            time_added DATE,
                            time_removed DATE
                        );
                        CREATE TABLE task_sessions(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            task_id INTEGER,
                            session_id INTEGER,
                            session_time INTEGER,
                            FOREIGN KEY(task_id) REFERENCES tasks(id),
                            FOREIGN KEY(session_id) REFERENCES sessions(id)
                        );
                        CREATE TABLE last_session_tasks(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            task_id INTEGER,
                            FOREIGN KEY (task_id) REFERENCES tasks(id)
                        );""")
    
    for task_row in conn.execute("""
            SELECT id,description FROM tasks WHERE id IN
            (SELECT task_id FROM last_session_tasks);"""):
        found = False
        for task in tasks:
            if task.task == task_row["description"]:
                found = True

        if not found: conn.execute("""
            UPDATE tasks SET
                time_removed=datetime("now","localtime"),
                last_updated=datetime('now','localtime')
            WHERE id=?""", task_row["id"])
    
    conn.execute('DELETE FROM last_session_tasks;')

    conn.commit()

    # create new session
    conn.execute('INSERT INTO sessions (time_added) VALUES (datetime("now","localtime"));')
    session_id = conn.execute('SELECT last_insert_rowid();').fetchone()[0]

    for task in tasks:
        task_row = conn.execute('SELECT id from tasks where description=?;', (task.task,)).fetchone()
        if not task_row:
            task_id = task.insert_into_sqlite3(conn)
        else:
            task_id = task_row["id"]

        conn.execute("""INSERT INTO task_sessions (task_id,session_id,session_time)
                        VALUES(?,?,?)""",
                        (task_id, session_id, timedelta_to_seconds(task.session_time)))
        conn.execute("""INSERT INTO last_session_tasks (task_id) VALUES(?)""",
                    (task_id,))
        
        task.clear_session_time()

    conn.execute("""
        UPDATE sessions SET total_session_time=(
            SELECT SUM(session_time) FROM task_sessions WHERE task_id IN (
                SELECT task_id FROM last_session_tasks) and session_id=?) WHERE id=?;""",
        ( session_id,session_id ))
    
    conn.commit()
    
    save()
            

def export_csv(option, opt, value, parser):
    """
    Exports the sqlite database to csv (convienience function)
    """
    pass

def main():
    """
    Program entry point
    """

    # Parse the Command Line Args
    parser = optparse.OptionParser()
    parser.add_option('-a','--add',
                    help='Add new task to list',
                    action='callback',
                    metavar='TASK',
                    type='string',
                    callback=add)
    parser.add_option('-r','--remove',
                    help='Remove task from list (TASKNUM == -1 for all)',
                    action='callback',
                    metavar='TASKNUM',
                    type='int',
                    callback=remove)
    parser.add_option('-s','--start',
                    help='Start timing a task',
                    action='callback',
                    metavar='TASKNUM',
                    type='int',
                    callback=start)
    parser.add_option('-t','--stop',
                    help='Stop timing a task',
                    action='callback',
                    metavar='TASKNUM',
                    type='int',
                    callback=stop)
    parser.add_option('-l','--list',
                    help='List all tasks',
                    action='callback',
                    callback=list)
    parser.add_option('-o','--total',
                    help='Output total time in todo to stdout',
                    action='callback',
                    callback=total_time)
    parser.add_option('-u','--update',
                    help='Update sqlite database (run via cron, sessions are defined as the time between updates)',
                    action='callback',
                    callback=update_database)
    parser.add_option('-e','--export',
                    help='Exports database to CSV',
                    action='callback',
                    callback=export_csv)

    (options,args) = parser.parse_args()

if __name__=="__main__":
    main()

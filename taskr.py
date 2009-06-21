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
import math
import shutil
import os
from operator import attrgetter

# CONFIG
TASK_FILE = '/home/carl/dropbox/tasks/time.txt'

cat_starter = '+'
default_category = 'uncategorized'

# VARIABLES
tasks = []
comments = []   # Comments will be moved to beginning of file

line_pattern = '^\[(?P<num>.*)\] \[(?P<status>.)\] \[(?P<time>\d+:\d+)\] \[(?P<session>\d+:\d+)\] \[(?P<task>.*?)\](?: \[(?P<start_time>.*)\])?'
line_format  = '[{num:d}] [{stat}] [{time}] [{session}] [{task}]'
start_time_format = '%H:%M %d:%m:%Y'

stdout_format_string = '[{num:d}] [{task}] [{msg}]'
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
            return 'Running'
        return 'Stopped'

    def update_total_time(self):
        if self.running:
            now = datetime.datetime.now()
            difference = now - self.time_start
            self.time_total = self.time_total + difference
            self.session_time = self.session_time + difference

    def get_total_time(self):
        self.update_total_time()
        return format_timedelta(self.time_total)


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

def save():
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

def stdout_format(n, t, m, time=None):
    string = stdout_format_string.format(num=n, task=t, msg=m)
    if time:
        string += ' [' + time + ']'
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
    task_str = value.strip()
    if not task_str:
        print("Error: No task description")

    n=0
    for t in sorted(tasks,compare_task_nums):
        if t.num == n:
            n=t.num+1

    task_obj = Task(task=task_str, num=n)

    stdout_format(task_obj.num, task_obj.task, 'Added to '+task_obj.category)
    tasks.append(task_obj)
    save()


def remove(option,opt,value,parser):
    global tasks
    which = int(value)
    if which == -1:
        if prompt("Remove All Tasks?"):
            print("Removed all tasks")
            tasks = []
            save()
        return

    for i,task in enumerate(tasks):
        if which == task.num:
            stdout_format(task.num, task.task, 'Removed from '+task.category)
            del tasks[i]
            save()

def start(option,opt,value,parser):
    which = int(value)
    for i,task in enumerate(tasks):
        if which == task.num:
            stdout_format(task.num, task.task, 'Started')
            tasks[i].start()
            save()

def stop(option,opt,value,parser):
    which = int(value)
    for i,task in enumerate(tasks):
        if which == task.num:
            stdout_format(task.num, task.task, 'Stopped', task.get_total_time())
            tasks[i].stop()
            save()

def list(option,opt,value,parser):
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
            stdout_format(task.num,task.task,task.formatted_running(), task.get_total_time())
        print('')

def total_time(option,opt,value,parser):
    total = datetime.timedelta()
    for task in tasks:
        total += task.time_total
    
    print("Total time on list: " + format_timedelta(total))

def update_database(option, opt, value, parser):
    """
    This function updates a sqlite database with the latest
    session data.

    Database := {last_session_tasks, sessions, tasks}
        last session tasks  :=  table of the tasks which were in the time.txt database
                                as of the last session
        sessions            :=  table of all the sessions
        tasks               :=  table of all the tasks

    For each task in database.last_session_tasks:
        if task not in time.txt:
            task.datetime_removed = now
        
    For each task in tasks:
        if not database[task]:
            create database[task]
               task := {id, description, total_time, last_updated, datetime_added, datetime_removed} 
        Create database[session]:
            session := {id, task_key, datetime_now, task_key->last_updated, session_time}
        database[task]->last_updated = now
        database[task]->total_time = task.total_time

    Note database[task]->id != task.num

    Function also clears session_time for every task in text database
    """
    pass

def export_csv(option, opt, value, parser):
    """
    Exports the sqlite database to csv (convienience function)
    """
    pass

def main():
    """
    Program entry point
    """
    # load the task file
    load()

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

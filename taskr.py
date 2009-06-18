#!/usr/bin/python

import optparse
import fileinput
import re
import datetime
import math

# CONFIG
TASK_FILE = '/home/carl/dropbox/taskr/todo.txt'

# VARIABLES
tasks = []

line_pattern = '^\[(?P<num>.*)\] \[(?P<status>.)\] \[(?P<time>\d+:\d+)\] \[(?P<task>.*?)\](?: \[(?P<start_time>.*)\])?'
line_format  = '[{num:d}] [{stat}] [{time}] [{task}]'
start_time_format = '%H:%M %d:%m:%Y'

stdout_format_string = '[{num:d}] [{task}] [{msg}]'

# TASK CLASS
class Task:
    def __init__(self, line=None, task="", num=0):
        """
        Creates a task object by parsing
        a line out of the task file
        
        line -- a line to parse
        """
        self.time_total = datetime.timedelta()
        self.running = False

        if line:
            self.parse(line)
        elif task:
            self.task = task
            self.num = num
        else:
            self.task = ""
            self.num = 0
        
    def parse(self, line):
        """
        Parses a line formatted like so:
        [status] [00:00] [task here]
        
        line -- line to be parsed
        """
        s = re.search(line_pattern, line)
        status = s.group('status')
        self.num = int(s.group('num'))
        t = s.group('time').split(':')
        task = s.group('task')

        self.time_total = datetime.timedelta(hours=   int(t[0]),
                                             minutes= int(t[1]))
        self.task = task

        if status == 'x':
            self.running = True
            self.time_start = datetime.datetime.strptime(s.group('start_time'), start_time_format)
        else:
            self.running = False

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

        return line_format.format(num=self.num, stat=status, time=formatted_time, task=self.task) + now

    def formatted_running(self):
        if self.running:
            return 'Running'
        return 'Stopped'

    def update_total_time(self):
        if self.running:
            now = datetime.datetime.now()
            difference = now - self.time_start
            self.time_total = self.time_total + difference

    def get_total_time(self):
        self.update_total_time()
        return format_timedelta(self.time_total)


# UTIL
def load():
    """
    Loads the task list
    """
    for line in fileinput.input(TASK_FILE):
        t = line.strip()
        if not t or t.startswith('#'):
            continue
        tasks.append(Task(line=t))

def save():
    """
    Saves all the tasks
    """

    # sort the task list
    tasks.sort(compare_tasks)

    f = open(TASK_FILE, 'w')
    for task in tasks:
        f.write(task.seralize() + '\n')

def compare_tasks(t,t2):
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

# CALLBACKS
def add(option,opt,value,parser):
    task_str = value.strip()
    if not task_str:
        print("Error: No task description")

    n=0
    for t in tasks:
        if t.num == n:
            n=t.num+1

    task_obj = Task(task=task_str, num=n)

    stdout_format(task_obj.num, task_obj.task, 'Added')
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
            stdout_format(task_obj.num, task_obj.task, 'Removed')
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
    for task in tasks:
        stdout_format(task.num,task.task,task.formatted_running(), task.get_total_time())

def total_time(option,opt,value,parser):
    total = datetime.timedelta()
    for task in tasks:
        total += task.time_total
    
    print("Total time on list: " + format_timedelta(total))

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

    (options,args) = parser.parse_args()

if __name__=="__main__":
    main()

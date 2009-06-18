This program will be a project timing program running on plain text files.
It will be simple to use and also double
as a task list.

Todo
----
 + finish start/stop
 + add finished function (moves it to a finished list?  Or seperate section?)
 + Testing
 + add csv output to send it to excel
 + add "stats" output which will total up all hours on list

Example run
--------

$ taskr add "School Work"
[1] School Work [not started]
$ taskr add "Job Work"
[2] Job Work [not started]
$ taskr start 1
[1] School Work [started]
$ taskr list
[1] School Work [running] [00:01]
[2] Job Work [not started] [00:00]
$ taskr stop 1
[1] School Work [stopped] [00:02]
Worked 00:02 this session.
$ taskr start 1
[1] School Work [started]
$ taskr start 2
[2] Job Work [started]
$ taskr stop
[1] School Work [stopped] [00:03]
Worked 00:01 this session.
[2] Job Work [stopped] [00:01]
Worked 00:01 this session.


Commands
--------
add
remove
start
stop
list

Example task file
-----------------

# Tasks
[x] [00:03] [School Work] [time started]
[ ] [00:01] [Job Work]

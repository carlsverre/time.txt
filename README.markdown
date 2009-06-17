This program will be a project timing program running on markdown
formatted plain text files.  It will be simple to use and also double
as a task list.

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


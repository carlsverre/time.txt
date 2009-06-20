Taskr
=====
This program will be a project timing program running on plain text files.
It will be simple to use and also double as a task list.

Installation and Running
------------------------
+ Just drop the source file somewhere on your path, or link it.
+ Run it with ./taskr (or if its on your path, just taskr works).
+ I recommend you alias t to taskr
	- tl for taskr -l
	- ts for taskr -s
	- tt for taskr -t
	- tr for taskr -r

Todo
----
 + add finished function (moves it to a finished list?)
 + Testing
 + add csv output to send it to excel
 + add categories and tags (+tag, =category)
	- list output and todo file should be sorted by category
	- you can list select categories like: taskr -l CATEGORY
	- you can move items between categories and add tags to items
 + maintain comments in text file

Example run
-----------

	$ taskr -l
	[0] [csc360 P2 +school] [Stopped] [01:15]
	[1] [taskr work +personal] [Running] [00:01]
	[3] [Francine Legault Phone +work] [Stopped] [00:00]
	$ taskr -a "Taskr Demo"
	[4] [Taskr Demo] [Added]
	$ taskr -l
	[0] [csc360 P2 +school] [Stopped] [01:15]
	[1] [taskr work +personal] [Running] [00:01]
	[3] [Francine Legault Phone +work] [Stopped] [00:00]
	[4] [Taskr Demo] [Stopped] [00:00]
	$ taskr -s 4
	[4] [Taskr Demo] [Started]
	$ taskr -l
	[0] [csc360 P2 +school] [Stopped] [01:15]
	[1] [taskr work +personal] [Running] [00:01]
	[3] [Francine Legault Phone +work] [Stopped] [00:00]
	[4] [Taskr Demo] [Running] [00:00]
	$ cat todo.txt 
	[0] [ ] [01:15] [csc360 P2 +school]
	[1] [x] [00:01] [taskr work +personal] [18:49 19:06:2009]
	[3] [ ] [00:00] [Francine Legault Phone +work]
	[4] [x] [00:00] [Taskr Demo] [18:49 19:06:2009]
	$ taskr -l
	[0] [csc360 P2 +school] [Stopped] [01:15]
	[1] [taskr work +personal] [Running] [00:02]
	[3] [Francine Legault Phone +work] [Stopped] [00:00]
	[4] [Taskr Demo] [Running] [00:01]
	$ taskr -t 4
	[4] [Taskr Demo] [Stopped] [00:01]
	$ taskr -r 4
	[4] [Taskr Demo] [Removed]
	$ taskr -o
	Total time on list: 03:53

Commands
--------

	add "TASK" - adds task with description TASK to list
	remove NUM - removes task with num NUM
	start NUM  - starts task with num NUM
	stop NUM   - stops task with num NUM
	list       - lists all tasks
	total      - total time of tasks on list

Example task file
-----------------

	[0] [ ] [01:15] [csc360 P2 +school]
	[1] [x] [00:01] [taskr work +personal] [18:49 19:06:2009]
	[3] [ ] [00:00] [Francine Legault Phone +work]
	[4] [x] [00:00] [Taskr Demo] [18:49 19:06:2009]

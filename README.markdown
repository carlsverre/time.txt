Taskr
=====
This program is be a project timing program running on plain text files.
It is simple to use and also doubles as a task list. Changelog is at the end

Installation and Running
------------------------
+ Just drop the source file somewhere on your path, or link it.
+ Run it with ./taskr (or if its on your path, just taskr works).
+ I recommend you alias t to taskr.  Also the following aliases are useful:
	- tl for taskr -l
	- ts for taskr -s
	- tt for taskr -t
	- tr for taskr -r

Todo
----
 + Testing
 + implement update and export functions

Example run
-----------
	$ taskr -l
	+ personal
	[1] [taskr work] [Running] [03:35]

	+ school
	[0] [csc360 P2] [Stopped] [01:15]

	+ work
	[3] [Francine Legault Phone] [Stopped] [00:00]

	$ taskr -a "Demoing Taskr +demo" -a "Multiple Items +demo"
	[4] [Demoing Taskr] [Added to demo]
	[5] [Multiple Items] [Added to demo]
	$ taskr -l
	+ demo
	[4] [Demoing Taskr] [Stopped] [00:00]
	[5] [Multiple Items] [Stopped] [00:00]

	+ personal
	[1] [taskr work] [Running] [03:37]

	+ school
	[0] [csc360 P2] [Stopped] [01:15]

	+ work
	[3] [Francine Legault Phone] [Stopped] [00:00]

	$ taskr -s 4
	[4] [Demoing Taskr] [Started]
	$ cat dropbox/taskr/todo.txt
	+ demo
	[4] [x] [00:00] [Demoing Taskr] [21:01 19:06:2009]
	[5] [ ] [00:00] [Multiple Items]

	+ personal
	[1] [x] [03:37] [taskr work] [21:01 19:06:2009]

	+ school
	[0] [ ] [01:15] [csc360 P2]

	+ work
	[3] [ ] [00:00] [Francine Legault Phone]

	$ taskr -t 4
	[4] [Demoing Taskr] [Stopped] [00:01]
	$ taskr -l
	+ demo
	[4] [Demoing Taskr] [Stopped] [00:01]
	[5] [Multiple Items] [Stopped] [00:00]

	+ personal
	[1] [taskr work] [Running] [03:38]

	+ school
	[0] [csc360 P2] [Stopped] [01:15]

	+ work
	[3] [Francine Legault Phone] [Stopped] [00:00]

	$ taskr -r 4
	[4] [Demoing Taskr] [Removed from demo]
	$ taskr -r 5
	[5] [Multiple Items] [Removed from demo]
	$ taskr -o
	Total time on list: 04:44

Commands
--------

	add "TASK" - adds task with description TASK to list
				 (use +category to add tasks to categories)
	remove NUM - removes task with num NUM
	start NUM  - starts task with num NUM
	stop NUM   - stops task with num NUM
	list       - lists all tasks
	total      - total time of tasks on list
	update	   - Update sqlite database backend (for stats and archiving) (not implemented)
	export	   - Exports database to CSV (not implemented)

Example task file
-----------------
	+ demo
	[4] [x] [00:00] [00:00] [Demoing Taskr] [21:01 19:06:2009]
	[5] [ ] [00:00] [00:00] [Multiple Items]

	+ personal
	[1] [x] [03:37] [00:38] [taskr work] [21:01 19:06:2009]

	+ school
	[0] [ ] [01:15] [00:00] [csc360 P2]

	+ work
	[3] [ ] [00:00] [00:00] [Francine Legault Phone]

Changelog
---------

	0.9
		+	framework for functionality of new commands (export, update)
		+	writes to temporary files rather than main database
			(updates main database when finished)
	0.8
		+	All commands except export and update.
	0.1
		+	Initial Commit

Time.txt
=====
This program is be a project timing program running on plain text files.
It is simple to use and also doubles as a task list. Changelog is at the end.

Installation and Running
------------------------
+ Just drop the source file somewhere on your path, or link it.
+ Run it with ./timetxt (or if its on your path, just timetxt works).
+ I recommend you alias t to timetxt.  Also the following aliases are useful:
	- tl for timetxt -l
	- ts for timetxt -s
	- tt for timetxt -t
	- tr for timetxt -r

Todo
----
 + Testing
 + implement update and export functions
 + Add exception handling
 + Rewrite whole thing in sql

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
	####################################################################
	#                   Comments must be in this block                 #
	#------------------------------------------------------------------#
	# [num] [active] [total time] [session time] [task] [time started] #
	####################################################################

	+ personal
	[1] [x] [05:26] [01:38] [time.txt work] [17:44 21:06:2009]

	+ school
	[0] [ ] [01:15] [00:00] [csc360 P2]

	+ studying
	[4] [ ] [03:54] [00:00] [csc360]
	[5] [ ] [05:15] [00:41] [csc305]

	+ work
	[3] [ ] [00:00] [00:00] [Francine Legault Phone]

Changelog
---------

* 0.9	June 21, 2009
	+	renamed project from taskr to time.txt due to taskr being taken
	+	framework for functionality of new commands (export, update)
	+	writes to temporary files rather than main database
		(updates main database when finished)
* 0.8
	+	All commands except export and update.
* 0.1
	+	Initial Commit

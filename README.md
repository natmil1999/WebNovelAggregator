A flask program that runs a local server and monitors for new chapters from webnovels.


This server connects with the database (No support has been added to change the database besides adding new webnovels.)
to display chapters from webnovels listed in the database that the reader has not yet read.

The program must be placed into the Windows C drive, into the Program Files folder "C:\Program Files". 
The folder with the program must be named WebNovelAggregator. This is so that the program can properly locate the 
identifier.sqlite database file.

A identifier.sqlite file has been provided. This file is a blank database that the webnovel fictions and chapters will be stored in.

When one of the chapter links displayed is clicked, the server registers that chapter as read and no longer displays it.

Only webnovels with new chapters will be displayed.

The program has support for webnovels on RoyalRoad.com and Patreon.com

The program cannot webscrape for patreon chapters. Instead, it monitors an email inbox (with settings enabled to allow
remote access) that patreon sends new post notifications to.

It is recommended that a user forwards patreon emails to a new email account that the server then checks.

A 'Patreon_Email_Login.txt' file needs to be made in the project directory that stores the users email username and password.
This Username and Password file is stored locally.

The server then monitors the email inbox for patreon updates.

The chapter displayed on the webserver will link to the pateron post with the new chapter (Post from author).

New webnovels can be added on the addfiction page by entering the information. The addFiction page asks for the title of the novel on royalroad, the url of the fiction page on royalroad, then name of the author (On patreon, not on RR), and 0 if new chapters will be on patreon or 1 to monitor for new chapters from royalroad.
When new fictions are added, all the fictions current chapters are scraped and added to the database as read. This is to avoid having potentially 100's of chapters added to the server display screen that the user has already read. 

Functionality to make updates or deletions to the database has not been added.

The server can be started using 'python app.py' when in the program directory in windows command prompt.
The command cd "C:\Program Files\WebNovelAggregator && python app.py" can be used to navigate to the program directory and run it in one line.

If you wish to regularly use this local server, it may be useful to use windows task scheduler (or a different mecahnism) to run the above command on startup; there are many resources online on how to do this.

This is mainly a personal use project. Updates to allow for easier use by other users in the future may be added depending on interest.


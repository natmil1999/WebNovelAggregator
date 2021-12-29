A flask program that runs a local server and monitors for new chapters from webnovels.

This server connects with the database (No support has been added to change the database besides adding new webnovels. The database file path at the
top of app.py must be changed in the code for it to work properly for other users.)
to display chapters from webnovels listed in the database that the reader has not yet read.

A identifier.sqlite file has been provided. This file is a blank database that should work once the database file path at the top of app.py has been adjusted. 

When one of the chapter links displayed is clicked, the server registers that chapter as read and no longer displays it.

Only webnovels with new chapters will be displayed.

The program has support for webnovels on RoyalRoad.com and Patreon.com

The program cannot webscrape for patreon chapters. Instead, it monitors an email inbox (with settings enabled to allow
remote access) that patreon sends new post notifications to.

A 'Password.txt' file needs to be made in the project directory that stores the users email password, and the email
address in function read_gmail in DatabaseUtilites.py needs to be updated for other users to use.

The server then monitors the email inbox for patreon updates. The server expects the email inbox to only receive emails
from patreon. The server only has light error checking to make sure that it adds chapters only if the email subject
has "just shared" in it.

The chapter displayed on the webserver will link to the pateron post with the new chapter (Post from author).

New webnovels can be added on the addfiction page by entering the information. The addFiction page asks for the title of the novel on royalroad, the url of the fiction page on royalroad, then name of the author (On patreon, not on RR), and 0 to update chapters from patreon or 1 to update chapters from royalroad.
When new fictions are added, all the fictions current chapters are scraped and added to the database as read. This is to avoid having potentially 100's of chapters added to the server display screen that the user has already read, and would have to manually click each chapter to remove them from the display. 

Functionality to make updates or deletions to the database has not been added, this needs to be done manually.

The server can be started using 'python app.py' when in the program directory in windows command prompt.

This is mainly a personal use project. Updates to allow for easier use by other users in the future may be added depending on interest.


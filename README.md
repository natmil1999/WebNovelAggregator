A flask program that runs a local server and monitors for new chapters from webnovels.

This server connects with the database (No support has been added to change the database. The database file path at the
top of app.py must be changed in the code for it to work properly for other users.)
to display chapters from webnovels listed in the database that the reader has not yet read.

A initDatabase file has been provided, but has not been tested. 

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

New webnovels can be added on the addfiction page by entering the information

The server can be started using 'python app.py' when in the program directory in windows command prompt.

This is mainly a personal use project. Updates to allow for easier use by other users in the future may be added depending on interest.

Notes 

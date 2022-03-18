import email
import imaplib
import time
from email.header import decode_header

from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy

from ChapterRetrievers import RoyalRoadRetriever


class DatabaseUtilities:

    def __init__(self, app):
        self.db = SQLAlchemy(app)

        # Class to store the fiction database information
        class Fictions(self.db.Model):
            fiction_id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.Text, unique=False, nullable=False)
            url = self.db.Column(self.db.Text, unique=True, nullable=False)
            patreon_RR = self.db.Column(self.db.Integer, nullable=False, default=1)
            author = self.db.Column(self.db.Text, nullable=False, default="Filler")
            chapters = self.db.relationship('Chapters', backref='fictions', lazy=True)

        self.Fictions = Fictions

        # Class to store the Chapter information in the database's format
        class Chapters(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            fiction_id = self.db.Column(self.db.Integer, self.db.ForeignKey('fictions.fiction_id'), nullable=False)
            url = self.db.Column(self.db.Text, unique=True, nullable=False)
            read = self.db.Column(self.db.Integer, default=0)
            title = self.db.Column(self.db.Text, nullable=False)

            def __repr__(self):
                return '<Chapter %r>' % self.title

        self.Chapters = Chapters

    # Update the database with new patreon chapters found in the email
    def update_patreon_chapters(self):

        # Read the email, return a list of new chapters that were in the email
        emails = self.read_gmail()

        # Loop through the new chapters and add them to the database, with error checking
        for chapter in emails:
            try:
                fiction_id = self.Fictions.query.filter_by(author=chapter.get('author')).first().fiction_id
                url = chapter.get('url')
                # IF the chapter url isn't already in the database and the fiction is set to use patreon chapters
                if self.Chapters.query.filter_by(fiction_id=fiction_id, url=url).count() == 0 and \
                        self.Fictions.query.filter_by(fiction_id=fiction_id).first().patreon_RR == 0:
                    chappy = self.Chapters(
                        fiction_id=fiction_id,
                        url=chapter.get('url'),
                        title=chapter.get('chapterTitle'))
                    self.db.session().add(chappy)
                    self.db.session.commit()
            except:
                print("Failed to add Chapter: %s" % chapter.get('chapterTitle'))

    # Update the database with new chapters on RoyalRoad
    # Parameter chapterList is a result of the get_RR_chapter_list function in ChapterRetrievers, called
    #   in update_RR_fictions
    # chapterList is a list of chapters from RR for all fictions in the database
    def update_RR_chapters(self, chapterList):

        # Loop through all the chapters for the fictions in the database.
        # Check if the chapter is already in the database
        # If it is a new chapter, add it to the database as unread
        for chapter in chapterList:
            try:
                # Get fiction_id in database based on chapter's fiction field.
                fiction_id = self.Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id

                url = chapter.get('url')

                # Check if the chapter is in the database
                if self.Chapters.query.filter_by(fiction_id=fiction_id, url=url).count() == 0:
                    # If chapter is not in the database, add it
                    chappy = self.Chapters(
                        fiction_id=self.Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id,
                        url=chapter.get('url'),
                        title=chapter.get('title'))
                    self.db.session().add(chappy)
                    self.db.session.commit()
            except:
                print("Failed to add chapter: %s" % chapter.get('title'))

    # Get the list of chapters for each fiction
    # URL parameter allows for this to be called and specify a fiction to get the chapter list for, regardless
    #   of database settings
    def update_RR_fictions(self, url=''):
        # Initialize the RoyalRoadRetriever object
        retriever = RoyalRoadRetriever()

        # For all fictions in the database, where the database indicates it is an RR fiction
        for f in self.Fictions.query.all():

            # If the fiction is configured to update from RR in the database, or the url is passed as the parameter
            if f.patreon_RR == 1 or f.url == url:
                try:
                    # Try to web scrape the list of chapters for this fiction
                    soup = retriever.get_web_data(f.url)
                    chapterList = retriever.get_RR_ChapterList(soup)
                    # Call function to add new chapters to the database
                    self.update_RR_chapters(chapterList)
                except:
                    # Error connecting to RR website, ignore.
                    print("ERROR: Could not connect to RR!")

    # Reads the email to find new Patreon chapters
    def read_gmail(self):
        global subject, body

        # Open file holding email login username and password
        hiddenPassword = open("Patreon_Email_Login.txt", "r")

        # Set email username to be the first line of the login file that is stored locally.
        username = hiddenPassword.readline().strip()

        # Set password to be the second line of the Password file that is stored locally.
        password = hiddenPassword.readline().strip()

        # create an IMAP4 class with SSL

        # catch error if it can't connect to gmail.
        try:
            imap = imaplib.IMAP4_SSL("imap.gmail.com")
            # authenticate
            imap.login(username, password)
        except:
            print("Email could not connect!")
            # End function early on error with a blank return
            return []

        # Specify to find emails from inbox
        status, messages = imap.select("INBOX")

        # total number of emails
        messages = int(messages[0])
        emails = []

        # Loop through emails in the inbox
        for i in range(1, messages + 1):

            # fetch the email message by ID
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    From, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(From, bytes):
                        From = From.decode(encoding)

                    # if the email message is multipart
                    msg.walk()
                    msg.walk()
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()

            # Parse through email subject for the chapter name
            name = subject.replace('for patrons only', '')[1:]

            # Parse through the email subject for the author name
            author = name.strip().split('just')[0].strip()

            # Only try to add a chapter if the subject line had "Just Shared" in it.
            # This is because emails with 'Just Shared' indicate it is a new Patreon post and not an unrelated email
            if subject.find("just shared") > 0:
                name = name.split('"')[1]

                # Collect the chapter info and find the chapter url in the email body
                chapter = {"chapterTitle": name,
                           "url": BeautifulSoup(body, 'lxml').find_all('a')[2].attrs.get('href'),
                           'author': author
                           }
                emails.append(chapter)

        # Mark all emails for deletion
        typ, data = imap.search(None, 'ALL')
        for num in data[0].split():
            imap.store(num, '+FLAGS', '\\Deleted')

        # delete the emails marked for deletion
        imap.expunge()

        start = time.perf_counter()
        # close the connection and logout
        imap.close()
        imap.logout()
        return emails

    # Get a list of all the unread chapters in the database
    def get_new_chapters(self):

        # Dict of fictions and chapter lists.
        # Key = string of fiction name
        # Value = tuple of (len of chapter list, list of chapters)
        fictions = {}
        for f in self.Fictions.query.all():
            chapterList = []
            for c in self.Chapters.query.filter_by(fiction_id=f.fiction_id, read=0):
                chapterList.append(c)

            # Make newest chapters appear on top.
            chapterList.reverse()


            if len(chapterList) > 0:
                fictions[str(f.name)] = (len(chapterList), chapterList)

        return fictions

    # Mark all of the chapters for a fiction that was just added to the database as read
    def mark_all_as_read(self, url):
        retriever = RoyalRoadRetriever()
        soup = retriever.get_web_data(url)
        chapterList = retriever.get_RR_ChapterList(soup)

        # Mark all of the fictions chapters as read by calling mark_chapter_as_read for each chapter
        for c in chapterList:
            self.mark_chapter_as_read(c.get('url'))

    # Mark the chapter passed to this function by url as read in the database
    def mark_chapter_as_read(self, url):
        try:
            # Change the chapter to be read
            self.Chapters.query.filter_by(url=url).first().read = 1
            # Push the change to the database
            self.db.session.commit()
        except:
            print("Error marking chapter as read: " + url)

    # Add a new fiction to the database
    def add_fiction(self, fiction, author, url, site):

        fic = self.Fictions(
            name=fiction,
            url=url,
            author=author,
            patreon_RR=site
        )
        # Try to add the fiction to the database
        try:
            self.db.session().add(fic)
            self.db.session.commit()
        except:
            print("Failed to add fiction: " + fiction)

import email
import imaplib
from email.header import decode_header

from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy

from ChapterRetrievers import RoyalRoadRetriever


class DatabaseUtilities:

    def __init__(self, app):
        self.db = SQLAlchemy(app)

        class Fictions(self.db.Model):
            fiction_id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.Text, unique=False, nullable=False)
            url = self.db.Column(self.db.Text, unique=True, nullable=False)
            patreon_RR = self.db.Column(self.db.Integer, nullable=False, default=1)
            author = self.db.Column(self.db.Text, nullable=False, default="Filler")
            chapters = self.db.relationship('Chapters', backref='fictions', lazy=True)

        self.Fictions = Fictions

        class Chapters(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            fiction_id = self.db.Column(self.db.Integer, self.db.ForeignKey('fictions.fiction_id'), nullable=False)
            url = self.db.Column(self.db.Text, unique=True, nullable=False)
            read = self.db.Column(self.db.Integer, default=0)
            title = self.db.Column(self.db.Text, nullable=False)

            def __repr__(self):
                return '<Chapter %r>' % self.title

        self.Chapters = Chapters

    def update_patreon_chapters(self):
        emails = self.read_gmail()
        for chapter in emails:
            try:
                fiction_id = self.Fictions.query.filter_by(author=chapter.get('author')).first().fiction_id
                url = chapter.get('url')
                if self.Chapters.query.filter_by(fiction_id=fiction_id, url=url).count() == 0:
                    chappy = self.Chapters(
                        fiction_id=fiction_id,
                        url=chapter.get('url'),
                        title=chapter.get('chapterTitle'))
                    self.db.session().add(chappy)
                    self.db.session.commit()
            except:
                print("Failed to add Chapter: %s" % chapter.get('chapterTitle'))

    def update_RR_chapters(self, chapterList):
        for chapter in chapterList:
            try:
                fiction_id = self.Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id
                url = chapter.get('url')
                if self.Chapters.query.filter_by(fiction_id=fiction_id, url=url).count() == 0:
                    chappy = self.Chapters(
                        fiction_id=self.Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id,
                        url=chapter.get('url'),
                        title=chapter.get('title'))
                    self.db.session().add(chappy)
                    self.db.session.commit()
            except:
                print("Failed to add chapter: %s" % chapter.get('title'))

    def update_RR_fictions(self):
        retriever = RoyalRoadRetriever()
        for f in self.Fictions.query.all():
            if f.patreon_RR == 1:
                soup = retriever.get_web_data(f.url)
                chapterList = retriever.get_RR_ChapterList(soup)
                self.update_RR_chapters(chapterList)

    def read_gmail(self):
        global subject, body
        username = "webnovelaggregator1999@gmail.com"
        password = "18Nmiller="

        # create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login(username, password)

        status, messages = imap.select("INBOX")

        # total number of emails
        messages = int(messages[0])
        emails = []
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

            name = subject.replace('for patrons only', '')[1:]
            author = name.strip().split('just')[0].strip()
            # Only try to add a chapter if the subject line had "Just Shared" in it.
            if subject.find("just shared") > 0:
                # print(name)
                name = name.split('"')[1]
                chapter = {"chapterTitle": name,
                           "url": BeautifulSoup(body, 'lxml').find_all('a')[2].attrs.get('href'),
                           'author': author
                           }
                emails.append(chapter)

        # close the connection and logout
        imap.close()
        imap.logout()
        return emails

    def get_new_chapters(self):
        fictions = []
        for f in self.Fictions.query.all():
            chapterList = []
            for c in self.Chapters.query.filter_by(fiction_id=f.fiction_id, read=0):
                chapterList.append(c)

            # Make newest chapters appear on top? Might not want that in production version
            chapterList.reverse()

            fiction = {
                "name": f.name,
                "chapters": chapterList
            }
            if len(chapterList) > 0:
                fictions.append(fiction)

        return fictions

    def mark_all_as_read(self, url):
        retriever = RoyalRoadRetriever()
        soup = retriever.get_web_data(url)
        chapterList = retriever.get_RR_ChapterList(soup)
        for c in chapterList:
            self.mark_chapter_as_read(c.get('url'))

    def mark_chapter_as_read(self, url):
        try:
            self.Chapters.query.filter_by(url=url).first().read = 1
            self.db.session.commit()
        except:
            print("Error marking chapter as read: " + url)

    def add_fiction(self, fiction_data):

        fic = self.Fictions(
            name=fiction_data.fiction,
            url=fiction_data.url,
            author=fiction_data.author,
            patreon_RR=fiction_data.site
        )
        try:
            self.db.session().add(fic)
            self.db.session.commit()
        except:
            print("Failed to add fiction: " + fiction_data.fiction)

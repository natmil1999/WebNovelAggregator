import email
import imaplib
from email.header import decode_header

from bs4 import BeautifulSoup
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request, url_for
from flask_sqlalchemy import SQLAlchemy

from ChapterRetrievers import RoyalRoadRetriever

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Users\\natmi\\PycharmProjects\\WebNovelAggregator\\identifier.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Fictions(db.Model):
    fiction_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=False, nullable=False)
    url = db.Column(db.Text, unique=True, nullable=False)
    patreon_RR = db.Column(db.Integer, nullable=False, default=1)
    author = db.Column(db.Text, nullable=False, default="Filler")
    chapters = db.relationship('Chapters', backref='fictions', lazy=True)

    def __repr__(self):
        return '<Fiction %r>' % self.name


class Chapters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fiction_id = db.Column(db.Integer, db.ForeignKey('fictions.fiction_id'), nullable=False)
    url = db.Column(db.Text, unique=True, nullable=False)
    read = db.Column(db.Integer, default=0)
    title = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Chapter %r>' % self.title


@app.route('/')
def home():
    # Class to web scrape chapter urls from fiction pages

    db_utils = DatabaseUtilities()

    # Add any new chapters from RoyalRoad to database
    db_utils.update_RR_fictions()

    # Add new chapters from the emails in aggregator inbox
    db_utils.update_patreon_chapters()

    fictionList = db_utils.get_new_chapters()

    # Mark all chapters of a fiction as read
    # db_utils.mark_all_as_read(Fictions.query.all()[1])

    return render_template('homepage.html', title='My Updated WebNovels', fictionList=fictionList,
                           fictionListLen=len(fictionList), sorry="No New Chapters, sorry ):")


@app.route('/addFiction', methods=['GET', 'POST'])
def addFiction():
    try:
        db_utils = DatabaseUtilities()
        if request.method == 'POST':
            fiction = request.form.get("fname").strip()
            author = request.form.get("fauth").strip()
            url = request.form.get("furl").strip()
            site = request.form.get("fsite").strip()
            fic = Fictions(
                name=fiction,
                url=url,
                author=author,
                patreon_RR=site
            )
            db.session().add(fic)
            db.session.commit()
            db_utils.update_patreon_chapters()
            db_utils.update_RR_fictions()
            db_utils.mark_all_as_read(url)
    except:
        pass

    return redirect('/')


@app.route('/mark_chapter_as_read', methods=['GET', 'POST'])
def mark_chapter_as_read():
    db_utils = DatabaseUtilities()

    # Mark the chapter as read
    db_utils.mark_chapter_as_read(request.form.get('chapter_url'))

    # Refresh the page
    return redirect(url_for('/'))


if __name__ == '__main__':
    app.run()


class DatabaseUtilities:

    def update_patreon_chapters(self):
        emails = self.read_gmail()
        for chapter in emails:
            try:
                id = Fictions.query.filter_by(author=chapter.get('author')).first().fiction_id
                url = chapter.get('url')
                if Chapters.query.filter_by(fiction_id=id, url=url).count() == 0:
                    chappy = Chapters(
                        fiction_id=id,
                        url=chapter.get('url'),
                        title=chapter.get('chapterTitle'))
                    db.session().add(chappy)
                    db.session.commit()
            except:
                pass

    def update_RR_chapters(self, chapterList):
        for chapter in chapterList:
            try:
                id = Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id
                url = chapter.get('url')
                if Chapters.query.filter_by(fiction_id=id, url=url).count() == 0:
                    chappy = Chapters(
                        fiction_id=Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id,
                        url=chapter.get('url'),
                        title=chapter.get('title'))
                    db.session().add(chappy)
                    db.session.commit()
            except:
                pass

    def update_RR_fictions(self):
        retriever = RoyalRoadRetriever()
        for f in Fictions.query.all():
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
        for f in Fictions.query.all():
            chapterList = []
            for c in Chapters.query.filter_by(fiction_id=f.fiction_id, read=0):
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
            Chapters.query.filter_by(url=url).first().read = 1
            db.session.commit()
        except:
            print("Error marking chapter as read: " + url)

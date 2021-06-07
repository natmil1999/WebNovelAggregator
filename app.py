from flask import Flask
from bs4 import BeautifulSoup
import requests
import imaplib
import email
from email.header import decode_header
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
    retriever = RoyalRoadRetriever()

    # Need fictionurl query
    fictionUrl = Fictions.query.filter_by(name="Blue Core").first().url
    soup = retriever.get_web_data(Fictions.query.filter_by(name="Blue Core").first().url)

    chapterList = retriever.get_RR_ChapterList(soup)
    updateChapters(chapterList)

    fiction = Fictions(name='Blue Core', url='https://www.royalroad.com/fiction/25082/blue-core')
    try:
        db.session.add(fiction)
        db.session.commit()
    except:
        pass

    emails = read_gmail()
    html = ""
    for i in emails:
        html = html + "<a href = " + i.get('url') + ">" + i.get('chapterTitle') + "</a><br></br>"
    for i in chapterList:
        html = html + "<a href = " + i.get('url') + ">" + i.get('title') + "</a><br></br>"

    return html


if __name__ == '__main__':
    app.run()

def read_gmail():
    username = "webnovelaggregator1999@gmail.com"
    password = "18Nmiller="

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")

    # total number of emails
    messages = int(messages[0])

    for i in range(1, messages + 1):

        emails = []
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
        name = name.split('"')[1]
        chapter = {"chapterTitle": name,
                   "url": BeautifulSoup(body, 'lxml').find_all('a')[2].attrs.get('href')
                   }
        emails.append(chapter)
    # close the connection and logout
    imap.close()
    imap.logout()
    return emails

def updateChapters(chapterList):
    for chapter in chapterList:
        try:
            chappy = Chapters(fiction_id=Fictions.query.filter_by(name=chapter.get('fiction')).first().fiction_id, url=chapter.get('url'),
                              title=chapter.get('title'))
            db.session().add(chappy)
            db.session.commit()
        except:
            pass


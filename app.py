import time

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

from DatabaseUtilities import DatabaseUtilities

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Users\\natmi\\PycharmProjects\\WebNovelAggregator\\identifier.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db_utils = DatabaseUtilities(app)


@app.route('/')
def home():
    # Add any new chapters from RoyalRoad to database
    start = time.perf_counter()
    db_utils.update_RR_fictions()
    print("Time taken to update RR Fictions: %f" % (time.perf_counter() - start))

    # Add new chapters from the emails in aggregator inbox
    start = time.perf_counter()
    db_utils.update_patreon_chapters()
    print("Time taken to update Patreon Chapters: %f" % (time.perf_counter() - start))

    start = time.perf_counter()
    fiction_list = db_utils.get_new_chapters()
    print("Time taken to get new chapters for fiction_list: %f" % (time.perf_counter() - start))

    # Mark all chapters of a fiction as read
    # db_utils.mark_all_as_read(Fictions.query.all()[1])
    return render_template('homepage.html', title='My Updated WebNovels', fictionList=fiction_list,
                           fictionListLen=len(fiction_list), sorry="No New Chapters, sorry ):")


@app.route('/addFiction', methods=['GET', 'POST'])
def add_fiction():
    if request.method == 'POST':
        fiction = request.form.get("fname").strip()
        author = request.form.get("fauth").strip()
        url = request.form.get("furl").strip()
        site = request.form.get("fsite").strip()
        db_utils.add_fiction(fiction, author, url, site)
        db_utils.update_patreon_chapters()
        db_utils.update_RR_fictions(url)
        db_utils.mark_all_as_read(url)
    return redirect('/')


@app.route('/mark_chapter_as_read', methods=['GET', 'POST'])
def mark_chapter_as_read():
    # Mark the chapter as read
    db_utils.mark_chapter_as_read(request.form.get('chapter_url'))

    # Refresh the page
    return redirect('/')


if __name__ == '__main__':
    app.run()

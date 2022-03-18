import time

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

from DatabaseUtilities import DatabaseUtilities

app = Flask(__name__)

# Absolute File Path for database file. Should be changed for each user.
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Program Files\\WebNovelAggregator\\identifier.sqlite"
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


    # Dict of fictions and chapter lists.
    # Key = string of fiction name
    # Value = tuple of (len of chapter list, list of chapters)
    fiction_list = db_utils.get_new_chapters()

    # Mark all chapters of a fiction as read
    # db_utils.mark_all_as_read(Fictions.query.all()[1])

    # Pass all necessary chapter and fiction information to be rendered by the template
    return render_template('homepage.html', title='My Updated WebNovels', fictionList=fiction_list,
                           fictionListLen=len(fiction_list), sorry="No New Chapters, sorry ):")


@app.route('/addFiction', methods=['GET', 'POST'])
def add_fiction():
    # Get the form from the webpage with new fiction information
    if request.method == 'POST':
        fiction = request.form.get("fname").strip()
        author = request.form.get("fauth").strip()
        url = request.form.get("furl").strip()
        site = request.form.get("fsite").strip()

        # Add the fiction to the database
        db_utils.add_fiction(fiction, author, url, site)

        # Update the fiction with its chapters based on the site specified
        if site == 0:
            db_utils.update_patreon_chapters()
        else:
            db_utils.update_RR_fictions(url)

        # Mark all of the fiction's chapters as read
        db_utils.mark_all_as_read(url)
    return redirect('/')


# Mark a chapter that is clicked on as read in the database
@app.route('/mark_chapter_as_read', methods=['GET', 'POST'])
def mark_chapter_as_read():
    # Mark the chapter as read
    db_utils.mark_chapter_as_read(request.form.get('chapter_url'))

    # Refresh the page
    return redirect('/')

if __name__ == '__main__':
    app.run()

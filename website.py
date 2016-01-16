from flask import Flask, render_template, g
import sqlite3
import datetime
import fantasybball as fb

app = Flask(__name__)
date_obj = datetime.date.today()  # Get today's date
date = str(date_obj)
date_long = date_obj.strftime("%B %d %Y")
injurylist = fb.injurylist()

conn = sqlite3.connect("../stats.sqlite")
cur = conn.cursor()
date_test = cur.execute('''
    SELECT date
    FROM Dates
    WHERE date=?
    ''', (date, )).fetchall()
cur.close()

if not date_test:
    import statload

"""
See explanation for connection to a sqlite database at
http://opentechschool.github.io/python-flask/extras/databases.html
"""


@app.before_request  # Runs function before every request from browser
def before_request():
    # Connect to database
    g.db = sqlite3.connect("../stats.sqlite")


@app.teardown_request  # Closes the database connection after every request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')  # Routes method to home directory online
def get_stats():
    # Gets change stats from database and renders to html template
    # Select team neams
    names = g.db.execute('''
        SELECT Teams.name
        FROM Teams
        JOIN Pergame_rank
        ON Teams.id = Pergame_rank.team_id
        WHERE date_id=18
        ''').fetchall()

    # Get date_id for today's date
    date_id = g.db.execute('''
        SELECT id
        FROM Dates
        WHERE date=?
        ''', (date, )).fetchone()[0]

    # Get per game statistics
    stats = g.db.execute('''
        SELECT THREES, AST, BLK, FG, FT, PTS, REB, STL
        FROM Pergame_stats
        WHERE date_id=?
        ''', (date_id, )).fetchall()

    # Get per game rankings
    rankings = g.db.execute('''
        SELECT THREES, AST, BLK, FG, FT, PTS, REB, STL, TOTAL
        FROM Pergame_rank
        WHERE date_id=?
        ''', (date_id, )).fetchall()

    # Get per game rankings
    changes = g.db.execute('''
        SELECT THREES, AST, BLK, FG, FT, PTS, REB, STL, TOTAL
        FROM Change_stats
        WHERE date_id=?
        ''', (date_id, )).fetchall()

    return render_template('index.html',
                           stats=stats,
                           date=date_long,
                           names=names,
                           rankings=rankings,
                           changes=changes,
                           injuries=injurylist.to_html(index=False))

if __name__ == '__main__':
    app.run(debug=True)

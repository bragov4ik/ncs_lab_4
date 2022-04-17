from flask import Flask, make_response, render_template, request, g

from db import get_db

app = Flask(__name__)
DATABASE = './database.db'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    
def post_feedback(author, text):
    with get_db() as conn:
        # Right way (+ escape)
        # conn.cursor().execute(
        #     "INSERT INTO feedback (author, text) VALUES (?, ?);",
        #     (author, text)
        # )
        q = "INSERT INTO feedback (author, text) VALUES ('{}', '{}');".format(
            author, text
        )
        conn.cursor().executescript(q)
    print("Saved feedback {}: {}".format(author, text))

def get_all_feedback():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT author, text FROM feedback;")
        return cur.fetchall()

@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == "POST":
        print(request.form)
        post_feedback(
            request.form['author'],
            request.form['text']
        )
        entries = get_all_feedback()
        return render_template(
            "feedback.html",
            entries=entries,
            submitted=True
        )
    elif request.method == "GET":
        entries = get_all_feedback()
        return render_template("feedback.html", entries=entries)

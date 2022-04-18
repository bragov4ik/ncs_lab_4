from flask import Flask, render_template, request, g, redirect
from markupsafe import escape

from db import get_db
from utils import prepare_response

app = Flask(__name__)
DATABASE = './database.db'


@app.teardown_appcontext
def close_connection(_):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def post_feedback(author, text):
    with get_db() as conn:
        author = author[:128]
        text = text[:512]
        author = escape(author)
        text = escape(text)
        conn.cursor().execute(
            "INSERT INTO feedback (author, text) VALUES (?, ?);",
            (author, text)
        )
    print("Saved feedback {}: {}".format(author, text))


def get_all_feedback():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT author, text FROM feedback;")
        return cur.fetchall()


def get_token(user, password):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password, auth_cookie FROM users WHERE login = ?;", (user,))
        res = cur.fetchone()
        if not res:
            return None
        p, t = res
        if password != p:
            return None
        return t


def get_is_admin(token):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE auth_cookie = ?;", (token,))
        res = cur.fetchone()
        if res:
            return res[0]
        return None


@app.route("/")
@app.route("/index.html")
def index():
    return prepare_response(render_template("index.html"))


@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == "POST":
        print(request.form)
        post_feedback(
            request.form['author'],
            request.form['text']
        )
        entries = get_all_feedback()
        return prepare_response(render_template(
            "feedback.html",
            entries=entries,
            submitted=True
        ))
    elif request.method == "GET":
        entries = get_all_feedback()
        return prepare_response(
            render_template("feedback.html", entries=entries)
        )


@app.route("/login", methods=['GET'])
def login():
    return prepare_response(render_template("login.html"))


@app.route("/set_cookie", methods=['GET'])
def set_cookie():
    user = request.args.get('login')
    password = request.args.get('password')
    token = get_token(user, password)
    if not token:
        return prepare_response("Something went wrong!")
    ret = redirect("/user_page")
    ret.set_cookie('auth', token)
    return ret


@app.route("/user_page", methods=['GET'])
def user_page():
    token = request.cookies.get('auth')
    if not token:
        return redirect("/login")
    is_admin = get_is_admin(token)
    return prepare_response(render_template("user_page.html", admin=bool(is_admin)))


@app.route("/admin_only", methods=['GET'])
def admin_only():
    # Broken access control error
    # Right way:
    token = request.cookies.get('auth')
    if get_is_admin(token):
        return prepare_response(render_template("admin_only.html"))
    return prepare_response("You are not admin!")

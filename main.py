from datetime import datetime
import os

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Task, User

app = Flask(__name__)
#app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/all')
def all_tasks():
    return render_template('all.jinja2', tasks=Task.select())

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        # If a user is NOT logged in (username not in the dict(session), they cannot create a task
        # They will instead be redirected to the login screen
        return redirect(url_for('login'))
    # If the method is POST:
    #    then use the name that the user submitted to create a
    #    new task and save it
    #    Also, redirect the user to the list of all tasks
    # Otherwise, just render the create.jinja2 template
    if request.method == 'POST':
        task = Task(name=request.form['name'])
        task.save()

        return redirect(url_for('all_tasks'))
    else:
        return render_template('create.jinja2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # If the user is attempting to submit the login form (method is POST)
        #    Find a user from the database that matches the username provided in the form submission
        person = User.select().where(User.name == request.form['name']).get()
        if person and pbkdf2_sha256.verify(request.form['password'], person.password):
            #    If you find such a user and their password matches the provided password:
            #        Then log the user in by settings session['username'] to the users name
            #        And redirect the user to the list of all tasks
            session['username'] = request.form['name']
            return redirect(url_for('all_tasks'))
        else:
            #    Else:
            #        Render the login.jinja2 template and include an error message
            return render_template('login.jinja2', error="Incorrect username or password")
    else:
        # Else the user is just trying to view the login form
        #    so render the login.jinja2 template
        return render_template('login.jinja2')

@app.route('/incomplete', methods=['GET', 'POST'])
def incomplete_tasks():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            user = User.select().where(User.name == session['username']).get()
            Task.update(performed=datetime.now(), performed_by=user).where(Task.id == request.form['task_id']).execute()

    return render_template('incomplete.jinja2', tasks=Task.select().where(Task.performed.is_null()))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

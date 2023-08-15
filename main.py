from datetime import datetime
import os

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Task, User

app = Flask(__name__)
# app.secret_key = b'\xe4\xb9\xe9\xceO\x16\x94AN\xa3\xefs\x10I\xee\x80\x17\xe84\xa9\xc3\x91\x15a'
app.secret_key = os.environ.get('SECRET_KEY').encode()


@app.route('/all')
def all_tasks():
    return render_template('all.jinja2', tasks=Task.select())


@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        task = Task(name=request.form['name'])
        task.save()

        return redirect(url_for('all_tasks'))
    else:
        return render_template('create.jinja2')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.select().where(User.name == request.form['name']).get()

        if user and pbkdf2_sha256.verify(request.form['password'], user.password):
            session['username'] = request.form['name']
            return redirect(url_for('all_tasks'))

        return render_template('login.jinja2', error="Incorrect username or password.")

    else:
        return render_template('login.jinja2')


@app.route('/incomplete', methods=['GET', 'POST'])
def incomplete_tasks():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user = User.select().where(User.name == session['username']).get()

        Task.update(performed=datetime.now(), performed_by=user) \
            .where(Task.id == request.form['task_id']) \
            .execute()

    return render_template('incomplete.jinja2', tasks=Task.select().where(Task.performed.is_null()))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

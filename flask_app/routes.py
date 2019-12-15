from flask import Flask, render_template, url_for, redirect, request, Blueprint
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from flask_login import login_user, current_user, logout_user, login_required
from flask_app.model import User
from flask_app.forms import RegistrationForm, LoginForm
from flask_app import app, db

dorms = []

@app.route('/')
def index():
    global dorms
    response = requests.get('http://reslife.umd.edu/hallsatglance/')
    soup = BeautifulSoup(response.text, features="html.parser")

    lists = soup.find_all("td", {"width" : "62"})
    cutoff = lists[1:]

    dorms = list(map(lambda dorm: dorm.get_text(), filter(lambda tag:tag.get_text()!="", cutoff)))

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('users.login'))

    return render_template('main.html', dorms=dorms, form=form)

@app.route('/home')
def home():
    global dorms
    return render_template('home.html', dorms=dorms)

@app.route('/details/<dorm>')
def details(dorm):
    return render_template('details.html', dorm=dorm)

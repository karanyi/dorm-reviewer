from flask import Flask, render_template, url_for, redirect, request, Blueprint, session
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from flask_login import login_user, current_user, logout_user, login_required
from flask_app.model import User
from flask_app.forms import RegistrationForm, LoginForm, UpdateForm
from flask_app import db, bcrypt

import qrcode
import qrcode.image.svg as svg

from io import BytesIO

dorms = []

users = Blueprint("users", __name__)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/home')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect('/home')

    return render_template('login.html', title='Login', form=form)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect('/home')

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(username=form.username.data, password=hashed)
        db.session.add(user)
        db.session.commit()

        # return redirect(url_for('users.login'))
        session['reg_username'] = user.username

        return redirect(url_for('users.tfa'))
    
    return render_template('register.html', title='Register', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@users.route("/tfa")
def tfa():
    if 'reg_username' not in session:
        return redirect(url_for('main.index'))

    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return render_template('tfa.html'), headers

@users.route("/qr_code")
def qr_code():
    if 'reg_username' not in session:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(username=session['reg_username']).first()

    session.pop('reg_username')

    img = qrcode.make(user.get_auth_uri(), image_factory=svg.SvgPathImage)

    stream = BytesIO()

    img.save(stream)

    headers = {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0' # Expire immediately, so browser has to reverify everytime
    }

    return stream.getvalue(), headers

@users.route("/profile", methods=["GET", "POST"])
def profile():
    form = UpdateForm()

    if form.validate_on_submit():
        current_user.username = form.username.data

        db.session.commit()

        return redirect(url_for('users.profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
    
    return render_template('profile.html', title='Account', form=form)
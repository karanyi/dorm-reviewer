from flask import Flask, render_template, url_for, redirect, request, Blueprint
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from flask_login import login_user, current_user, logout_user, login_required
from flask_app.model import User, Review
from flask_app.forms import RegistrationForm, LoginForm, ReviewForm
from flask_app import db, bcrypt

dorms = []

main = Blueprint("main", __name__)

def removeEscapeSequences(word):
    word = word.replace('\t', '')
    word = word.replace('\n', '')
    return word

@main.route('/')
def index():
    global dorms
    response = requests.get('http://reslife.umd.edu/hallsatglance/')
    soup = BeautifulSoup(response.text, features="html.parser")

    lists = soup.find_all("td", {"width" : "62"})
    cutoff = lists[1:]

    dorms = list(map(lambda dorm: removeEscapeSequences(dorm), map(lambda dorm: dorm.get_text(), filter(lambda tag:tag.get_text()!="", cutoff))))

    if current_user.is_authenticated:
        return redirect('/home')

    registrationForm = RegistrationForm()
    loginForm = LoginForm()

    return render_template('main.html', dorms=dorms, loginForm=loginForm, registrationForm=registrationForm)

@main.route('/review/<dorm>', methods=["GET", "POST"])
def review(dorm):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(dorm=dorm, amenities=int(form.amenities.data), location=int(form.location.data),
            social=int(form.social.data), comment=form.comments.data, author=current_user)
        db.session.add(review)
        db.session.commit()

        return redirect('/home')
    
    return render_template('review.html', dorm=dorm, form=form)

@main.route('/home')
def home():
    global dorms
    lst = []

    for dorm in dorms:
        reviews = Review.query.filter_by(dorm=dorm)
        count = 0
        for review in reviews:
            count += review.location + review.social + review.amenities
        lstReviews = list(reviews)
        if (len(lstReviews) == 0):
            average = 'N/A'
        else:
            average = round(count / (len(list(reviews)) * 3), 2)
        lst.append((dorm, average))

    print(lst)
    return render_template('home.html', dorms=lst)

@main.route('/details/<dorm>')
def details(dorm):
    reviews = Review.query.filter_by(dorm=dorm)

    if (len(list(reviews)) != 0):
        averageSocial = 0
        averageLocation = 0
        averageAmenities = 0
        for review in reviews:
            averageSocial += review.amenities
            averageLocation += review.social
            averageAmenities += review.amenities
        
        averageSocial = round(averageSocial / len(list(reviews)), 2)
        averageLocation = round(averageLocation / len(list(reviews)), 2)
        averageAmenities = round(averageAmenities / len(list(reviews)), 2)
    else:
        averageSocial = 'N/A'
        averageLocation = 'N/A'
        averageAmenities = 'N/A'

    return render_template('details.html', dorm=dorm, social=averageSocial, 
        location=averageLocation, amenities=averageAmenities, reviews=reviews)

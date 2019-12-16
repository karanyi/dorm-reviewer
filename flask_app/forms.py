from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from flask_login import current_user

from flask_app.model import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        print("YEEEEEET")
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is taken')

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError("That username does not exist in our database.")

class ReviewForm(FlaskForm):
    amenities = RadioField("Amenities", choices=[('1', '1'), ('2', '2'), 
        ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), 
        ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], default='1')
    location = RadioField("Location", choices=[('1', '1'), ('2', '2'), 
        ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), 
        ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], default='1')
    social = RadioField("Social", choices=[('1', '1'), ('2', '2'), 
        ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), 
        ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')], default='1')
    comments = TextAreaField("Comments", render_kw={"rows": 10, "cols": 50},
        validators=[DataRequired()])
    submit = SubmitField("Submit Review")

class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('That username is already taken')
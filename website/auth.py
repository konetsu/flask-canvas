from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators
from wtforms.validators import DataRequired
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, current_user
auth = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username=StringField("Username",[validators.DataRequired(), validators.Length(min=3,max=20,message="min 3, max 20 characters")])
    password=StringField("Password",[validators.DataRequired(), validators.Length(min=6,max=50,message="min 6, max 50 characters")])
    button=SubmitField("Login")

class RegisterForm(FlaskForm):
    username=StringField("Username",[validators.DataRequired(), validators.Length(min=3,max=20,message="min 3, max 20 characters")])
    password=PasswordField("Password",[validators.DataRequired(), validators.Length(min=6,max=50,message="min 6, max 50 characters")])
    password2=PasswordField("Password 2",[validators.DataRequired(), validators.Length(min=6,max=50,message="min 6, max 50 characters")])
    button=SubmitField("Register")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    loginform=LoginForm()
    if loginform.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                session.permanent = True
                db.session.commit()
                return redirect(url_for('views.home'))
            else:
                flash('wrong password.')
                return redirect(url_for('auth.login'))
        else:
            flash('this username doesn not exist.')
            return redirect(url_for('auth.login'))
    return render_template("login.html", loginform=loginform)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    registerform=RegisterForm()
    if request.method=="POST":
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('password2')
        user = User.query.filter_by(username=username).first()
        if not username.isalnum():
            flash('Username can only contain letters and numbers.')
            return redirect(url_for('auth.register'))
        elif user:
            flash('this username has been taken: '+username)
            return redirect(url_for('auth.register'))
        elif len(username) < 3:
            flash('username must be 3+ characters.')
            return redirect(url_for('auth.register'))
        elif password1 != password2:
            flash('passwords did not match.')
            return redirect(url_for('auth.register'))
        elif len(password1) < 6:
            flash('password must be 6+ characters.')
            return redirect(url_for('auth.register'))
        else:
            new_user = User(
                            username=username,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session.permanent = True
            return redirect(url_for('views.home'))
    return render_template("register.html", registerform=registerform)
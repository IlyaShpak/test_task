import pickle
import pandas as pd
import json
import os

from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from my_app import app, db
from my_app.models import User, UserResult
from my_app.xgb_model import preprocess_data

filename = os.path.abspath("my_app/xgb_models/model.sav")
model = pickle.load(open(filename, "rb"))


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')


@app.route('/main', methods=['GET'])
@login_required
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            app.logger.info('User logged in')
            login_user(user)
            return redirect(url_for('main'))
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    email = request.form.get('email')
    existing_user = User.query.filter_by(login=login).first()
    user_with_same_email = User.query.filter_by(email=email).first()
    if user_with_same_email:
        flash('User with this email already exists!')
        return render_template('register.html')
    if existing_user:
        flash('User with this login already exists!')
        return render_template('register.html')
    if request.method == 'POST':
        if not (login and password and password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        elif not email:
            flash('Please fill email!')
        else:
            app.logger.info('New user registered')
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd, email=email)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('main'))

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    app.logger.info('User logged out')
    logout_user()
    return redirect(url_for('hello_world'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    username = current_user.login
    email = current_user.email
    pet_name = current_user.pet_name
    number_of_calculations = current_user.number_of_calculations
    if pet_name is None:
        pet_name = ''
    return render_template('profile.html', username=username, email=email,
                           pet_name=pet_name, number_of_calculations=number_of_calculations)


@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']
        new_pet_name = request.form['pet_name']
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            user_with_same_login = User.query.filter_by(login=new_username).first()
            user_with_same_email = User.query.filter_by(email=new_email).first()

            if user_with_same_login and user_with_same_login.id != current_user.id:
                flash('User with this username already exists')
            elif user_with_same_email and user_with_same_email.id != current_user.id:
                flash('User with this email already exists')
            else:
                app.logger.info('Editing user profile')
                user.login = new_username
                user.email = new_email
                user.pet_name = new_pet_name
                db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash('User not found')
            return redirect(url_for('profile'))

    return render_template('profile.html')


@app.route('/load', methods=['GET'])
@login_required
def load_data():
    return render_template("load_data.html")


@app.route('/process_data', methods=['POST'])
@login_required
def process_data():
    json_result = None
    file = request.files['file']
    try:
        data = pd.read_csv(file)
    except Exception as e:
        app.logger.error(f"Error reading CSV file: {e}")
        flash('Please upload a csv file')
    try:
        data = preprocess_data(data)
        try:
            prediction = model.predict(data).tolist()
            json_result = json.dumps(prediction)
            user_id = current_user.id
            user = User.query.filter_by(id=user_id).first()
            user.number_of_calculations += 1
            user_results = UserResult(user_id=user_id, json_result=json_result)
            app.logger.info(f"Successful prediction")
            db.session.add(user_results)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error predicting data: {e}")
            flash('Error processing data')
    except Exception as e:
        app.logger.error(f"Error preprocessing data: {e}")
        flash('Error preprocessing data')

    return json_result


@app.route('/download_results', methods=['GET'])
@login_required
def download_results():
    app.logger.info('Downloading results')
    user_result = UserResult.query.filter_by(user_id=current_user.id).order_by(UserResult.id.desc()).first()
    return jsonify(user_result.json_result), 200, {'Content-Disposition': 'attachment; filename="results.json"'}


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response

from flask import Flask, render_template, url_for, session, redirect, jsonify, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import time
import datetime
import os
import random
import string


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mathenge,./1998@localhost/dantee'
app.config['SECRET_KEY'] = 'some=secret+key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import *

@app.route('/register')
def register():
    return render_template('register.html')
# owner registration occurs

@app.route('/user_reg', methods=['POST'])
def user_reg():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        rank = request.form['rank']
        newrank = rank.upper()
        workid = request.form['workid']
        password = request.form['password']
        confirmpass = request.form['confirmpass']

        if password != confirmpass:
            flash('Passwords dont match', 'danger')
            return redirect(url_for('register'))
        elif Officers.check_email_exist(email):
            flash('Email already in use', 'danger')
            return redirect(url_for('register'))
        else:
            try:     
                hashpassword = bcrypt.generate_password_hash(
                password).decode('utf-8')
                y = Officers(name=name, email=email,
                        phone_number=phone, password=hashpassword,work_id=workid,officer_rank=newrank)
                insert = y.insert_record()            
                flash('Account successfully created', 'success')
                return redirect(url_for('login'))
            except:
                flash('Account creation failed. check your credentials and try again', 'danger')
                return redirect(url_for('register'))
    return redirect(url_for('register'))


@app.route('/')
def login():
    return render_template('login.html')

@app.route('/user/log_in', methods=['POST'])
def officers_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if Officers.check_email_exist(email):
            if Officers.validate_password(email=email, password=password):
                uid = Officers.get_officers_id_by_email(email)
                session['uid'] = uid
                getrank = Officers.check_ocpd(uid)
                print(getrank)
                if getrank:
                    return redirect(url_for('ocpd_home'))
                else:
                    return redirect(url_for('officer_home'))
            else:
                flash('Invalid login credentials', 'danger')
                return redirect(url_for('owner_login'))
        else:
            flash('Invalid login credentials', 'danger')
            return redirect(url_for('user_login'))
    else:
        flash('Incorrect Method', 'danger')
        return redirect(url_for('user_register'))

@app.route('/ocpd/home')
def ocpd_home():
    if 'uid' in session:
        names = []
        inmates = Offences.pending_processing()
        for inmate in inmates:
            iid = inmate.inmate
            name = Inmates.get_name_by_id(iid)
            names.append(name)
            officerid = inmate.arresting_officer
        return render_template('ocpdhome.html',offences = inmates,names = names)
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/officer/home')
def officer_home():
    if 'uid' in session:
        return render_template('officerhome.html')
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/officer/detainees')
def detainees():
    if 'uid' in session:
        names = []
        finallist = []
        inmates = Offences.pending_processing()
        for inmate in inmates:
            iid = inmate.inmate
            name = Inmates.get_name_by_id(iid)
            names.append(name)
            officerid = inmate.arresting_officer
        print(type(inmates))
        return render_template('detainees.html',offences = inmates,names = names)
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/ocpd/foward')
def all_detainees():
    if 'uid' in session:
        names = []
        finallist  = []
        inmates = Offences.pending_processing()
        for inmate in inmates:
            if inmate.category != "misdemeanor":
                finallist.append(inmate)
                iid = inmate.inmate
                name = Inmates.get_name_by_id(iid)
                names.append(name)
            else:
                names = []
                finallist  = []
        return render_template('ocpddetainees.html',offences = finallist,names = names)
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/ocpd/release')
def release_detainee():
    if 'uid' in session:
        names = []
        finallist  = []
        inmates = Offences.pending_processing()
        for inmate in inmates:
            if inmate.category != "felony" and inmate.category != "infraction":
                finallist.append(inmate)
                iid = inmate.inmate
                name = Inmates.get_name_by_id(iid)
                names.append(name)
            else:
                names = []
                finallist  = []
        return render_template('release.html',offences = finallist,names = names)
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/inmate/court/<int:iid>',methods = ['POST'])
def fowared_court(iid):
    if 'uid' in session:
        comment = request.form['comment']
        caseid = int(iid)
        insert = Courtcase(case = caseid,comments = comment)
        insert.insert_record()
        update = Offences.update_offence_by_id(caseid)
        if update:
            flash('Complete','success')
            return redirect(url_for('ocpd_home'))
        else:
            flash('Transaction incomplete','danger')
            return redirect(url_for('ocpd_home'))
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/inmate/bail/<int:iid>',methods = ['POST'])
def fowared_bail(iid):
    if 'uid' in session:
        amount = request.form['amount']
        caseid = int(iid)
        insert = Cashbails(case = caseid,amount = amount)
        insert.insert_record()
        update = Offences.update_offence_by_id(caseid)
        if update:
            flash('Complete','success')
            return redirect(url_for('ocpd_home'))
        else:
            flash('Transaction incomplete','danger')
            return redirect(url_for('ocpd_home'))
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login'))

@app.route('/ocpd/officers')
def officers():
    if 'uid' in session:
        allofficers = Officers.all()
        return render_template('allofficers.html',officers = allofficers)
    else:
        flash('Login to register','danger')
        return redirect(url_for('owner_login')) 
  
    

def register_offence(details):
    description = details['description']
    location = details['location']
    category = details['category']
    inmate = details['inmate']
    booking_officer = details['booking_officer']
    arresting_officer = details['arresting_officer']
    x = Offences(description = description,
        category=category, location = location,inmate = inmate,
        arresting_officer = arresting_officer,booking_officer = booking_officer)
    x.insert_record()
    return True


@app.route('/register-offence',methods = ['POST'])
def inmate_offence():
    if 'uid' in session:
        name = request.form['name']
        inmate_id_number = request.form['id']
        phone = request.form['phone']
        location = request.form['location']
        description = request.form['description']
        category = request.form['category']
        booking_officer = session['uid']
        arresting_officer = request.form['arrestingofficer']
        oid = Officers.get_id_by_work_id(arresting_officer)
        if oid:
            iid = Inmates.get_inmate_id_by_nid(inmate_id_number)
            if iid == False:
                x = Inmates(name = name, id_number=inmate_id_number,
                    phone_number=phone)
                x.insert_record()
                iid = Inmates.get_inmate_id_by_nid(inmate_id_number)
            details = {
                        'description':description,
                        'location':location,
                        'category':category,
                        'inmate':iid,
                        'booking_officer':session['uid'],
                        'arresting_officer': oid
                    }
            _offence = register_offence(details)
            if _offence:
                flash('Inmate Registered','success')
                return redirect(url_for('officer_home'))
            else:
                flash('error registering inmate','danger')
                return redirect(url_for('officer_home'))
        else:
            flash('Arresting officer not found','danger')
            return redirect(url_for('officer_home'))
    else:
        return redirect(url_for('login'))

@app.route('/logout',methods = ['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
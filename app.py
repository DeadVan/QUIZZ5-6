from flask import Flask, redirect, render_template, request,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from bs4 import BeautifulSoup
import requests


URL = "https://amindi.ge/ka/"
req = requests.get(URL)
soup = BeautifulSoup(req.content, 'html.parser')

weather = soup.find('div', class_='degrees')
weather = weather.text.strip()




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)
app.secret_key = "gasagebi"
app.permanent_session_lifetime = timedelta(minutes=20)


class Register(db.Model):
    id = db.Column('user_id',db.Integer,primary_key=True)
    username = db.Column('username',db.String(45))
    password = db.Column('password',db.String(55))

db.create_all()



@app.route('/registration',methods=['POST','GET'])
def registration():
    if request.method == "POST":
        session.permanent = True
        name = request.form['name']
        password = request.form['password']
        if len(name) == 0:
            flash("Name field is empty")
            return render_template("registration.html")

        elif len(password) == 0:
            flash("Password field is empty")
            return render_template("registration.html")

        elif len(name) < 6:
            flash("Name should be more than 5 characters")
            return render_template("registration.html")

        elif len(password) < 6:
            flash("Password should be more than 5 characters")
            return render_template("registration.html")

        if Register.query.filter_by(username=name).first():
            flash("Username already exist")
            return render_template("registration.html")

        else:
            user_info = Register(username=name,password=password)
            session.permanent = True
            session['user'] = name
            db.session.add(user_info)
            db.session.commit()
            return redirect(url_for('WelcomePage',yourname=name))
    return render_template("registration.html")

@app.route('/')
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        session.permanent = True
        name = request.form["name"]
        password = request.form["password"]
        if Register.query.filter_by(username=name,password=password).first():
            session['user'] = name
            return redirect(url_for('WelcomePage',yourname=name))
        flash("Username or Password is invalid")
        return render_template("login.html")
    if request.method == "GET":
        return render_template("login.html")

@app.route('/WelcomePage/<yourname>')
def WelcomePage(yourname):
    if 'user' not in session.keys():
        flash("Session time expired")
        return redirect(url_for("login"))
    elif yourname != session['user']:
        if 'user' in session.keys():
            user = session['user']
            flash("That page doesn't exist")
            return redirect(f'/WelcomePage/{user}')
        else:
            return redirect(url_for("login"))
    return render_template("base.html",content=yourname,curweather=weather)

@app.route('/logout')
def logout():
    session.pop('user',None)
    flash("you have logged out","info")
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')



if __name__ == '__main__':
    app.run(debug=True)
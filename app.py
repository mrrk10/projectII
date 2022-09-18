from curses import use_default_colors
import imp
from tkinter.messagebox import RETRY
from tokenize import String
from flask import Flask, render_template, url_for, flash, redirect,request
from flask_sqlalchemy import SQLAlchemy
# from flask_login import Mixin
from flask_wtf  import FlaskForm
# from wtforms import StringFiled,PasswordField,SubmitField 
from wtforms.validators import InputRequired,Length,ValidationError

import joblib
# from flask import request, jsonify
import numpy as np

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databse.db'
app.config['SECRET_KEY']="Thisis asecretkey"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(20), nullable=False,unique=True)
    password = db.Column(db.String(80),nullable=False)
    



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")    
def home():
    return render_template('home.html')

@app.route("/login")
def login():
    return render_template('login.html')    


    
@app.route("/register")
def register():
     # code to validate and add user to database goes here
    username = request.form.get('username')
    email= request.form.get('email')
    password = request.form.get('password')   

    username = User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database

    if username: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('register'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(username=username, email=email, password=generate_password_hash(password, method='rk256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

       
#######################################################################################
#prediction

def ValuePredictor(to_predict_list, size, algo):
    to_predict = np.array(to_predict_list).reshape(1,size)
    if(size==7):
        loaded_model = joblib.load(algo)
        result = loaded_model.predict(to_predict)
    return result[0]

@app.route('/predict1', methods = ["POST"])
def predict():
    prediction=""
    if request.method == "POST":

        form = request.form.to_dict()
        predict1 = predict2 = predict=None
        if 'predict1' in form:
            predict1 = form['predict1'] or None
            del form['predict1']
        
        if 'predict2' in form:
            predict2= form['predict2'] or None
            del form['predict2']

        if 'predict3' in form:
            predict3= form['predict3'] or None
            del form['predict3']

        to_predict_list = list(form.values())
        to_predict_list = list(map(float,to_predict_list))
        
        result = ""
        accuracy=""
        if predict1:
            if(len(to_predict_list)==7):
                result = ValuePredictor(to_predict_list,7,'hdp_model.pkl')
                accuracy = "You are data is predicted using Logistic Regression"
        elif predict2:
            if(len(to_predict_list)==7):
                result = ValuePredictor(to_predict_list,7,'randomf_model.pkl')
                accuracy = "You are data is predicted using Random Forest"
        elif predict3:
            if(len(to_predict_list)==7):
                result = ValuePredictor(to_predict_list,7,'randomf_model.pkl')
                accuracy = "You are data is predicted using Support Vector machine"        

        if(int(result)==1):
            prediction = "You have heart condition, Consult the doctor immediately"
        else:
            prediction = "You are safe. You have no dangerous symptoms !!! :-)"
    return(render_template("prediction_result.html", prediction_text=prediction,accuracy=accuracy))       

####################################################################################################

#API


@app.route('/api/predict/', methods = ["POST"])
def predict_api():
    prediction=""
    if request.method == "POST":

        form = request.json.to_dict()
        predict1 = predict2 = predict3=None
        if 'predict1' in form:
            predict1 = form['predict1'] or None
            del form['predict1']
        
        if 'predict2' in form:
            predict2= form['predict2'] or None
            del form['predict2']

        if 'predict3' in form:
            predict2= form['predict3'] or None
            del form['predict3']

        to_predict_list = list(form.values())
        to_predict_list = list(map(float,to_predict_list))
        
        result = ""
        accuracy=""
        if predict1:
            if(len(to_predict_list)==7):
                result = ValuePredictor(to_predict_list,7,'hdp_model.pkl')
                accuracy = "Logistic Regression Prediction"
        elif predict2:
            if(len(to_predict_list)==7):
                result = ValuePredictor(to_predict_list,7,'randomf_model.pkl')
                accuracy = "Random Forrest Prediction"
        elif predict3:
            if(len(to_predict_list)==7):
                result = ValuePredictor(to_predict_list,7,'svc_model.pkl')
                accuracy = "Support Vector Machine Prediction"

        if(int(result)==1):
            prediction = "You have heart condition, Consult the doctor immediately"
        else:
            prediction = "You are safe. You have no dangerous symptoms !!! :-)"
    return jsonify({'status': True,"prediction":prediction,"accuracy":accuracy})  







####################################################################################################
if __name__ == "__main__":
    # Use below for local flask deployment
    app.run(debug=True,port=5001)
    
    #Use below for AWS EC2 deployment
    #app.run(host='0.0.0.0',port=8081)

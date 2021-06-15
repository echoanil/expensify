from flask import Flask,render_template,request,redirect, send_from_directory, jsonify, url_for
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, ExpenseModel, db, login
from datetime import datetime, date
import config
import json
import os
 
app =Flask(__name__)
app.secret_key = config.SECRET

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expense_tracker.db"
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  
db.init_app(app)
login.init_app(app)
login.login_view = "login"
 
@app.before_first_request
def create_all():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard", _external=True))
    
    if request.method == "POST":
        email = request.form["email"]
        user = UserModel.query.filter_by(email = email).first()

        if user is not None and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard", _external=True))
        else:
            return render_template("login.html", message="The e-mail address and/or password you specified are not correct.")

    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard", _external=True))
     
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
 
        if UserModel.query.filter_by(email=email).first():
            return render_template("register.html", message="A user is already registered with this e-mail address.")
             
        user = UserModel(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login", _external=True))

    return render_template("register.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login", _external=True))

def remove(string):
    return string.replace(" ", "")

def total(cuser):
    exp = []
    inc = []
    for ex in cuser.expenses:
        if ex.ttype == "Expense":
            exp.append(ex.amount)
        elif ex.ttype == "Income":
            inc.append(ex.amount)
    total_expense = sum(exp)
    total_income = sum(inc)
    balance = total_income - total_expense

    return balance, total_expense, total_income

@app.route("/delete_expense", methods=["POST"])
def delete_expense():
    expense = json.loads(request.data)
    expenseId = expense['expenseId']
    expense = ExpenseModel.query.get(expenseId)
    if expense:
        if expense.user_id == current_user.id:
            db.session.delete(expense)
            db.session.commit()

    return jsonify({})

@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    balance, expense, income = 0, 0, 0
    balance, expense, income = total(current_user)
    if request.method == "POST":
        title = request.form["title"]
        amount = request.form["amount"]
        date = datetime.strptime(remove(request.form["date"]), '%m/%d/%Y')
        note = request.form["note"]
        ttype = request.form["ttype"]
        tag = request.form["tag"]
        new_expense = ExpenseModel(title=title, amount=amount, date=date, ttype=ttype, tag=tag, user_id=current_user.id)
        db.session.add(new_expense)
        db.session.commit()
        balance, expense, income = total(current_user)
        return render_template("dashboard.html", user=current_user, balance=balance, expense=expense, income=income)

    return render_template("dashboard.html", user=current_user, balance=balance, expense=expense, income=income)

@app.route("/recent_transactions")
@login_required
def recent():
    return render_template("recent.html", user=current_user)

def monthly(cuser):
    exp = [0] * 12
    inc = [0] * 12
    todays_date = date.today()
    
    for ex in cuser.expenses:
        if ex.date.year == todays_date.year:
            if ex.ttype == "Expense":
                exp[ex.date.month - 1] = exp[ex.date.month - 1] + ex.amount
            elif ex.ttype == "Income":
                inc[ex.date.month - 1] = inc[ex.date.month - 1] + ex.amount

    return exp, inc

@app.route("/stats")
@login_required
def stats():
    expense, income = monthly(current_user)
    return render_template("stats.html", expense=json.dumps(expense), income=json.dumps(income))

@app.route("/50-30-20-rule")
@login_required
def rule():
    return render_template("rule.html")

@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")

@app.errorhandler(500)
def handle_500(e):
    return render_template("500.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
   app.run(host='0.0.0.0',debug=False, port=8080)
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
 
login = LoginManager()
db = SQLAlchemy()

class ExpenseModel(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    amount = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    ttype = db.Column(db.String(200))
    tag = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
 
class UserModel(UserMixin, db.Model):
    __tablename__ = "users"
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String())
    expenses = db.relationship("ExpenseModel")
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
 
@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
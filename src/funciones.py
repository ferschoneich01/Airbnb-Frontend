from functools import wraps
from flask import Flask, session, redirect
from flask_session import Session

app = Flask(__name__)
# Set up database
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def login_required(f): 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def limpiarString(c):
    cad2 = ""
    # i = 0
    for cad in c:
        if cad == "[" or cad == "]" or cad == "(" or cad == ")" or cad == "," or cad == "%" or cad == "\'" or cad == "{" or cad == "}":
            cad == ""
        else:
            cad2 = cad2+cad
    return cad2

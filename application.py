import os
import time
import datetime

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash




from helpers import apology, login_required, usd


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# # Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///financetracker.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show current expenses and incomes"""

    if request.method == "GET":

        transactions = getTransactions()

        # for transaction in transactions:
        #     transaction['datetime'] = datetime.datetime.strptime(transaction['timestamp'], %Y-%m-d)

        # transactions_sorted = sorted(transactions, key=lambda k: k['datetime'])



        return render_template("index.html", expCategories=getExpCategories(), trips=getTrips(), transactions=transactions)





@app.route("/statistics", methods=["GET", "POST"])
@login_required
def statistics():
    """Show statistics"""

    if request.method == "GET":
        return returnToStatisitcs()



@app.route("/trips")
@login_required
def trips():
    """Show trips"""



    return render_template("trips.html", expCategories=getExpCategories(), trips=getTrips())



@app.route("/addExpenseIncomeTrip", methods=["POST"])
@login_required
def addExpenseIncomeTrip():

    # Handling of new expenses
    if request.form.get("expDate"):
        return addExpense()

    # Handling of new Income
    if request.form.get("incDate"):
        return addIncome()

    # Handling of new trips
    if request.form.get("tripTitle"):
        return addTrip()



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            #return apology("must provide username", 403)
            flash("You must provide a username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            #return apology("must provide password", 403)
            flash("You must provide a password!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":

        return render_template("register.html")

    else:

        # Ensure username was chosen
        if not request.form.get("username"):
            #return apology("must choose username", 403)
            flash("You must choose a username!")
            return redirect("/register")

        # Ensure password was chosen
        if not request.form.get("password"):
            #return apology("must choose password", 403)
            flash("You must choose a password!")
            return redirect("/register")

        # Ensure password was repeated correctly
        if not request.form.get("confirmation"):
            #return apology("must repeat password", 403)
            flash("You must confirm your password!")
            return redirect("/register")

        # Ensure that passwords coincide
        if request.form.get("password") != request.form.get("confirmation"):
            #return apology("passwords don't coincide", 403)
            flash("Your passwords do not match!")
            return redirect("/register")

        for username in getUserNames():
            if request.form.get("username") == username["username"]:
                flash("This username already exists!")
                return redirect("/register")


        hash_value = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash_value)", username=request.form.get("username"), hash_value=hash_value)

        #return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))[0]["id"]

        flash("Registered!")

        # Redirect user to home page
        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


def getUserNames():
    return db.execute("SELECT username FROM users")


def getUserData():
    return db.execute("SELECT * FROM users WHERE id = (:user_id)"
                                                    , user_id=session["user_id"])

def getExpCategories():
    return db.execute("SELECT * FROM expCategories")


def getTrips():
    return db.execute("SELECT id, title, startDate, endDate FROM trips WHERE user_id = :user_id",
                        user_id=session['user_id'])

def getTransactions():
    return db.execute("SELECT * FROM transactions LEFT JOIN expCategories ON transactions.expCategory_id = expCategories.id WHERE user_id = :user_id ORDER BY transactions.timestamp DESC", user_id=session['user_id'])


def returnToStart():
    return render_template("index.html", expCategories=getExpCategories(), trips=getTrips(), transactions=getTransactions())

def returnToStatisitcs():
    return render_template("statistics.html", expCategories=getExpCategories(), trips=getTrips())

def returnToTrips():
    return render_template("trips.html", expCategories=getExpCategories(), trips=getTrips())



def addExpense():
    # Check, if every necessary info was given
    if not request.form.get("category"):
        flash("You did not complete the form")
        return returnToStart()

    if not request.form.get("trip"):
        flash("You did not complete the form")
        return returnToStart()

    if not request.form.get("expAmount"):
        flash("You did not complete the form")
        return returnToStart()

    # Assign Values
    timestamp = request.form.get("expDate")
    category = int(request.form.get("category"))
    trip = int(request.form.get("trip"))
    amount = float(request.form.get("expAmount"))
    amount = float(f"{amount:,.2f}")
    notes = request.form.get("expNotes")
    exp = True


    db.execute("INSERT INTO transactions (user_id, expCategory_id, trip_id, timestamp, notes, amount, exp) VALUES (:user_id, :expCategory_id, :trip_id, :timestamp, :notes, :amount, :exp)",
    user_id=session["user_id"], expCategory_id=category, trip_id=trip, timestamp=timestamp, notes=notes, amount=amount, exp=exp)

    return redirect("/")


def addIncome():
    # Check, if every necessary informatin was given
    if not request.form.get("incAmount"):
        flash("You did not complete the form")
        return redirect("/")

    timestamp = request.form.get("incDate")
    amount = request.form.get("incAmount")
    notes = request.form.get("incNotes")
    exp = False

    db.execute("INSERT INTO transactions (user_id, timestamp, notes, amount, exp) VALUES (:user_id, :timestamp, :notes, :amount, :exp)",
    user_id=session["user_id"], timestamp=timestamp, notes=notes, amount=amount, exp=exp)

    return redirect("/")



def addTrip():
    # Check, if every necessary info was given
    if not request.form.get("startDate"):
        flash("You need to choose a start date")
        return redirect("/")

    if not request.form.get("endDate"):
        flash("You need to choose an end date")
        return redirect("/")

    title = request.form.get("tripTitle")
    startDate = request.form.get("startDate")
    endDate= request.form.get("endDate")

    db.execute("INSERT INTO trips (user_id, title, startDate, endDate) VALUES (:user_id, :title, :startDate, :endDate)",
                                        user_id=session['user_id'], title=title, startDate=startDate, endDate=endDate)

    return redirect("/")



import os
import time
import datetime
import calendar

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

        selectedDate = datetime.date.today()
        # print(selectedDate)
        # print(type(selectedDate))

        session["selected_date"] = selectedDate.isoformat()

        return toIndexWithoutRefresh()

        # for day in days:
        #     day['transactions'] = [{'id': transaction['id'], 'exp': transaction['exp'], 'notes': transaction['notes'], 'category': transaction['category'], 'amount': transaction['amount']} for transaction in transactions if transaction['DAY'] == day['DAY']]


@app.route("/changeToPrevMonth", methods=["GET"])
def changeToPrevMonth():

    changeMonth("prev")

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()

    return render_template('indexAJAX.html', days=days, month=getSumPerMonth(), transactions=transactions)


@app.route("/changeToNextMonth", methods=["GET"])
def changeToNextMonth():

    changeMonth("next")

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()

    return render_template('indexAJAX.html', days=days, month=getSumPerMonth(), transactions=transactions)


def changeMonth(m):

    selectedDate = datetime.date.fromisoformat(session["selected_date"])

    day = 1 if m == "prev" else calendar.monthrange(selectedDate.year, selectedDate.month)[1]
    selectedDate = selectedDate.replace(day=day)

    selectedMonth = selectedDate + datetime.timedelta(days=1 if m == "next" else -1)

    session['selected_date'] = selectedMonth.isoformat()



@app.route("/statistics", methods=["GET", "POST"])
@login_required
def statistics():
    """Show statistics"""

    if request.method == "GET":

        month = db.execute("""
            SELECT SUM(CASE WHEN transactions.exp = 1 THEN transactions.amount ELSE 0 END) * (-1) AS exp_per_category, expCategories.label AS label, transactions.expCategory_id
            FROM transactions
            JOIN expCategories ON transactions.expCategory_id = expCategories.id
            WHERE strftime('%Y-%m', transactions.timestamp) = strftime('%Y-%m', :selectedDate) AND transactions.user_id = :user_id
            GROUP BY transactions.expCategory_id
            ORDER BY exp_per_category DESC
            """,
            user_id=session['user_id'], selectedDate=session['selected_date'])

        monthTotal = db.execute("""
            SELECT SUM(CASE WHEN transactions.exp = 1 THEN transactions.amount ELSE 0 END) * (-1) AS t
            FROM transactions
            WHERE strftime('%Y-%m', transactions.timestamp) = strftime('%Y-%m', :selectedDate) AND transactions.user_id = :user_id
            """,
            user_id=session['user_id'], selectedDate=session['selected_date'])[0]['t']

        for category in month:
            category['percentage'] = round(category['exp_per_category'] / monthTotal *100)
            category['exp_per_category'] = format(round(abs(category['exp_per_category']), 2), ".2f")

        return render_template("statistics.html", expCategories=getExpCategories(), trips=getTrips(), month=month, monthTotal=monthTotal)

@app.route("/changeToPrevMonthStat", methods=["GET"])
def changeToPrevMonthStat():

    changeMonth("prev")

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()

    return render_template('statisticsAJAX.html', month=month, monthTotal=monthTotal)

@app.route("/changeToNextMonthStat", methods=["GET"])
def changeToNextMonthStat():

    changeMonth("next")

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()

    return render_template('statisticsAJAX.html', month=month, monthTotal=monthTotal)




@app.route("/statistics/<category>")
@login_required
def statisticCategory(category):

    return apology("yet to be implemented")




app.route("/trips")
@login_required
def trips():
    """Show trips"""

    return render_template("trips.html", expCategories=getExpCategories(), trips=getTrips())


@app.route("/trips/<trip>")
@login_required
def trip(trip):
    """Show data of selected Trip"""

    return apology("yet to be implemented")



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


@app.route("/editExpenses", methods=["POST"])
@login_required
def editExpenses():
    """Edit Expense"""

    # Check, if every necessary info was given
    if not request.form.get("editExpDate"):
        flash("You did not complete the form")
        return returnToStart()

    if not request.form.get("editExpCategory"):
        flash("You did not complete the form")
        return returnToStart()

    if not request.form.get("editExpTrip"):
        flash("You did not complete the form")
        return returnToStart()

    if not request.form.get("editExpAmount"):
        flash("You did not complete the form")
        return returnToStart()

    # Assign Values
    timestamp = request.form.get("editExpDate")
    category = int(request.form.get("editExpCategory"))
    trip = int(request.form.get("editExpTrip"))
    amount = float(request.form.get("editExpAmount"))
    amount = float(f"{amount:,.2f}") * (-1)
    notes = request.form.get("editExpNotes")
    # exp = True

    transaction_id = request.form.get("editExpId")

    db.execute("""
    UPDATE transactions
    SET timestamp = :timestamp, expCategory_id = :category, trip_id = :trip, amount = :amount, notes = :notes
    WHERE id = :transaction_id
    """,
    timestamp=timestamp, category=category, trip=trip, amount=amount, notes=notes,transaction_id=transaction_id)

    return toIndexWithoutRefresh()


@app.route("/editIncome", methods=["POST"])
@login_required
def editIncome():
    """Edit Income"""

    # Check, if every necessary info was given

    if not request.form.get("editIncDate"):
        flash("You did not complete the form")
        return returnToStart()

    if not request.form.get("editIncAmount"):
        flash("You did not complete the form")
        return returnToStart()

    # Assign Values
    timestamp = request.form.get("editIncDate")
    amount = float(request.form.get("editIncAmount"))
    amount = float(f"{amount:,.2f}")
    notes = request.form.get("editIncNotes")
    # exp = False

    transaction_id = request.form.get("editIncId")

    db.execute("""
    UPDATE transactions
    SET timestamp = :timestamp, amount = :amount, notes = :notes
    WHERE id = :transaction_id
    """,
    timestamp=timestamp, amount=amount, notes=notes, transaction_id=transaction_id)

    return toIndexWithoutRefresh()


@app.route("/deleteTransaction", methods=["POST"])
@login_required
def deleteTransaction():
    """Delete Transaction"""


    transaction_id = request.form.get("deleteId")

    db.execute("""
    DELETE FROM transactions
    WHERE id = :transaction_id
    """,
    transaction_id=transaction_id)

    return toIndexWithoutRefresh()



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
    return db.execute("SELECT id, title, startDate, endDate FROM trips WHERE user_id = :user_id ORDER BY startDate DESC",
                        user_id=session['user_id'])

def getTransactions():
    return db.execute("SELECT * FROM transactions LEFT JOIN expCategories ON transactions.expCategory_id = expCategories.id WHERE user_id = :user_id ORDER BY transactions.timestamp DESC", user_id=session['user_id'])



#month
def getSumPerMonth():
    month = db.execute("""
        SELECT SUM(CASE WHEN exp = 1 THEN amount ELSE 0 END) AS exp_per_month, SUM(CASE WHEN exp = 0 THEN amount ELSE 0 END) AS inc_per_month, SUM(amount) AS saldo,  strftime('%Y', timestamp) AS year, strftime('%m', timestamp) AS month
        FROM transactions
        WHERE user_id = :user_id AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', :selectedDate)
        """,
        user_id=session['user_id'], selectedDate=session['selected_date'])[0]

    if month['MONTH'] is None:
        month = {
            'month_name' : calendar.month_name[int(datetime.date.fromisoformat(session['selected_date']).month)],
            'YEAR' : datetime.date.fromisoformat(session['selected_date']).year,
            'exp_per_month' : 0.0,
            'inc_per_month' : 0.0,
            'saldo' : 0.0
            }
    else:
        month['month_name'] = calendar.month_name[int(month['MONTH'])]
        month['inc_per_month'] = format(round(month['inc_per_month'], 2), ".2f")
        month['exp_per_month'] = format(round(abs(month['exp_per_month']), 2), ".2f")
        month['saldo'] = format(round(month['saldo'], 2), ".2f")


    return month

# days
def getTransactionsCurrentMonthGroupedByDay():
    days = db.execute("""
        SELECT SUM(CASE WHEN exp = 1 THEN amount ELSE 0 END) AS exp_per_day, SUM(CASE WHEN exp = 0 THEN amount ELSE 0 END) AS inc_per_day, SUM(amount) AS saldo,  strftime('%Y', timestamp) AS year, strftime('%m', timestamp) AS month, STRFTIME('%d', timestamp) AS day
        FROM transactions
        WHERE user_id = :user_id AND year = strftime('%Y', :selectedDate) AND month = strftime('%m', :selectedDate)
        GROUP BY year, month, day
        ORDER by timestamp DESC""",
        user_id=session['user_id'], selectedDate=session['selected_date'])

    for day in days:
        day['exp_per_day'] = format(abs(day['exp_per_day']), ".2f")
        day['inc_per_day'] = format(day['inc_per_day'], ".2f")
        day['saldo'] = format(day['saldo'], ".2f")

    return days

# Transactions
def getTransactionsCurrentMonth():
    transactions = db.execute("""
        SELECT transactions.id, transactions.timestamp, transactions.expCategory_id, transactions.trip_id, transactions.notes, transactions.amount, transactions.exp, expCategories.label AS category, STRFTIME('%d', transactions.timestamp) AS day
        FROM transactions
        LEFT JOIN expCategories ON transactions.expCategory_id = expCategories.id
        WHERE user_id = :user_id AND strftime('%Y', transactions.timestamp) = strftime('%Y', :selectedDate) AND strftime('%m', transactions.timestamp) = strftime('%m', :selectedDate)
        ORDER BY transactions.timestamp DESC""",
        user_id=session['user_id'], selectedDate=session['selected_date'])

    for transaction in transactions:
        transaction['amount'] = format(abs(transaction['amount']), ".2f")

    return transactions

# allTransactions
def getAllTransactions():
    transactions =  db.execute("""
        SELECT transactions.id, transactions.timestamp, transactions.expCategory_id, transactions.trip_id, transactions.notes, transactions.amount, transactions.exp
        FROM transactions
        WHERE user_id = :user_id
        """,
        user_id=session['user_id'])

    for transaction in transactions:
        transaction['amount'] = format(abs(transaction['amount']), ".2f")

    return transactions




def returnToStart():
    return render_template("index.html", expCategories=getExpCategories(), trips=getTrips(), transactions=getTransactions(), allTransactions=getAllTransactions())




def returnToTrips():
    return render_template("trips.html", expCategories=getExpCategories(), trips=getTrips())



def addExpense():
    # Check, if every necessary info was given
    if not request.form.get("category"):
        flash("You did not complete the form")
        return toIndexWithoutRefresh()

    if not request.form.get("trip"):
        flash("You did not complete the form")
        return toIndexWithoutRefresh()

    if not request.form.get("expAmount"):
        flash("You did not complete the form")
        return toIndexWithoutRefresh()

    # Assign Values
    timestamp = request.form.get("expDate")
    category = int(request.form.get("category"))
    trip = int(request.form.get("trip"))
    amount = float(request.form.get("expAmount"))
    amount = float(f"{amount:,.2f}") * (-1)
    notes = request.form.get("expNotes")
    exp = True


    db.execute("INSERT INTO transactions (user_id, expCategory_id, trip_id, timestamp, notes, amount, exp) VALUES (:user_id, :expCategory_id, :trip_id, :timestamp, :notes, :amount, :exp)",
    user_id=session["user_id"], expCategory_id=category, trip_id=trip, timestamp=timestamp, notes=notes, amount=amount, exp=exp)

    return toIndexWithoutRefresh()


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

    return toIndexWithoutRefresh()



def addTrip():
    # Check, if every necessary info was given
    if not request.form.get("startDate"):
        flash("You need to choose a start date")
        return toIndexWithoutRefresh()

    if not request.form.get("endDate"):
        flash("You need to choose an end date")
        return toIndexWithoutRefresh()

    title = request.form.get("tripTitle")
    startDate = request.form.get("startDate")
    endDate= request.form.get("endDate")

    db.execute("INSERT INTO trips (user_id, title, startDate, endDate) VALUES (:user_id, :title, :startDate, :endDate)",
                                        user_id=session['user_id'], title=title, startDate=startDate, endDate=endDate)

    return toIndexWithoutRefresh()


def toIndexWithoutRefresh():

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()


    return render_template("index.html", expCategories=getExpCategories(), trips=getTrips(), days=days, month=getSumPerMonth(), transactions=transactions, allTransactions=getAllTransactions())
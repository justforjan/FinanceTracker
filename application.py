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
import requests




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




### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ### INDEX ###

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show current expenses and incomes"""

    if request.method == "GET":

        selectedDate = datetime.date.today()
        # print(selectedDate)
        # print(type(selectedDate))

        session["selected_date"] = selectedDate.isoformat()

        return render_template("index.html", expCategories=getExpCategories(), trips=getTrips(), countries=getCountries(), allTransactions=getAllTransactions())

        # for day in days:
        #     day['transactions'] = [{'id': transaction['id'], 'exp': transaction['exp'], 'notes': transaction['notes'], 'category': transaction['category'], 'amount': transaction['amount']} for transaction in transactions if transaction['DAY'] == day['DAY']]


@app.route("/changeMonth/<direction>", methods=["GET"])
def changeMonthIndex(direction):

    session['selected_date'] = changeMonth(session['selected_date'], direction)

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()

    return render_template('indexAJAX.html', days=days, month=getSumPerMonth(), transactions=transactions)



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
        ORDER BY transactions.timestamp DESC
        """,
        user_id=session['user_id'], selectedDate=session['selected_date'])

    for transaction in transactions:
        transaction['amount'] = format(abs(transaction['amount']), ".2f")

    return transactions


def toIndexWithoutRefresh():

    transactions = getTransactionsCurrentMonth()
    days = getTransactionsCurrentMonthGroupedByDay()

    return render_template("index.html", expCategories=getExpCategories(), trips=getTrips(), countries=getCountries(), days=days, month=getSumPerMonth(), transactions=transactions, allTransactions=getAllTransactions())



### STATISTICS ### STATISTICS ### STATISTICS ### STATISTICS ### STATISTICS ### STATISTICS ### STATISTICS ### STATISTICS ### STATISTICS ###

@app.route("/statistics", methods=["GET", "POST"])
@login_required
def statistics():
    """Show statistics"""

    if request.method == "GET":

        monthSum = getSumPerMonth()
        month = getMonthData(float(monthSum['exp_per_month']))

        return render_template("statistics.html", expCategories=getExpCategories(), trips=getTrips(), countries=getCountries(), month=month, monthSum=getSumPerMonth())

@app.route("/statistics/prevMonth", methods=["GET"])
def changeToPrevMonthStat():

    session['selected_date'] = changeMonth(session['selected_date'], "prev")

    return redirect("/statistics")

@app.route("/statistics/nextMonth", methods=["GET"])
def changeToNextMonthStat():

    session['selected_date'] = changeMonth(session['selected_date'], "next")

    return redirect("/statistics")



def getMonthData(monthTotal):
    month = db.execute("""
        SELECT SUM(CASE WHEN transactions.exp = 1 THEN transactions.amount ELSE 0 END) * (-1) AS exp_per_category, expCategories.label AS label, transactions.expCategory_id
        FROM transactions
        JOIN expCategories ON transactions.expCategory_id = expCategories.id
        WHERE strftime('%Y-%m', transactions.timestamp) = strftime('%Y-%m', :selectedDate) AND transactions.user_id = :user_id
        GROUP BY transactions.expCategory_id
        ORDER BY exp_per_category DESC
        """,
        user_id=session['user_id'], selectedDate=session['selected_date'])

    for category in month:
        category['percentage'] = round(category['exp_per_category'] / monthTotal *100)
        category['exp_per_category'] = format(round(abs(category['exp_per_category']), 2), ".2f")

    return month


@app.route("/statistics/<category>")
@login_required
def statisticCategory(category):

    # days = getTransactionsSortedByDayOfSelectedCategory(category)
    # transactions = getTransactionsCurrentMonthOfSelectedCategory(category)
    allTransactions = getAllTransactionsOfSelectedCategory(category)

    session['selected_category'] = category

    return render_template("categories.html", expCategories=getExpCategories(), trips=getTrips(), countries=getCountries(), categoryLabel=category, allTransactions=allTransactions)


@app.route("/statistics/changeMonth/<direction>", methods=["GET"])
def changeMonthCat(direction):

    session['selected_date'] = changeMonth(session['selected_date'], direction)

    days = getTransactionsSortedByDayOfSelectedCategory(session['selected_category'])
    transactions = getTransactionsCurrentMonthOfSelectedCategory(session['selected_category'])

    return render_template('indexAJAX.html', days=days, month=getMonthName(session['selected_date']), transactions=transactions)



# DAY with selected category
def getTransactionsSortedByDayOfSelectedCategory(category):
    days = db.execute("""
        SELECT SUM(CASE WHEN exp = 1 THEN transactions.amount ELSE 0 END) AS exp_per_day, SUM(CASE WHEN exp = 0 THEN transactions.amount ELSE 0 END) AS inc_per_day, SUM(transactions.amount) AS saldo,  strftime('%Y', transactions.timestamp) AS year, strftime('%m', transactions.timestamp) AS month, STRFTIME('%d', transactions.timestamp) AS day
        FROM transactions
        JOIN expCategories ON expCategories.id = transactions.expCategory_id
        WHERE transactions.user_id = :user_id AND year = strftime('%Y', :selectedDate) AND month = strftime('%m', :selectedDate) AND expCategories.label = :category
        GROUP BY year, month, day
        ORDER by timestamp DESC
        """,
    user_id=session['user_id'], selectedDate=session['selected_date'], category=category)

    for day in days:
        day['exp_per_day'] = format(abs(day['exp_per_day']), ".2f")
        day['inc_per_day'] = format(day['inc_per_day'], ".2f")
        day['saldo'] = format(day['saldo'], ".2f")

    return days

# TRANSACTIONS with selected category
def getTransactionsCurrentMonthOfSelectedCategory(category):
    transactions = db.execute("""
        SELECT transactions.id, transactions.timestamp, transactions.expCategory_id, transactions.trip_id, transactions.notes, transactions.amount, transactions.exp, expCategories.label AS category, STRFTIME('%d', transactions.timestamp) AS day
        FROM transactions
        LEFT JOIN expCategories ON transactions.expCategory_id = expCategories.id
        WHERE user_id = :user_id AND strftime('%Y', transactions.timestamp) = strftime('%Y', :selectedDate) AND strftime('%m', transactions.timestamp) = strftime('%m', :selectedDate) AND expCategories.label = :category
        ORDER BY transactions.timestamp DESC        """,
    user_id=session['user_id'], selectedDate=session['selected_date'], category=category)

    for transaction in transactions:
        transaction['amount'] = format(abs(transaction['amount']), ".2f")

    return transactions

# ALL TRANSACTIONS with selected category
def getAllTransactionsOfSelectedCategory(category):
    transactions =  db.execute("""
        SELECT transactions.id, transactions.timestamp, transactions.expCategory_id, transactions.trip_id, transactions.notes, transactions.amount, transactions.exp
        FROM transactions
        JOIN expCategories ON expCategories.id = transactions.expCategory_id
        WHERE user_id = :user_id AND expCategories.label = :category
        """,
    user_id=session['user_id'], category=category)

    for transaction in transactions:
        transaction['amount'] = abs(transaction['amount'])

    return transactions



### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ### TRIPS ###

@app.route("/trips")
@login_required
def trips():
    """Show trips"""

    return render_template("trips.html", expCategories=getExpCategories(), trips=getTrips(), countries=getCountries())


@app.route("/trips/<trip>")
@login_required
def selectedTrip(trip):
    """Show data of selected Trip"""

    selectedTripData = getSelectedTrip(trip)
    session['selected_trip_id'] = selectedTripData['id']
    session['selected_trip_title'] = selectedTripData['title']

    selectedTripExpCategories = getTripExpensesGroupedByCategory(selectedTripData['id'], selectedTripData['SUM'])

    session['selected_trip_month'] = selectedTripData['startDate']

    cc = db.execute("""
    SELECT country_code
    FROM countries
    WHERE trip_id = :trip_id
    """,
    trip_id=session['selected_trip_id'])

    selectedCountryCodes = [c['country_code'] for c in cc]

    # All Transactions
    allTransactions = getAllExpensesOfTrip(selectedTripData['id'])

    return render_template("trip.html", expCategories=getExpCategories(), trips=getTrips(), countries=getCountries(), tripData=selectedTripData, tripCategories=selectedTripExpCategories, allTransactions=allTransactions, countryCodes=selectedCountryCodes)


@app.route("/editTrip", methods=['POST'])
@login_required
def editTrip():
    """Edit Trip"""

    # Check, if every necessary info was given
    if not request.form.get("editTripTitle"):
        flash("You did not complete the form")
        return redirect("/trips")

    if not request.form.get("editStartDate"):
        flash("You did not complete the form")
        return redirect("/trips")

    if not request.form.get("editEndDate"):
        flash("You did not complete the form")
        return redirect("/trips")

    title = request.form.get("editTripTitle")
    startDate = request.form.get("editStartDate")
    endDate = request.form.get("editEndDate")
    trip_id = request.form.get("editTripId")
    countries =  request.form.getlist("editTripCountries")

    db.execute("""
        DELETE FROM countries
        WHERE trip_id = :trip_id
        """,
    trip_id=trip_id)

    insertCountries(countries, trip_id)

    db.execute("""
    UPDATE trips
    SET title = :title, startDate = :startDate, endDate = :endDate
    WHERE id = :trip_id
    """,
    title=title, startDate=startDate, endDate=endDate, trip_id=trip_id)

    return redirect("/trips/" + title)


@app.route("/deleteTrip", methods=['POST'])
@login_required
def deleteTrip():
    """Delete Trip"""

    # Check, if every necessary info was given

    option = request.form['option']
    trip_id = request.form.get("deleteTripId")

    db.execute("""
        DELETE FROM countries
        WHERE trip_id = :trip_id
        """,
    trip_id=trip_id)

    if option == 'option1':

        db.execute("""
            DELETE FROM transactions
            WHERE trip_id = :trip_id
        """,
        trip_id=trip_id)

        db.execute("""
            DELETE FROM trips
            WHERE id = :trip_id
        """,
        trip_id=trip_id)

    else:

        assignedTrip = request.form.get("expTripReassign")

        db.execute("""
            UPDATE transactions
            SET trip_id = :assignedTrip
            WHERE trip_id = :trip_id
        """,
        assignedTrip=assignedTrip, trip_id=trip_id)

    return redirect("/trips")


@app.route("/trips/changeMonth/<direction>")
@login_required
def changeMonthTrip(direction):
    """change month"""

    session['selected_trip_month'] = changeMonth(session['selected_trip_month'], direction)

    # Transactions
    transactions = getTripExpensesOfSelectedMonth(session['selected_trip_id'])

    # Day (Transactions sorted by day)
    days = getTripExpensesSelectedMonthGroupedByDay(session['selected_trip_id'])

    month = getMonthName(session['selected_trip_month'])

    return render_template("indexAJAX.html", transactions=transactions, days=days, month=month)



def getSelectedTrip(trip):
    trip = db.execute("""
        SELECT trips.id, trips.title, trips.startDate, trips.endDate, SUM(transactions.amount) * (-1) AS sum
        FROM trips
        LEFT JOIN transactions ON transactions.trip_id = trips.id
        WHERE trips.user_id = :user_id AND trips.title = :trip
        ORDER BY trips.startDate DESC
        """,
    user_id=session['user_id'], trip=trip)[0]

    startDate = datetime.date.fromisoformat(trip['startDate'])
    endDate = datetime.date.fromisoformat(trip['endDate'])

    trip['startMonth_name'] = calendar.month_abbr[int(startDate.month)]
    trip['startDay'] = startDate.day
    trip['startYear'] = startDate.year

    trip['endMonth_name'] = calendar.month_abbr[int(endDate.month)]
    trip['endDay'] = endDate.day
    trip['endYear'] = endDate.year

    trip['duration'] = (endDate - startDate).days + 1

    today = datetime.date.today()

    if endDate >= today:
        trip['current'] = True

    if trip['SUM'] != None:

        if endDate >= today:
            duration = (today - startDate).days + 1
            trip['daily_average'] = format(round((trip['SUM'] / float(duration)), 2), ".2f")

        else:
            trip['daily_average'] = format(round((trip['SUM'] / float(trip['duration'])), 2), ".2f")
    else:
        trip['daily_average'] = '0.00'
        trip['SUM'] = '0.00'

    return trip

def  getTripExpensesGroupedByCategory(trip_id, tripTotal):
    categories = db.execute("""
        SELECT SUM(CASE WHEN transactions.exp = 1 THEN transactions.amount ELSE 0 END) * (-1) AS exp_per_category, expCategories.label AS category_label, expCategories.id AS category_id
        FROM transactions
        JOIN expCategories ON transactions.expCategory_id = expCategories.id
        WHERE transactions.trip_id = :trip_id AND transactions.user_id = :user_id
        GROUP BY transactions.expCategory_id
        ORDER BY exp_per_category DESC
        """,
    trip_id=trip_id, user_id=session['user_id'])

    for category in categories:
        category['percentage'] = round(category['exp_per_category'] / tripTotal *100)

    return categories


# All Transactions of selected trip
def getAllExpensesOfTrip(trip_id):
    transactions =  db.execute("""
        SELECT transactions.id, transactions.timestamp, transactions.expCategory_id, transactions.trip_id, transactions.notes, transactions.amount, transactions.exp, expCategories.label
        FROM transactions
        LEFT JOIN expCategories ON expCategories.id = transactions.expCategory_id
        WHERE user_id = :user_id AND transactions.trip_id = :trip_id
        """,
    user_id=session['user_id'], trip_id=trip_id)

    for transaction in transactions:
        transaction['amount'] = format(abs(transaction['amount']), ".2f")

    return transactions

# TRANSACTIONS of selected month and trip
def getTripExpensesOfSelectedMonth(trip_id):
    transactions = db.execute("""
        SELECT transactions.id, transactions.timestamp, transactions.expCategory_id, transactions.trip_id, transactions.notes, transactions.amount, transactions.exp, expCategories.label AS category, STRFTIME('%d', transactions.timestamp) AS day
        FROM transactions
        LEFT JOIN expCategories ON transactions.expCategory_id = expCategories.id
        WHERE user_id = :user_id AND strftime('%Y-%m', transactions.timestamp) = strftime('%Y-%m', :selectedDate) AND transactions.trip_id = :trip_id
        ORDER BY transactions.timestamp DESC
        """,
        user_id=session['user_id'], selectedDate=session['selected_trip_month'], trip_id=trip_id)

    for transaction in transactions:
        transaction['amount'] = format(abs(transaction['amount']), ".2f")

    return transactions

# DAYS Transactions of selected month grouped by day of selected trip
def getTripExpensesSelectedMonthGroupedByDay(trip_id):
    days = db.execute("""
        SELECT SUM(CASE WHEN exp = 1 THEN amount ELSE 0 END) AS exp_per_day,  strftime('%Y', timestamp) AS year, strftime('%m', timestamp) AS month, STRFTIME('%d', timestamp) AS day
        FROM transactions
        WHERE user_id = :user_id AND year = strftime('%Y', :selectedDate) AND month = strftime('%m', :selectedDate) AND trip_id = :trip_id
        GROUP BY year, month, day
        ORDER by timestamp DESC
        """,
        user_id=session['user_id'], selectedDate=session['selected_trip_month'], trip_id=trip_id)

    for day in days:
        day['exp_per_day'] = format(abs(day['exp_per_day']), ".2f")

    return days






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
    trips = db.execute("""
        SELECT id, title, startDate, endDate
        FROM trips
        WHERE user_id = :user_id
        ORDER BY startDate DESC
        """,
        user_id=session['user_id'])

    for trip in trips:
        trip['startMonth_name'] = calendar.month_abbr[int(datetime.date.fromisoformat(trip['startDate']).month)]
        trip['startDay'] = datetime.date.fromisoformat(trip['startDate']).day
        trip['startYear'] = datetime.date.fromisoformat(trip['startDate']).year

        trip['endMonth_name'] = calendar.month_abbr[int(datetime.date.fromisoformat(trip['endDate']).month)]
        trip['endDay'] = datetime.date.fromisoformat(trip['endDate']).day
        trip['endYear'] = datetime.date.fromisoformat(trip['endDate']).year

        trip['country_codes'] = db.execute("""
            SELECT country_code
            FROM countries
            WHERE trip_id = :trip_id
            LIMIT 4
        """,
        trip_id=trip['id'])

    print(trips[1])

    return trips



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
    countries = request.form.getlist("tripCountries")

    print('SELECTED COUNTRIES')
    print(countries)
    print(type(countries))
    print("-----------------------------------------------")

    db.execute("""
        INSERT INTO trips (user_id, title, startDate, endDate)
        VALUES (:user_id, :title, :startDate, :endDate)
    """,
    user_id=session['user_id'], title=title, startDate=startDate, endDate=endDate)

    trip_id = db.execute("""
    SELECt id
    FROM trips
    WHERE user_id = :user_id
    ORDER BY id DESC
    LIMIT 1
    """,
    user_id=session['user_id'])[0]['id']

    insertCountries(countries, trip_id)

    return redirect("/trips")


# MONTH name and year
def getMonthName(date):

    month = {
        'month_name' : calendar.month_name[int(datetime.date.fromisoformat(date).month)],
        'YEAR' : datetime.date.fromisoformat(date).year,
    }

    return month


def changeMonth(date, m):

    if m == 'curr':
        return date

    selectedDate = datetime.date.fromisoformat(date)

    day = 1 if m == "prev" else calendar.monthrange(selectedDate.year, selectedDate.month)[1]
    selectedDate = selectedDate.replace(day=day)

    selectedMonth = selectedDate + datetime.timedelta(days=1 if m == "next" else -1)

    date = selectedMonth.isoformat()

    return date

def getCountries():
    d = requests.get('https://restcountries.eu/rest/v2/all?fields=name;alpha2Code', 'r')
    return d.json()



def insertCountries(countries, trip_id):
    for country_code in countries:
        db.execute("""
        INSERT INTO countries (trip_id, country_code)
        VALUES (:trip_id, :country_code)
        """,
        trip_id=trip_id, country_code=country_code.lower())

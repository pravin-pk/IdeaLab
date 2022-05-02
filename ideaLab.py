from flask import Flask, render_template, request, redirect, url_for, session, make_response
import sqlite3
import pandas as pd
import stripe
from mail import successMail

app = Flask(__name__)

app.secret_key = 'ideaLab'

# stripe.api_key = 'sk_test_51Kt9XkSI3vcYtsdqzfG2gQzHfCNESxyqd7xfuVGHwYpSLK40d4xHyBoI6rJFqWyEwSAiEnUau9QlVJOVqd3JWaET008RbgAAKP'


# app.config["SERVER_NAME"]  = "localhost:8888"
# webbrowser.open('http://127.0.0.1:5000/')

@app.route("/")
def homepage():
    return render_template("frontPage.html")

@app.route("/log", methods = ["POST", "GET"])
def checkOut():
    if request.method != "POST":
        return render_template("checkoutPage.html")

    try:
        conn = sqlite3.connect("idealabLog.sqlite")
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS LOG (NAME TEXT, USN TEXT, PURPOSE TEXT, CHECKIN TIME, CHECKOUT TIME, ENTRYDATE DATE)")

        cur.execute(
            "INSERT INTO LOG VALUES (? ,?, ?, ?, ?, date())",
            (
                request.form["name"],
                request.form["USN"],
                request.form["purpose"],
                request.form["checkin"],
                request.form["checkout"],
                # "%s-%s-%s" % (now.year, now.month, now.day),
            ),
        )

        conn.commit()
        cur.close()
        return "<script> alert('Log data Saved Succesfully'); document.location = '/log'; </script>"

    except sqlite3.Error as e:
        print(e.args)
        cur.close()
        return redirect("/log", 404)
    

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method != "POST":
        return render_template("loginPage.html")

    user = request.form["Username"]
    if user in ["MechHOD", "pk", "yathishSir"]:
        return redirect(url_for("check"))
    else:
        return redirect(url_for("checkOut"))

@app.route("/logs", methods = ['POST', 'GET'])
def check():
    if request.method == "GET":
        try:
            conn = sqlite3.connect("idealabLog.sqlite")
            cur = conn.cursor()

            cur.execute("SELECT * FROM LOG;")
            data = cur.fetchall()
            cur.close()

            # toExcel(data)

            return render_template("checklog.html", content=data)
        except sqlite3.Error as e:
            cur.close()
            print(e)
            return redirect(url_for("login"))

    try:
        conn = sqlite3.connect("idealabLog.sqlite")
        cur = conn.cursor()

        cur.execute("SELECT * FROM LOG WHERE ENTRYDATE BETWEEN ? AND ?", (request.form["start"], request.form["end"]))
        data = cur.fetchall()
        cur.close()

        toExcel(data)

        return render_template("checklog.html", content = data)
    except sqlite3.Error as e:
        cur.close()
        print(e)
        return redirect(url_for("login"))
    

def toExcel(data):
    # print(data)
    try:
        df = pd.DataFrame(data)
        df.columns = ['Name', 'USN', 'Purpose', 'CheckInTime', 'CheckOutTime', 'Date']
        # print(df)
        # df.to_csv('log.csv', index=False)
        df.to_excel('static/log.xlsx', index=False)
    except Exception:
        return


@app.route('/booking', methods= ["POST", "GET"])
def booking():
    if request.method != "POST":
        # return render_template("booking.html")
        try:
            conn = sqlite3.connect("idealabSlot.sqlite")
            cur = conn.cursor()

            cur.execute("CREATE TABLE IF NOT EXISTS BOOK_SLOT (NAME TEXT, USN TEXT, PURPOSE TEXT, START DATETIME, END DATETIME, ENTRYDATE DATETIME)")

            cur.execute("SELECT NAME, PURPOSE, START, END FROM BOOK_SLOT WHERE END > DATETIME('now', 'localtime') ORDER BY END;")
            data = cur.fetchall()
            cur.close()

            return render_template("booking.html", content=data)
        except sqlite3.Error as e:
            cur.close()
            print(e)
            return redirect(url_for("homepage"))

    try:
        if request.form["endDT"] < request.form["startDT"]:
            return "<script> alert('Invalid time'); document.location = '/booking'; </script>"


        conn = sqlite3.connect("idealabSlot.sqlite")
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS BOOK_SLOT (NAME TEXT, USN TEXT, PURPOSE TEXT, START DATETIME, END DATETIME, ENTRYDATE DATETIME)")

        cur.execute("SELECT MAX(END), MAX(START) FROM BOOK_SLOT WHERE PURPOSE = ?", (request.form["purpose"],))
        date = cur.fetchall()

        if date[0][0] is None:
            date = cur.execute("SELECT DATETIME('now', 'localtime');").fetchall()

        startDate = request.form["startDT"].split('T')
        endDate = request.form["endDT"].split('T')
        startDate = f"{startDate[0]} {startDate[1]}"
        endDate = f"{endDate[0]} {endDate[1]}"

        if startDate >= date[0][0]:
            name = request.form["name"]
            usn = request.form["USN"]
            purpose = request.form["purpose"]

            cur.execute(
                "INSERT INTO BOOK_SLOT VALUES (? ,?, ?, ?, ?, datetime('now', 'localtime'))",
                (
                    name,
                    usn,
                    purpose,
                    startDate,
                    endDate,
                    # "%s-%s-%s" % (now.year, now.month, now.day),
                ),
            )

            conn.commit()
            cur.close()
            # return render_template("booking.html", modal = {'text':'Slot booked'}), 201
            # return redirect(url_for("payment", price = request.form.get("price")))

            sendMail = successMail()
            sendMail.addRecipent(request.form["emailId"])
            sendMail.sendMail(name, usn, purpose, startDate, endDate)
            return "<script> alert('Slot booked, Check mail for more details'); document.location = '/booking'; </script>"
        else:
            cur.close()
            return "<script> alert('Selected Time is booked already, Chose some other date and time'); document.location = '/booking'; </script>"

    except sqlite3.Error as e:
        print(e.args)
        cur.close()
        return redirect("/log", 404)
    
@app.route("/showBookings", methods = ['GET', 'POST'])
def showBookings():
    if request.method == "GET":
        try:
            conn = sqlite3.connect("idealabSlot.sqlite")
            cur = conn.cursor()

            cur.execute("SELECT * FROM BOOK_SLOT;")
            data = cur.fetchall()
            cur.close()

            toExcel(data)

            return render_template("showBookings.html", content=data)
        except sqlite3.Error as e:
            cur.close()
            print(e)
            return redirect(url_for("homepage"))

@app.route("/payment", methods = ['GET', 'POST'])
def payment():    
    price = request.args.get("price")
    print(price)
    return render_template("payment.html", content = price)


# ------------TRYING PAYMENT-----------------
# @app.route('/create-checkout-session', methods=['POST', 'GET'])
# def create_checkout_session():
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                     'price': 'price_1KtCZjSI3vcYtsdq9aU1LDde',
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url='/success.html',
#             cancel_url='/cancel.html',
#         )
#     except Exception as e:
#         return str(e)

#     return redirect(checkout_session.url, code=303)






if __name__ == "__main__":
    app.run(debug=True)
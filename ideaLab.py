import webbrowser
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)

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
        return redirect(url_for("check", usr = user))
    else:
        return redirect(url_for("checkOut"))

@app.route("/<usr>", methods = ['POST', 'GET'])
def check(usr):
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

            cur.execute("SELECT NAME, PURPOSE, START, END FROM BOOK_SLOT WHERE START > DATETIME('now', 'localtime') ORDER BY END;")
            data = cur.fetchall()
            cur.close()

            return render_template("booking.html", content=data)
        except sqlite3.Error as e:
            cur.close()
            print(e)
            return redirect(url_for("log"))

    try:
        conn = sqlite3.connect("idealabSlot.sqlite")
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS BOOK_SLOT (NAME TEXT, USN TEXT, PURPOSE TEXT, START DATETIME, END DATETIME, ENTRYDATE DATE)")

        cur.execute("SELECT MAX(END), MAX(START) FROM BOOK_SLOT WHERE PURPOSE = ?", (request.form["purpose"],))
        date = cur.fetchall()

        if date[0][0] is None:
            date = cur.execute("SELECT DATETIME();").fetchall()

        if request.form["startDT"] > date[0][0] or request.form["endDT"] < date[0][1]:

            cur.execute(
                "INSERT INTO BOOK_SLOT VALUES (? ,?, ?, ?, ?, date())",
                (
                    request.form["name"],
                    request.form["USN"],
                    request.form["purpose"],
                    request.form["startDT"],
                    request.form["endDT"],
                    # "%s-%s-%s" % (now.year, now.month, now.day),
                ),
            )

            conn.commit()
            cur.close()
            return "<script> alert('Slot Booked'); document.location = '/booking'; </script>"

        else:
            cur.close()
            return "<script> alert('Selected Time is booked already, Chose some other date and time'); document.location = '/booking'; </script>"

    except sqlite3.Error as e:
        print(e.args)
        cur.close()
        return redirect("/log", 404)
    


if __name__ == "__main__":
    app.run(debug=True)
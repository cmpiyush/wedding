from flask import Flask, render_template, session, request, redirect, url_for, flash
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["wedding_db"]
rsvp_collection = db["rsvp"]
user_collection = db["users"]
ADMIN_USER = os.getenv("ADMIN_DEFAULT_USER")
ADMIN_PASS = os.getenv("ADMIN_DEFAULT_PASS")

# --- Utility: Check if admin exists, else create default one ---
def ensure_admin_exists():
    if not user_collection.find_one({"username": os.getenv("ADMIN_DEFAULT_USER")}):
        user_collection.insert_one({
            "username": os.getenv("ADMIN_DEFAULT_USER"),
            "password": os.getenv("ADMIN_DEFAULT_PASS"),
            "role": "admin"
        })
        print("✅ Default admin created.")

ensure_admin_exists()

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/story")
def story():
    return render_template("story.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/rsvp", methods=["GET", "POST"])
def rsvp():
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        guests = request.form["guests"]
        attending = request.form["attending"]

        entry = {
            "name": name,
            "mobile": mobile,
            "guests": int(guests),
            "attending": attending,
            "timestamp": datetime.datetime.now()
        }

        rsvp_collection.insert_one(entry)
        flash("Thank you for your RSVP, Seema will be happy to see you!", "success")
        return redirect(url_for("rsvp"))

    return render_template("rsvp.html")

# Admin Login
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" in session:
        rsvps = list(rsvp_collection.find())
        return render_template("admin.html", rsvps=rsvps)

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["user"] = username
            return redirect(url_for("admin"))
        else:
            flash("Invalid credentials", "danger")

    return '''
    <div style="margin:50px">
      <h2>Admin Login</h2>
      <form method="POST">
        <label>Username:</label><br>
        <input type="text" name="username" required><br><br>
        <label>Password:</label><br>
        <input type="password" name="password" required><br><br>
        <button type="submit">Login</button>
      </form>
    </div>
    '''
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))


import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from view_users import CANTSEEEMAIL

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

DB_FILE = "users.db"

# ------------------------
# Initialize Database
# ------------------------
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# ------------------------
# Flask-Login Setup
# ------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        if row:
            return User(row[0], row[1], row[2])
    return None

# ------------------------
# Forms
# ------------------------
class SignupForm(FlaskForm):
    username = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    role = SelectField(
        "Role",
        choices=[
            ("Developer", "Developer"),
            ("Researcher", "Researcher"),
            ("Student", "Student")
        ]
    )
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# ------------------------
# Routes
# ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        pwd = form.password.data

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, password FROM users WHERE email=?", (email,))
            user = c.fetchone()

        if user and check_password_hash(user[2], pwd):
            login_user(User(user[0], user[1], email))
            flash(f"Welcome {user[1]}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("index.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = SignupForm()
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data.lower()
        hashed_pw = generate_password_hash(form.password.data)
        role = form.role.data

        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                    (name, email, hashed_pw, role)
                )
                conn.commit()

            flash("Account created! You can now login.", "success")
            return redirect(url_for("index"))

        except sqlite3.IntegrityError:
            flash("Email already registered!", "error")

    return render_template("signup.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))



##admin things to do 
ADMIN_EMAIL = CANTSEEEMAIL
@app.route("/admin/users")
@login_required
def admin_users():

    if current_user.email != ADMIN_EMAIL:
        redirect(url_for('dashboard'))

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, email, role, password FROM users")
        users = c.fetchall()

    output = "<h2>Registered Users</h2><ul>"
    for u in users:
        output += f"<li> id : {u[0]} | name:  {u[1]}| Email: {u[2]} | Role: {u[3]}| Hashpwd: {u[4]}</li>"
    output += "</ul>"
    return output

if __name__ == "__main__":
    app.run(debug=True)
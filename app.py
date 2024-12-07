from flask import Flask, render_template, redirect, url_for, flash, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MySQL
mysql = MySQL(app)

# Initialize Flask extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", [user_id])
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    return None


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class OrderForm(FlaskForm):
    juice = SelectField('Choose Your Juice', choices=[], validators=[DataRequired()])
    fruits = SelectMultipleField('Select Fruits', choices=[], validators=[Optional()])
    toppings = SelectMultipleField('Select Toppings', choices=[('none', 'No Toppings')], validators=[Optional()])
    cup_size = RadioField('Cup Size', choices=[('regular', 'Regular'), ('large', 'Large')], validators=[DataRequired()])
    submit = SubmitField('Place Order')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (form.username.data, form.email.data, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", [form.email.data])
        user = cur.fetchone()
        cur.close()
        if user and bcrypt.check_password_hash(user[3], form.password.data):
            user_obj = User(id=user[0], username=user[1], email=user[2])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Login failed. Check your email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC", [current_user.id])
    orders = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', user=current_user, orders=orders)


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()

    # Dynamically populate form choices
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM juices")
    form.juice.choices = [(str(row[0]), row[1]) for row in cur.fetchall()]
    cur.execute("SELECT id, name FROM fruits")
    form.fruits.choices = [(str(row[0]), row[1]) for row in cur.fetchall()]
    cur.execute("SELECT id, name FROM toppings")
    form.toppings.choices += [(str(row[0]), row[1]) for row in cur.fetchall()]
    cur.close()

    if form.validate_on_submit():
        selected_juice = form.juice.data
        selected_fruits = ', '.join(form.fruits.data) if form.fruits.data else 'None'
        selected_toppings = ', '.join(form.toppings.data) if form.toppings.data else 'None'
        cup_size = form.cup_size.data

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO orders (user_id, juice_name, cup_size, fruits, toppings)
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user.id, selected_juice, cup_size, selected_fruits, selected_toppings))
        mysql.connection.commit()
        cur.close()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('order.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


# Database initialization
def initialize_database():
    with app.app_context():
        cur = mysql.connection.cursor()
        try:
            cur.execute("SHOW TABLES;")
            tables = cur.fetchall()
            if not tables:
                with open('db.sql', 'r') as f:
                    sql = f.read()
                for statement in sql.split(';'):
                    if statement.strip():
                        cur.execute(statement)
                mysql.connection.commit()
        finally:
            cur.close()


if __name__ == '__main__':
    initialize_database()  # Initialize database on first run
    app.run(debug=True)

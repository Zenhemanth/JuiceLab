from flask import Flask, render_template, redirect, url_for, flash, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import SelectField, SelectMultipleField, RadioField
from wtforms.validators import Optional
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import asyncio
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://user:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional but recommended to disable event notifications
app.config['SQLALCHEMY_POOL_SIZE'] = 10  # Number of connections in the pool
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5  # Extra connections beyond the pool size

# Initialize SQLAlchemy
db = SQLAlchemy(app)

mysql = MySQL(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'



class User(UserMixin):
    def __init__(self, id, username, email, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", [user_id])
    user = cur.fetchone()
    if user:
        return User(id=user[0], username=user[1], email=user[2], is_admin=user[4])
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
        if user and bcrypt.check_password_hash(user[3], form.password.data):
            user_obj = User(id=user[0], username=user[1], email=user[2])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('order'))
        flash('Login failed. Check your email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()

    # Populate form choices dynamically
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name FROM juices")
    form.juice.choices = [(str(row[0]), row[1]) for row in cur.fetchall()]
    cur.execute("SELECT id, name FROM fruits")
    form.fruits.choices = [(str(row[0]), row[1]) for row in cur.fetchall()]
    cur.execute("SELECT id, name FROM toppings")
    form.toppings.choices = [('none', 'No Toppings')] + [(str(row[0]), row[1]) for row in cur.fetchall()]
    cur.close()

    if form.validate_on_submit():
        # Fetch selected items
        selected_juice = form.juice.data
        selected_fruits = form.fruits.data if form.fruits.data else []
        selected_toppings = form.toppings.data if form.toppings.data else []
        cup_size = form.cup_size.data

        # Calculate nutritional facts
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT base_calories, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein
            FROM juices WHERE id = %s
        """, [selected_juice])
        juice_data = cur.fetchone()

        # Initialize totals
        total_calories = juice_data[0]
        total_fat = juice_data[1]
        total_cholesterol = juice_data[2]
        total_sodium = juice_data[3]
        total_carbohydrates = juice_data[4]
        total_fiber = juice_data[5]
        total_sugars = juice_data[6]
        total_protein = juice_data[7]

        nutritional_facts = {'Juice': juice_data[0]}

        # Add nutritional values from fruits
        for fruit in selected_fruits:
            cur.execute("""
                SELECT name, calories_per_gram, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein
                FROM fruits WHERE id = %s
            """, [fruit])
            name, calories_per_gram, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein = cur.fetchone()
            total_calories += calories_per_gram * 100  # Assuming 100g per fruit
            total_fat += fat
            total_cholesterol += cholesterol
            total_sodium += sodium
            total_carbohydrates += carbohydrates
            total_fiber += fiber
            total_sugars += sugars
            total_protein += protein
            nutritional_facts[name] = calories_per_gram * 100

        # Add nutritional values from toppings
        for topping in selected_toppings:
            if topping != 'none':
                cur.execute("""
                    SELECT name, calories_per_gram, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein
                    FROM toppings WHERE id = %s
                """, [topping])
                name, calories_per_gram, fat, cholesterol, sodium, carbohydrates, fiber, sugars, protein = cur.fetchone()
                total_calories += calories_per_gram * 10  # Assuming 10g per topping
                total_fat = round(total_fat, 1)
                total_cholesterol = round(total_cholesterol, 1)
                total_sodium = round(total_sodium, 1)
                total_carbohydrates = round(total_carbohydrates, 1)
                total_fiber = round(total_fiber, 1)
                total_sugars = round(total_sugars, 1)
                total_protein = round(total_protein, 1)
                nutritional_facts[name] = calories_per_gram * 10

        # Save order to database
        selected_fruits_str = ', '.join(selected_fruits) if selected_fruits else 'None'
        selected_toppings_str = ', '.join(selected_toppings) if selected_toppings else 'No Toppings'

        cur.execute("""
            INSERT INTO orders (user_id, juice_name, cup_size, fruits, toppings, total_calories)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (current_user.id, selected_juice, cup_size, selected_fruits_str, selected_toppings_str, total_calories))
        mysql.connection.commit()
        cur.close()

        flash('Thank you, your order has been placed successfully!')

        # Redirect to Nutrition Facts page
        return render_template(
            'nutrition_facts.html',
            nutritional_facts=nutritional_facts,
            total_calories=total_calories,
            total_fat=total_fat,
            total_cholesterol=total_cholesterol,
            total_sodium=total_sodium,
            total_carbohydrates=total_carbohydrates,
            total_fiber=total_fiber,
            total_sugars=total_sugars,
            total_protein=total_protein
        )

    return render_template('order.html', form=form)

@app.route('/process')
async def process_order():
    await asyncio.sleep(5)  # Simulate a long-running operation
    return "Order processed asynchronously!"

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Debugging
    print("Dashboard route accessed.")

    # Fetch user details
    user = current_user
    print("User details:", user)

    # Fetch order history
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC", [user.id])
    orders = cur.fetchall()
    cur.close()
    print("Orders fetched:", orders)

    return render_template('dashboard.html', user=user, orders=orders)

@app.route('/update_username', methods=['GET', 'POST'])
@login_required
def update_username():
    if request.method == 'POST':
        new_username = request.form['username']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Username updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('update_username.html')

from werkzeug.security import generate_password_hash

@app.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Password updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('update_password.html')

@app.route('/update_email', methods=['GET', 'POST'])
@login_required
def update_email():
    if request.method == 'POST':
        new_email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, current_user.id))
        mysql.connection.commit()
        cur.close()
        flash('Email updated successfully!')
        return redirect(url_for('dashboard'))
    return render_template('update_email.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Unauthorized access", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close()

    print("Orders fetched for admin:", orders)  # Debugging
    return render_template('admin_dashboard.html', orders=orders)

@app.route('/delete_order/<int:order_id>', methods=['POST', 'GET'])
@login_required
def delete_order(order_id):
    if not current_user.is_admin:
        flash("Unauthorized access", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM orders WHERE id = %s", [order_id])
        mysql.connection.commit()
        cur.close()
        flash("Order deleted successfully.", "success")
    except Exception as e:
        flash("An error occurred while deleting the order.", "danger")
        print(f"Error: {e}")

    return redirect(url_for('admin_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)

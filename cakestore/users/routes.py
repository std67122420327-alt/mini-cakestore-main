from flask import Blueprint, render_template, request, redirect, url_for, flash
from cakestore.models import User
from cakestore.extensions import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user

user_bp = Blueprint('users', __name__, template_folder='templates')

@user_bp.route('/')
def index():
    return render_template('users/index.html' , title= 'Users Page')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        query = db.select(User).where(User.username == username)
        user = db.session.scalar(query)
        if user :
            flash('Username already exists.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
            return redirect(url_for('users.register'))
        else:
            query = db.select(User).where(User.email == email)
            user = db.session.scalar(query)
            if user:
                flash('Email already exists.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
                return redirect(url_for('users.register'))
            else:
                if password == confirm_password:
                    pwd_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                    user = User(username=username, email=email, password=pwd_hash)
                    db.session.add(user)
                    db.session.commit()
                    flash('Registration successful!', 'info') # เปลี่ยนเป็นสีฟ้า (info)
                    return redirect(url_for('users.login'))
                else:
                    flash('Passwords do not match.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
                    return redirect(url_for('users.register'))
        
    return render_template('users/register.html' , title= 'Register Page')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        query = db.select(User).where(User.username == username)
        user = db.session.scalar(query)
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!', 'info') # เปลี่ยนเป็นสีฟ้า (info)
                return redirect(url_for('core.index'))
            else:
                flash('Incorrect password.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
                return redirect(url_for('users.login'))
        else:
            flash(f'Username: {username} does not exist.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
            return redirect(url_for('users.login'))
        

    return render_template('users/login.html' , title= 'Login Page')

@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')

        if len(firstname)>0 or len(lastname)>0:
            user.firstname = firstname
            user.lastname = lastname

            db.session.add(user)
            db.session.commit()
            flash('Profile updated successfully!', 'info') # เปลี่ยนเป็นสีฟ้า (info)
            return redirect(url_for('users.profile'))

    return render_template('users/profile.html', title='Profile Page', user=user)

@user_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not bcrypt.check_password_hash(current_user.password, old_password):
            flash('Old password is incorrect.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
            return redirect(url_for('users.change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'info') # เปลี่ยนเป็นสีฟ้า (info)
            return redirect(url_for('users.change_password'))

        hashed_new_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        current_user.password = hashed_new_password
        db.session.commit()
        flash('Password changed successfully!', 'info') # เปลี่ยนเป็นสีฟ้า (info)
        return redirect(url_for('users.profile'))
    return render_template('users/change_password.html', title='Change Password')

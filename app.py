from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import random
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Configuration - support both local and Render deployment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'media'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Static files configuration for production (whitenoise)
app.config['STATIC_FOLDER'] = 'static'
app.config['STATIC_URL_PATH'] = '/static'

# Enable whitenoise for static file serving on production
if os.getenv('RENDER'):
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static')

db = SQLAlchemy(app)

# Models
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(120))
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='CLIENT')  # ADMIN, HR, CLIENT
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class OTPCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    @staticmethod
    def create_for_user(user):
        code = ''.join(random.choices(string.digits, k=6))
        expires = datetime.utcnow() + timedelta(minutes=5)
        otp = OTPCode(user_id=user.id, code=code, expires_at=expires)
        db.session.add(otp)
        db.session.commit()
        return otp

    def is_valid(self, entered_code):
        return not self.is_used and self.expires_at > datetime.utcnow() and self.code == entered_code

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    min_experience = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    assigned_hr_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resume_path = db.Column(db.String(200))
    ai_score = db.Column(db.Float, default=0.0)
    matched_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    status = db.Column(db.String(20), default='APPLIED')
    selection_stage = db.Column(db.String(20), default='NONE')
    is_selected = db.Column(db.Boolean, default=False)
    offer_sent = db.Column(db.Boolean, default=False)
    custom_offer_letter_path = db.Column(db.String(200))
    feedback = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    meeting_link = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Forms
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('CLIENT', 'Client'), ('HR', 'HR'), ('ADMIN', 'Admin')], validators=[DataRequired()])
    organization_name = StringField('Organization Name (for HR)')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')

class SecretCodeForm(FlaskForm):
    secret_code = StringField('Secret Code', validators=[DataRequired()])
    submit = SubmitField('Verify')

# Routes
@app.route('/')
def home():
    jobs = Job.query.filter_by(is_active=True).join(Organization).filter(Organization.is_blocked == False).all()
    q = request.args.get('q', '')
    if q:
        jobs = [job for job in jobs if q.lower() in job.title.lower() or q.lower() in job.description.lower()]
    user = User.query.get(session.get('user_id')) if session.get('user_id') else None
    return render_template('home.html', jobs=jobs, user=user, q=q)

@app.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', 'CLIENT')
    if role.upper() in ['ADMIN', 'HR']:
        if not session.get('secret_verified'):
            return redirect(url_for('verify_secret', next=request.url))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data.upper())
        user.set_password(form.password.data)
        if form.role.data == 'HR' and form.organization_name.data:
            org = Organization.query.filter_by(name=form.organization_name.data).first()
            if not org:
                org = Organization(name=form.organization_name.data)
                db.session.add(org)
            user.organization = org
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('registration/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'CLIENT')
    if role.upper() in ['ADMIN', 'HR']:
        if not session.get('secret_verified'):
            return redirect(url_for('verify_secret', next=request.url))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            otp = OTPCode.create_for_user(user)
            session['otp_user_id'] = user.id
            # Send email (simplified)
            flash('OTP sent to your email.', 'info')
            return redirect(url_for('verify_otp'))
        flash('Invalid credentials.', 'error')
    return render_template('registration/login.html', form=form)

@app.route('/verify-secret', methods=['GET', 'POST'])
def verify_secret():
    form = SecretCodeForm()
    if form.validate_on_submit():
        secret_code = os.getenv('ADMIN_HR_SECRET_CODE', 'default_secret')
        if form.secret_code.data == secret_code:
            session['secret_verified'] = True
            next_url = request.args.get('next', url_for('home'))
            return redirect(next_url)
        flash('Invalid secret code.', 'error')
    return render_template('verify_secret.html', form=form)

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    user_id = session.get('otp_user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    form = OTPForm()
    if form.validate_on_submit():
        otp = OTPCode.query.filter_by(user_id=user.id, is_used=False).order_by(OTPCode.created_at.desc()).first()
        if otp and otp.is_valid(form.otp.data):
            otp.is_used = True
            db.session.commit()
            session['user_id'] = user.id
            session.pop('otp_user_id', None)
            return redirect(url_for('dashboard'))
        flash('Invalid or expired OTP.', 'error')
    return render_template('registration/verify_otp.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('otp_user_id', None)
    session.pop('secret_verified', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
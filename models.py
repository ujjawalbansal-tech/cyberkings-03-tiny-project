from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    phone          = db.Column(db.String(15))
    password       = db.Column(db.String(256), nullable=False)
    role           = db.Column(db.String(10), nullable=False)   # 'customer' / 'worker'
    city           = db.Column(db.String(100))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    profile_photo  = db.Column(db.String(255))   # filename stored in /static/uploads/

    # Worker-only
    skill          = db.Column(db.String(100))
    experience     = db.Column(db.Integer)
    is_available   = db.Column(db.Boolean, default=True)
    avg_rating     = db.Column(db.Float, default=0.0)
    total_reviews  = db.Column(db.Integer, default=0)
    total_earned   = db.Column(db.Float, default=0.0)   # total money received

    # Theme / settings
    dark_mode      = db.Column(db.Boolean, default=False)
    theme_color    = db.Column(db.String(20), default='teal')   # teal / blue / purple / amber

    # Relationships
    jobs_posted    = db.relationship('Job', backref='customer', lazy=True,
                                     foreign_keys='Job.customer_id')
    applications   = db.relationship('Application', backref='worker', lazy=True,
                                     foreign_keys='Application.worker_id')
    reviews_given  = db.relationship('Review', backref='reviewer', lazy=True,
                                     foreign_keys='Review.reviewer_id')

    def set_password(self, p): self.password = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password, p)

    def get_initials(self):
        parts = self.name.strip().split()
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


class Job(db.Model):
    __tablename__ = 'jobs'
    id                 = db.Column(db.Integer, primary_key=True)
    title              = db.Column(db.String(200), nullable=False)
    description        = db.Column(db.Text)
    skill              = db.Column(db.String(100), nullable=False)
    location           = db.Column(db.String(100), nullable=False)
    budget             = db.Column(db.String(50))           # per day budget
    date_from          = db.Column(db.String(50))
    date_to            = db.Column(db.String(50))
    status             = db.Column(db.String(20), default='open')
    # open / assigned / completed / cancelled / pending_cancel
    customer_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_worker_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at        = db.Column(db.DateTime)    # when worker accepted / job assigned
    payment_amount     = db.Column(db.Float)
    payment_accepted   = db.Column(db.Boolean, default=False)
    payment_sent       = db.Column(db.Boolean, default=False)
    is_direct_request  = db.Column(db.Boolean, default=False)

    applications       = db.relationship('Application', backref='job', lazy=True)
    assigned_worker    = db.relationship('User', foreign_keys=[assigned_worker_id])
    cancel_requests    = db.relationship('CancelRequest', backref='job', lazy=True)


class Application(db.Model):
    __tablename__ = 'applications'
    id         = db.Column(db.Integer, primary_key=True)
    job_id     = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    worker_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.Text)
    status     = db.Column(db.String(20), default='pending')
    # pending / accepted / rejected / worker_accepted (for direct requests)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    id          = db.Column(db.Integer, primary_key=True)
    job_id      = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    worker_id   = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating      = db.Column(db.Integer)
    comment     = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class CancelRequest(db.Model):
    """Worker or customer initiated cancellation."""
    __tablename__ = 'cancel_requests'
    id          = db.Column(db.Integer, primary_key=True)
    job_id      = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    initiated_by= db.Column(db.String(10))   # 'customer' / 'worker'
    reason      = db.Column(db.Text)
    status      = db.Column(db.String(20), default='pending')  # pending / accepted / rejected
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

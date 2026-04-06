from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Job, Application, Review
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to continue.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Auth Routes ────────────────────────────────────────────
@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'customer')
        city     = request.form.get('city', '').strip()
        skill    = request.form.get('skill', '').strip()
        exp      = request.form.get('experience', 0)

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('signup.html')

        user = User(name=name, email=email, phone=phone,
                    role=role, city=city, skill=skill,
                    experience=int(exp) if exp else 0)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {name}!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'customer':
        jobs  = Job.query.filter_by(customer_id=current_user.id).order_by(Job.created_at.desc()).limit(5).all()
        total_apps = sum(len(j.applications) for j in Job.query.filter_by(customer_id=current_user.id).all())
        return render_template('customer/dashboard.html', jobs=jobs, total_apps=total_apps)
    else:
        nearby = Job.query.filter_by(status='open').order_by(Job.created_at.desc()).limit(5).all()
        my_apps = Application.query.filter_by(worker_id=current_user.id).all()
        return render_template('worker/dashboard.html', nearby_jobs=nearby, my_apps=my_apps)


# ─── Customer Routes ────────────────────────────────────────
@app.route('/find-workers')
@login_required
def find_workers():
    skill    = request.args.get('skill', '')
    location = request.args.get('location', '')
    query = User.query.filter_by(role='worker', is_available=True)
    if skill:
        query = query.filter(User.skill.ilike(f'%{skill}%'))
    if location:
        query = query.filter(User.city.ilike(f'%{location}%'))
    workers = query.all()
    return render_template('customer/find_workers.html', workers=workers,
                           skill=skill, location=location)


@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'customer':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        job = Job(
            title       = request.form.get('title'),
            description = request.form.get('description'),
            skill       = request.form.get('skill'),
            location    = request.form.get('location'),
            budget      = request.form.get('budget'),
            date_needed = request.form.get('date_needed'),
            customer_id = current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('my_jobs'))
    return render_template('customer/post_job.html')


@app.route('/my-jobs')
@login_required
def my_jobs():
    jobs = Job.query.filter_by(customer_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('customer/my_jobs.html', jobs=jobs)


@app.route('/job/<int:job_id>/applications')
@login_required
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    if job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_jobs'))
    return render_template('customer/applications.html', job=job)


@app.route('/accept-application/<int:app_id>')
@login_required
def accept_application(app_id):
    application = Application.query.get_or_404(app_id)
    job = application.job
    if job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('dashboard'))
    application.status = 'accepted'
    job.status = 'assigned'
    job.assigned_worker_id = application.worker_id
    Application.query.filter(
        Application.job_id == job.id,
        Application.id != app_id
    ).update({'status': 'rejected'})
    db.session.commit()
    flash('Worker hired successfully!', 'success')
    return redirect(url_for('job_applications', job_id=job.id))


@app.route('/complete-job/<int:job_id>')
@login_required
def complete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('dashboard'))
    job.status = 'completed'
    db.session.commit()
    flash('Job marked as completed!', 'success')
    return redirect(url_for('my_jobs'))


@app.route('/send-request/<int:worker_id>', methods=['POST'])
@login_required
def send_direct_request(worker_id):
    title   = request.form.get('title', 'Direct Job Request')
    desc    = request.form.get('description', '')
    skill   = request.form.get('skill', '')
    job = Job(title=title, description=desc, skill=skill,
              location=current_user.city or '',
              customer_id=current_user.id, status='open')
    db.session.add(job)
    db.session.flush()
    app_obj = Application(job_id=job.id, worker_id=worker_id,
                          message='Direct request from customer')
    db.session.add(app_obj)
    db.session.commit()
    flash('Request sent!', 'success')
    return redirect(url_for('find_workers'))


# ─── Worker Routes ───────────────────────────────────────────
@app.route('/browse-jobs')
@login_required
def browse_jobs():
    if current_user.role != 'worker':
        return redirect(url_for('dashboard'))
    skill    = request.args.get('skill', '')
    location = request.args.get('location', '')
    query = Job.query.filter_by(status='open')
    if skill:
        query = query.filter(Job.skill.ilike(f'%{skill}%'))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    jobs = query.order_by(Job.created_at.desc()).all()
    applied_ids = [a.job_id for a in Application.query.filter_by(worker_id=current_user.id).all()]
    return render_template('worker/browse_jobs.html', jobs=jobs, applied_ids=applied_ids,
                           skill=skill, location=location)


@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'worker':
        return redirect(url_for('dashboard'))
    existing = Application.query.filter_by(job_id=job_id, worker_id=current_user.id).first()
    if existing:
        flash('Already applied.', 'info')
        return redirect(url_for('browse_jobs'))
    message = request.form.get('message', '')
    application = Application(job_id=job_id, worker_id=current_user.id, message=message)
    db.session.add(application)
    db.session.commit()
    flash('Application submitted!', 'success')
    return redirect(url_for('my_applications'))


@app.route('/my-applications')
@login_required
def my_applications():
    apps = Application.query.filter_by(worker_id=current_user.id).order_by(Application.created_at.desc()).all()
    return render_template('worker/applications.html', applications=apps)


@app.route('/worker-profile', methods=['GET', 'POST'])
@login_required
def worker_profile():
    if current_user.role != 'worker':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        current_user.name        = request.form.get('name', current_user.name)
        current_user.phone       = request.form.get('phone', current_user.phone)
        current_user.city        = request.form.get('city', current_user.city)
        current_user.skill       = request.form.get('skill', current_user.skill)
        current_user.experience  = int(request.form.get('experience', current_user.experience or 0))
        current_user.is_available = 'is_available' in request.form
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('worker_profile'))
    completed = Application.query.filter_by(worker_id=current_user.id, status='accepted').count()
    return render_template('worker/profile.html', completed=completed)


# ─── Review Route ────────────────────────────────────────────
@app.route('/review/<int:job_id>', methods=['POST'])
@login_required
def submit_review(job_id):
    job    = Job.query.get_or_404(job_id)
    rating = int(request.form.get('rating', 5))
    comment= request.form.get('comment', '')
    review = Review(job_id=job_id, worker_id=job.assigned_worker_id,
                    reviewer_id=current_user.id, rating=rating, comment=comment)
    db.session.add(review)
    worker = User.query.get(job.assigned_worker_id)
    if worker:
        total = worker.total_reviews + 1
        worker.avg_rating   = ((worker.avg_rating * worker.total_reviews) + rating) / total
        worker.total_reviews = total
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(url_for('my_jobs'))


# ─── Init DB ─────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
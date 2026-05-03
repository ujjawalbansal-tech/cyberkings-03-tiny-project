import os, uuid
from datetime import datetime, timedelta
from flask import (Flask, render_template, redirect, url_for, request,
                   flash, jsonify, send_from_directory)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Job, Application, Review, CancelRequest

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to continue.'


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'])


def save_photo(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Uploads ────────────────────────────────────────────────
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


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


# ─── Dashboard ──────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'customer':
        jobs       = Job.query.filter_by(customer_id=current_user.id).order_by(Job.created_at.desc()).limit(5).all()
        total_apps = sum(len(j.applications) for j in Job.query.filter_by(customer_id=current_user.id).all())
        return render_template('customer/dashboard.html', jobs=jobs, total_apps=total_apps)
    else:
        nearby  = Job.query.filter_by(status='open').order_by(Job.created_at.desc()).limit(5).all()
        my_apps = Application.query.filter_by(worker_id=current_user.id).all()
        # Direct requests waiting for worker acceptance
        direct_requests = Application.query.join(Job).filter(
            Application.worker_id == current_user.id,
            Application.status == 'pending',
            Job.is_direct_request == True
        ).all()
        return render_template('worker/dashboard.html',
                               nearby_jobs=nearby,
                               my_apps=my_apps,
                               direct_requests=direct_requests)


# ─── Settings ───────────────────────────────────────────────
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            if not current_user.check_password(old_pw):
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters.', 'error')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Password changed successfully!', 'success')

        elif action == 'theme':
            current_user.dark_mode   = 'dark_mode' in request.form
            current_user.theme_color = request.form.get('theme_color', 'teal')
            db.session.commit()
            flash('Theme updated!', 'success')

    return render_template('settings.html')


# ─── Profile (shared) ───────────────────────────────────────
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name  = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        current_user.city  = request.form.get('city', current_user.city).strip()

        if current_user.role == 'worker':
            current_user.skill       = request.form.get('skill', current_user.skill)
            current_user.experience  = int(request.form.get('experience', current_user.experience or 0))
            current_user.is_available = 'is_available' in request.form

        # Photo upload
        photo = request.files.get('profile_photo')
        saved = save_photo(photo)
        if saved:
            current_user.profile_photo = saved

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))

    if current_user.role == 'customer':
        all_jobs   = Job.query.filter_by(customer_id=current_user.id).all()
        stats = {
            'total':     len(all_jobs),
            'open':      sum(1 for j in all_jobs if j.status == 'open'),
            'assigned':  sum(1 for j in all_jobs if j.status == 'assigned'),
            'completed': sum(1 for j in all_jobs if j.status == 'completed'),
        }
        reviews_given = Review.query.filter_by(reviewer_id=current_user.id).all()
        return render_template('customer/profile.html',
                               all_jobs=all_jobs, stats=stats,
                               reviews_given=reviews_given)
    else:
        completed = Application.query.filter_by(worker_id=current_user.id, status='accepted').count()
        all_apps  = Application.query.filter_by(worker_id=current_user.id).all()
        stats = {
            'applied':   len(all_apps),
            'accepted':  sum(1 for a in all_apps if a.status == 'accepted'),
            'pending':   sum(1 for a in all_apps if a.status == 'pending'),
            'completed': Job.query.filter_by(assigned_worker_id=current_user.id, status='completed').count(),
        }
        return render_template('worker/profile.html',
                               completed=completed, stats=stats)


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
            date_from   = request.form.get('date_from'),
            date_to     = request.form.get('date_to'),
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
    now  = datetime.utcnow()
    return render_template('customer/my_jobs.html', jobs=jobs, now=now)


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
    application.status         = 'accepted'
    job.status                 = 'assigned'
    job.assigned_worker_id     = application.worker_id
    job.accepted_at            = datetime.utcnow()
    # Make worker unavailable from date_from
    worker = User.query.get(application.worker_id)
    if worker:
        worker.is_available = False
    Application.query.filter(
        Application.job_id == job.id,
        Application.id != app_id
    ).update({'status': 'rejected'})
    db.session.commit()
    flash('Worker hired successfully!', 'success')
    return redirect(url_for('job_applications', job_id=job.id))


@app.route('/complete-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def complete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        amount = request.form.get('payment_amount', '')
        try:
            job.payment_amount = float(amount)
        except (ValueError, TypeError):
            flash('Please enter a valid payment amount.', 'error')
            return render_template('customer/complete_job.html', job=job)
        job.status       = 'completed'
        job.payment_sent = True
        db.session.commit()
        flash('Job marked as completed! Payment request sent to worker.', 'success')
        return redirect(url_for('my_jobs'))
    return render_template('customer/complete_job.html', job=job)


@app.route('/send-request/<int:worker_id>', methods=['POST'])
@login_required
def send_direct_request(worker_id):
    title     = request.form.get('title', 'Direct Job Request').strip()
    desc      = request.form.get('description', '').strip()
    skill     = request.form.get('skill', '').strip()
    budget    = request.form.get('budget', '').strip()
    date_from = request.form.get('date_from', '').strip()
    date_to   = request.form.get('date_to', '').strip()

    job = Job(title=title, description=desc, skill=skill,
              location=current_user.city or '',
              budget=budget,
              date_from=date_from,
              date_to=date_to,
              customer_id=current_user.id,
              status='open',
              is_direct_request=True)
    db.session.add(job)
    db.session.flush()
    app_obj = Application(job_id=job.id, worker_id=worker_id,
                          message='Direct request from customer',
                          status='pending')
    db.session.add(app_obj)
    db.session.commit()
    flash('Request sent to worker! Waiting for their acceptance.', 'success')
    return redirect(url_for('find_workers'))


# ─── Remove Job (5-day rule) ─────────────────────────────────
@app.route('/remove-job/<int:job_id>', methods=['POST'])
@login_required
def remove_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_jobs'))

    now = datetime.utcnow()

    # Can remove freely if not yet assigned
    if job.status == 'open':
        db.session.delete(job)
        db.session.commit()
        flash('Job removed.', 'success')
        return redirect(url_for('my_jobs'))

    if job.status == 'assigned' and job.accepted_at:
        days_since = (now - job.accepted_at).days
        if days_since <= 5:
            db.session.delete(job)
            # Re-enable worker
            if job.assigned_worker_id:
                w = User.query.get(job.assigned_worker_id)
                if w:
                    w.is_available = True
            db.session.commit()
            flash('Job removed within 5-day window.', 'success')
        else:
            # Must request via cancel request
            flash('5-day removal window has passed. Please use "Request Cancellation" instead.', 'error')
    else:
        flash('This job cannot be removed at this stage.', 'error')
    return redirect(url_for('my_jobs'))


# ─── Cancellation Requests ───────────────────────────────────
@app.route('/request-cancel/<int:job_id>', methods=['POST'])
@login_required
def request_cancel(job_id):
    job    = Job.query.get_or_404(job_id)
    reason = request.form.get('reason', '').strip()
    initiated_by = 'customer' if current_user.role == 'customer' else 'worker'

    if initiated_by == 'customer' and job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_jobs'))
    if initiated_by == 'worker' and job.assigned_worker_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_applications'))

    cr = CancelRequest(job_id=job_id, initiated_by=initiated_by, reason=reason)
    db.session.add(cr)
    job.status = 'pending_cancel'
    db.session.commit()
    flash('Cancellation request sent.', 'success')
    if initiated_by == 'customer':
        return redirect(url_for('my_jobs'))
    return redirect(url_for('my_applications'))


@app.route('/respond-cancel/<int:cr_id>/<action>')
@login_required
def respond_cancel(cr_id, action):
    cr  = CancelRequest.query.get_or_404(cr_id)
    job = cr.job

    # The OTHER party responds
    if cr.initiated_by == 'worker' and job.customer_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_jobs'))
    if cr.initiated_by == 'customer' and job.assigned_worker_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_applications'))

    if action == 'accept':
        cr.status  = 'accepted'
        job.status = 'cancelled'
        # Re-enable worker
        if job.assigned_worker_id:
            w = User.query.get(job.assigned_worker_id)
            if w:
                w.is_available = True
        db.session.commit()
        flash('Job cancelled successfully.', 'success')
    else:
        cr.status  = 'rejected'
        job.status = 'assigned'
        db.session.commit()
        flash('Cancellation request rejected. Job continues.', 'info')

    if current_user.role == 'customer':
        return redirect(url_for('my_jobs'))
    return redirect(url_for('my_applications'))


# ─── Worker Routes ───────────────────────────────────────────
@app.route('/browse-jobs')
@login_required
def browse_jobs():
    if current_user.role != 'worker':
        return redirect(url_for('dashboard'))
    skill    = request.args.get('skill', '')
    location = request.args.get('location', '')
    query = Job.query.filter_by(status='open', is_direct_request=False)
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
    message     = request.form.get('message', '')
    application = Application(job_id=job_id, worker_id=current_user.id, message=message)
    db.session.add(application)
    db.session.commit()
    flash('Application submitted!', 'success')
    return redirect(url_for('my_applications'))


@app.route('/my-applications')
@login_required
def my_applications():
    apps  = Application.query.filter_by(worker_id=current_user.id).order_by(Application.created_at.desc()).all()
    # Cancel requests where worker needs to respond (customer initiated)
    cancel_reqs = CancelRequest.query.join(Job).filter(
        Job.assigned_worker_id == current_user.id,
        CancelRequest.initiated_by == 'customer',
        CancelRequest.status == 'pending'
    ).all()
    return render_template('worker/applications.html',
                           applications=apps, cancel_reqs=cancel_reqs)


# ─── Worker: Direct Requests inbox ───────────────────────────
@app.route('/my-requests')
@login_required
def my_requests():
    if current_user.role != 'worker':
        return redirect(url_for('dashboard'))
    # Direct job requests sent specifically to this worker
    requests_list = Application.query.join(Job).filter(
        Application.worker_id == current_user.id,
        Job.is_direct_request == True
    ).order_by(Application.created_at.desc()).all()
    return render_template('worker/requests.html', requests_list=requests_list)


@app.route('/accept-request/<int:app_id>')
@login_required
def accept_direct_request(app_id):
    application = Application.query.get_or_404(app_id)
    if application.worker_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_requests'))
    application.status              = 'worker_accepted'
    application.job.status          = 'assigned'
    application.job.assigned_worker_id = current_user.id
    application.job.accepted_at     = datetime.utcnow()
    current_user.is_available        = False
    db.session.commit()
    flash('Request accepted! Customer has been notified.', 'success')
    return redirect(url_for('my_requests'))


@app.route('/reject-request/<int:app_id>')
@login_required
def reject_direct_request(app_id):
    application = Application.query.get_or_404(app_id)
    if application.worker_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_requests'))
    application.status     = 'rejected'
    application.job.status = 'open'
    db.session.commit()
    flash('Request declined.', 'info')
    return redirect(url_for('my_requests'))


# ─── Worker: Profile ─────────────────────────────────────────
@app.route('/worker-profile', methods=['GET', 'POST'])
@login_required
def worker_profile():
    return redirect(url_for('worker/profile'))


# ─── Payment accept (worker) ─────────────────────────────────
@app.route('/accept-payment/<int:job_id>')
@login_required
def accept_payment(job_id):
    job = Job.query.get_or_404(job_id)
    if job.assigned_worker_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('my_applications'))
    job.payment_accepted = True
    # Add to worker total earned
    if job.payment_amount:
        current_user.total_earned += job.payment_amount
    # Re-enable worker availability
    current_user.is_available = True
    db.session.commit()
    flash(f'Payment of ₹{job.payment_amount:.0f} accepted!', 'success')
    return redirect(url_for('my_applications'))


# ─── Review ───────────────────────────────────────────────────
@app.route('/review/<int:job_id>', methods=['POST'])
@login_required
def submit_review(job_id):
    job = Job.query.get_or_404(job_id)
    # Check not already reviewed
    existing = Review.query.filter_by(job_id=job_id, reviewer_id=current_user.id).first()
    if existing:
        flash('You have already reviewed this job.', 'info')
        return redirect(url_for('my_jobs'))
    rating  = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
    review  = Review(job_id=job_id, worker_id=job.assigned_worker_id,
                     reviewer_id=current_user.id, rating=rating, comment=comment)
    db.session.add(review)
    worker = User.query.get(job.assigned_worker_id)
    if worker:
        total            = worker.total_reviews + 1
        worker.avg_rating     = ((worker.avg_rating * worker.total_reviews) + rating) / total
        worker.total_reviews  = total
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(url_for('my_jobs'))


# ─── Init DB ──────────────────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

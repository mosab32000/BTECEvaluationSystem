from flask import render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Role
from app.utils import send_password_reset_email, log_activity, create_notification
from werkzeug.urls import url_parse

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('تم تعليق حسابك. يرجى التواصل مع مدير النظام.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        log_activity(user, 'تسجيل الدخول', ip_address=request.remote_addr)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash('تم تسجيل الدخول بنجاح!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='تسجيل الدخول', form=form)

@auth.route('/logout')
@login_required
def logout():
    log_activity(current_user, 'تسجيل الخروج', ip_address=request.remote_addr)
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'success')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.password = form.password.data
        
        # إضافة دور المستخدم العادي
        user_role = Role.query.filter_by(name='user').first()
        if user_role:
            user.roles.append(user_role)
        
        db.session.add(user)
        db.session.commit()
        
        log_activity(user, 'إنشاء حساب جديد', ip_address=request.remote_addr)
        create_notification(
            user.id, 
            "مرحبًا بك في منصة مُدقِّق! يمكنك الآن تقديم مشاريعك للتدقيق.",
            category='success'
        )
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='التسجيل', form=form)

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            'تم إرسال رسالة بريد إلكتروني مع تعليمات إعادة تعيين كلمة المرور.',
            'info'
        )
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html',
                           title='إعادة تعيين كلمة المرور', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('الرابط غير صالح أو منتهي الصلاحية.', 'warning')
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        log_activity(user, 'إعادة تعيين كلمة المرور', ip_address=request.remote_addr)
        flash('تم تغيير كلمة المرور بنجاح.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

from flask import render_template,redirect,url_for,flash,request
from flask_login import login_user,logout_user,login_required
from . import auth
from ..models import User,db
from .forms import LoginForm
from .forms import RegisterationForm,ChangePasswordForm,ChangeEmailForm
from ..email import send_mail
from flask_login import current_user


@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remeberme.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误')
    return render_template('auth/login.html',form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经安全退出！')
    return  redirect(url_for('auth.login'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('你已经确认了你的账号，谢谢')
    else:
        flash('确认链接超时了')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,username = form.username.data,password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email,'确认你的账号','auth/email/confirm',user=user,token=token)
        flash('确认邮件已经发送至%s的邮箱，请查收现在已经可以登陆了' %(user.email))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] !='auth.':
            return  redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,'确认你的账号','auth/email/confirm',user = current_user,token=token)
    flash('确认邮件已经发送至%s的邮箱，请查收现在已经可以登陆了' % (current_user.email))
    return redirect(url_for('auth.login'))

@auth.route('/change-password',methods = ['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码已经更新成功，请重新登陆')
            return redirect(url_for('auth.logout'))
        else:
            flash('旧密码输入有误')
    return render_template("auth/change_password.html",form=form)


@auth.route('/change_email',methods = ['GET','POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_mail(new_email,'确认你的账号','auth/email/change_email',user = current_user,token=token)
            flash('新的确认邮件已经发送至你的新邮箱 %s,请注意查收'  %new_email)
            return redirect(url_for('auth.login'))
        else:
            flash('用户名或密码错误')
    return render_template("auth/change_email.html",form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('%s欢迎回来,您的新email地址已经开始生效了！' %current_user.username)
    else:
        flash('错误请求')
    return redirect(url_for('main.index'))
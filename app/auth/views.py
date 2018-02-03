from flask import render_template,redirect,url_for,flash,request
from flask_login import login_user,logout_user,login_required
from . import auth
from ..models import User,db
from .forms import LoginForm
from .forms import RegisterationForm


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

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,username = form.username.data,password = form.password.data)
        db.session.add(user)
        flash('现在已经可以登陆了')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)




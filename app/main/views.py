from datetime import datetime
from flask import render_template,session,redirect,url_for,flash
from flask_login import login_required

from . import main
from .forms import NameForm
from .. import db
from app.models import User
from app.email import send_mail


#自定义功能，输入一个邮箱地址，然后往里面发送测试邮件
@main.route('/sendemail',methods=['GET','POST'])
def sendemail():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        send_mail(session['name'],'test','mail/newuser')
        flash('邮件发送成功')
        return redirect(url_for('.sendemail'))
    return render_template('sendemail.html',name = session.get('name'),form = form)
    # send_mail('wenzhengde@qq.com','test','mail/newuser')



# @login_required
# def secret():
#     flash('未经授权不能查看该网页,请重新登陆')
#     return redirect(url_for('auth.login'))
@main.route('/')
def index():
    return render_template('index.html',current_time = datetime.utcnow())

# 这里要注意加入POST和GET否则点击后会报500错误
@main.route('/wtf',methods=['POST','GET'])
def wtf():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('好像你改名字了！')
        session['name'] = form.name.data
        return redirect(url_for('.wtf'))
        #用session改造刷新问题
        #name = form.name.data
    return render_template('wtf.html',form=form,name=session.get('name'))

@main.route('/data',methods=['GET','POST'])
def data():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            flash('你的名字还没在数据库中，现在将你的名字%s添加至数据库中的User表！' %user.username)
        else:
            session['known'] = True
            flash('数据库里面已经有你了！')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.data'))
    return render_template('data.html',form = form,name = session.get('name'),known = session.get('know',False))

# 传递参数进去后在render_template里面要使用name=name
@main.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)



## 做了URL自动的跳转
@main.route('/redirect')
def rd():
    return redirect('http://www.google.com')




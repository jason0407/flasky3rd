from datetime import datetime
from flask import render_template,session,redirect,url_for,flash,abort,request,current_app
from flask_login import login_required,current_user

from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm
from .. import db
from app.models import User,Role,Post
from app.email import send_mail
from ..decorators import admin_required,permission_required
from ..models import Permission


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
@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if  current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(body = form.body.data,author = current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html',form=form,posts = posts,pagination=pagination)

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
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)



## 做了URL自动的跳转
@main.route('/redirect')
def rd():
    return redirect('http://www.google.com')


@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return "For administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"

@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('你的账号已经更新')
        return redirect(url_for('.user',username = current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form = form)

@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('你的账号已经更新成功！')
        return redirect(url_for('.user',username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me = user.about_me
    return render_template('edit_profile.html', form=form,user = user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user !=post.author and \
        not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('您的文章已经更新')
        return redirect(url_for('.post',id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form = form)


from datetime import datetime
from flask import render_template,session,redirect,url_for,flash,abort,request,current_app,make_response
from flask_login import login_required,current_user

from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from .. import db
from app.models import User,Role,Post,Comment
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
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html',form=form,posts = posts,show_followed = show_followed,pagination=pagination)

# 开始关注某用户
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户信息有误，返回主页')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了%s' %username)
        return redirect(url_for('.user',username=username))
    current_user.follow(user)
    db.session.commit()
    flash('你已经开始关注%s' %username)
    return redirect(url_for('.user',username=username))

# 取消关注某用户
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户信息有误，返回主页')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你尚未关注该用户，返回主页')
        return redirect(url_for('.user',username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('你已经取消关注%s' %username)
    return redirect(url_for('.user',username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户信息有误，返回主页')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page,per_page= current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',user=user,title="关注你的用户",
                           endpoint = '.followers',pagination=pagination,followers=followers)

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户信息有误，返回主页')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.followed,'timestamp':item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',user=user,title="你关注的用户",
                           endpoint='.followed_by',pagination=pagination,follows=follows)



@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

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
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)



@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disable = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
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
        db.session.commit()
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

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body = form.body.data,
                          post = post,
                          author = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('你的评论已经提交')
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] +1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)

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


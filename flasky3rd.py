from flask import Flask,render_template
# 封装了客户端发送的请求
# request       请求上下文，请求对象，封闭了客户端发出的http请求中的内容
# session       请求上下文，用户会话, 用于存储请求之间需要"记信"的值的词典
# g             程序上下文，处理请求时用作临时存储对象。每次请求都会重设这个变量
#current_app    程序上下文，当前激活的程序实例
from flask import request
from flask import redirect
#使用外部方式运行相关程序,增加以后为运行时需要在后面加参数runserver使用
from flask_script import Manager
#导入BootStrap样式
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
#引入主要用于重定向，以解决刷新后需要表格重新提交
from flask import session,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
from flask_migrate import Migrate,MigrateCommand
import os
from flask_mail import Mail,Message
from threading import Thread




app = Flask(__name__)
# 犯了一个很傻B的错误，本来以为这个是放着玩玩的
# 没想到提前以后Bootstrap就没办法用了，一直卡在那里，然后折腾了很久，以为是环境问题
# app.debug = True


basedir  = os.path.abspath(os.path.dirname(__file__))
# 拼接数据库路径
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqllite')
# 每次请求结束后会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
#修改后需要重启Pycharm才生效，在这里坑了一小时，我日！
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'JASON <wenzhengde_us@163.com>'

print(os.environ.get('MAIL_USERNAME'))
print(os.environ.get('MAIL_PASSWORD'))
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = Manager(app)
#可以将数据库进行迁移
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)
# 如果需要使用Moment本地化时间来导入其库
moment = Moment(app)
# 实例化以使用bootstrap
mail = Mail(app)


class NameForm(FlaskForm):
    # 原来书上使用的是Require现在已经废弃改成DataRequire前面导入的时候也相应修改
    name = StringField('姓名： ',validators=[DataRequired()])
    submit = SubmitField('提交：')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref = 'role')

    #返回一个可读性的字符串表示模型主要用于测试
    def __repr__(self):
        return '<Role %r>' %self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return  '<User %r>' %self.username

# 添加程序上下文，完成后使用python flash3rd.py shell命令直接可以输入db，app,User，直接可以返回信息
def make_shell_context():
    return dict(app=app ,db=db, User=User, Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))

def send_mail(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] +subject,sender = app.config['FLASKY_MAIL_SENDER'],recipients = [to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    thr = Thread(target = send_async_email,args = [app,msg])
    thr.start()
    return thr
#异步发送邮件
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

#自定义功能，输入一个邮箱地址，然后往里面发送测试邮件
@app.route('/sendemail',methods=['GET','POST'])
def sendemail():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        send_mail(session['name'],'test','mail/newuser')
        flash('邮件发送成功')
        return redirect(url_for('sendemail'))
    return render_template('sendemail.html',name = session.get('name'),form = form)
    # send_mail('wenzhengde@qq.com','test','mail/newuser')


@app.route('/')
def index():
    return render_template('index.html',current_time = datetime.utcnow())

# 这里要注意加入POST和GET否则点击后会报500错误
@app.route('/wtf',methods=['POST','GET'])
def wtf():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('好像你改名字了！')
        session['name'] = form.name.data
        return redirect(url_for('wtf'))
        #用session改造刷新问题
        #name = form.name.data
    return render_template('wtf.html',form=form,name=session.get('name'))

@app.route('/data',methods=['GET','POST'])
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
        return redirect(url_for('data'))
    return render_template('data.html',form = form,name = session.get('name'),known = session.get('know',False))

# 传递参数进去后在render_template里面要使用name=name
@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)



## 做了URL自动的跳转
@app.route('/redirect')
def rd():
    return redirect('http://www.google.com')


## 自定义错误注意这里面的方法没有下划线
@app.errorhandler(404)
def page_not_found(e):
    return  render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500


if __name__ == '__main__':
    manager.run()
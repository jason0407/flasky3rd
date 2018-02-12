from flask import Flask,render_template
# 封装了客户端发送的请求
# request       请求上下文，请求对象，封闭了客户端发出的http请求中的内容
# session       请求上下文，用户会话, 用于存储请求之间需要"记信"的值的词典
# g             程序上下文，处理请求时用作临时存储对象。每次请求都会重设这个变量
# current_app    程序上下文，当前激活的程序实例
from flask import request
from flask import redirect
# 导入BootStrap样式
from flask_bootstrap import Bootstrap
from flask_mail import Mail,Message
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

db = SQLAlchemy()
# 实例化以使用bootstrap
bootstrap = Bootstrap()
# 如果需要使用Moment本地化时间来导入其库
moment = Moment()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
pagedown = PageDown()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 附加路由和自定义错误的页面

    # 注册蓝本
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app



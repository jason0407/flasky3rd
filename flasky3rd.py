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


app = Flask(__name__)
# 犯了一个很傻B的错误，本来以为这个是放着玩玩的
# 没想到提前以后Bootstrap就没办法用了，一直卡在那里，然后折腾了很久，以为是环境问题
# app.debug = True


bootstrap = Bootstrap(app)
manager = Manager(app)
# 如果需要使用Moment本地化时间来导入其库
moment = Moment(app)
# 实例化以使用bootstrap



@app.route('/')
def index():
    return render_template('index.html',current_time = datetime.utcnow())

@app.route('/test')
def test():
    return render_template('test.html')


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
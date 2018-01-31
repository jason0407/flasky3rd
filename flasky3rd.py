from flask import Flask
# 封装了客户端发送的请求
# request       请求上下文，请求对象，封闭了客户端发出的http请求中的内容
# session       请求上下文，用户会话, 用于存储请求之间需要"记信"的值的词典
# g             程序上下文，处理请求时用作临时存储对象。每次请求都会重设这个变量
#current_app    程序上下文，当前激活的程序实例
from flask import request
from flask import redirect
#使用外部方式运行相关程序,增加以后为运行时需要在后面加参数runserver使用
from flask_script import Manager

app = Flask(__name__)
app.debug = True
manager = Manager(app)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your broser is %s' %user_agent

## 做了URL自动的跳转
@app.route('/redirect')
def rd():
    return redirect('http://www.google.com')



if __name__ == '__main__':
    manager.run()
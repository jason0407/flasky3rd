from flask import Flask
# 封装了客户端发送的请求
# request       请求上下文，请求对象，封闭了客户端发出的http请求中的内容
# session       请求上下文，用户会话, 用于存储请求之间需要"记信"的值的词典
# g             程序上下文，处理请求时用作临时存储对象。每次请求都会重设这个变量
#current_app    程序上下文，当前激活的程序实例
from flask import request

app = Flask(__name__)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your broser is %s' %user_agent



if __name__ == '__main__':
    app.run(debug = True)
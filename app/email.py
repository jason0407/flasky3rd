from flask_mail import Message
from flask import render_template,current_app
from threading import Thread
# from manage import app
from app import mail

# 异步发送邮件
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to, subject, template, **kwargs):
    # 需要加入这一句，否则会上下文报错
    app = current_app._get_current_object()
    # 这里取配置文件为直接从manager return的app进行获取系统参数
    msg = Message(
        current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] +
        subject,
        sender=current_app.config['FLASKY_MAIL_SENDER'],
        recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr




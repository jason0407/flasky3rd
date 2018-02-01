#使用外部方式运行相关程序,增加以后为运行时需要在后面加参数runserver使用
from app import create_app,db
from app.models import User,Role
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand
# 犯了一个很傻B的错误，本来以为这个是放着玩玩的
# 没想到提前以后Bootstrap就没办法用了，一直卡在那里，然后折腾了很久，以为是环境问题
# app.debug = True

app = create_app('default')
manager = Manager(app)
#可以将数据库进行迁移
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)
# 添加程序上下文，完成后使用python flash3rd.py shell命令直接可以输入db，app,User，直接可以返回信息
def make_shell_context():
    return dict(app=app ,db=db, User=User, Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))






if __name__ == '__main__':
    manager.run()

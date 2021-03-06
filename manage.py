# 使用外部方式运行相关程序,增加以后为运行时需要在后面加参数runserver使用
from app import create_app, db
from app.models import User, Role,Post,Permission,Follow,Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
# 犯了一个很傻B的错误，本来以为这个是放着玩玩的
# 没想到提前以后Bootstrap就没办法用了，一直卡在那里，然后折腾了很久，以为是环境问题
# app.debug = True

app = create_app('default')
manager = Manager(app)
# 可以将数据库进行迁移
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
# 添加程序上下文，完成后使用python flash3rd.py shell命令直接可以输入db，app,User，直接可以返回信息


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,Post=Post,Permission=Permission,Follow=Follow,Comment=Comment)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    # 需要注意这里测试的路径
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
def deploy():
    """ Run Deploy"""
    from flask_migrate import upgrade
    from app.models import Role,User
    # 把数据库迁移到最新版本
    upgrade()

    # 创建用户角色
    Role.insert_roles()

if __name__ == '__main__':
    manager.run()

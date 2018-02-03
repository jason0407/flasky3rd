from . import db
#加入密码散列 其中generate_password_hash用于生成散列密码，check_password_hash用于校对散列密码
from werkzeug.security import generate_password_hash,check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    # 返回一个可读性的字符串表示模型主要用于测试
    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    # 如果试图读取password属性时，返回错误告诉其password不可读取
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 对password进行赋值时调用
    @password.setter
    # 传入User和password生成password_hash
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    # 传入User和password校验password_hash
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User %r>' % self.username
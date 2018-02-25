from . import db
#加入密码散列 其中generate_password_hash用于生成散列密码，check_password_hash用于校对散列密码
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from flask import current_app,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW |
                    Permission.COMMENT |
                    Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW |
                         Permission.COMMENT |
                         Permission.WRITE_ARTICLES |
                         Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def has_permission(self, perm):
        return self.permissions & perm == perm

    # 返回一个可读性的字符串表示模型主要用于测试
    def __repr__(self):
        return '<Role %r>' % self.name

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0X80

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disable = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))


    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format = 'html'),
                                                       tags=allowed_tags,strip=True))
db.event.listen(Comment.body,'set',Comment.on_change_body)

# 这里要注意需要增加一个UserMixin的一个参数用于标识用户状态，is_authenticated()表示用户已经登陆会返回True,is_active()表示是否允许登陆
# is_anonymous()对普通用户必须返回False
# get_id() 返回唯一标识符
class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    test1 = db.Column(db.String(32))
    followed = db.relationship('Follow',
                               # 使用foreign_keys指定外键
                               foreign_keys=[Follow.follower_id],
                               # 将两者指到follower模型，lazy='joined' 从联结查询的模型中加载相关对象
                               backref=db.backref('follower',lazy='joined'),
                               # 不会直接返回记录可是返回查询对象
                               lazy='dynamic',
                               # cascde将用户添加到数据库会话后，要把对象自动添加到对象中
                               cascade = 'all,delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    comments = db.relationship('Comment',backref='author',lazy='dynamic')
    # 静态方法后面就不用加括号
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'wenzhengde@qq.com':
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            self.follow(self)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    # def can(self,permissions):
    #     return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id}).decode('utf-8')



    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


    def generate_email_change_token(self,new_email,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'change_email':self.id,'new_email':new_email}).decode('utf-8')


    def change_email(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True
    def generate_fake(count=100):
        from sqlalchemy.exc import  IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()




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

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)
    # follow某用户
    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed = user)
            db.session.add(f)
    def unfollow(self,user):
        f = self.followed.filter_by(followed_id = user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self,user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id = user.id).first() is not None

    def is_followed_by(self,user):
        if user.id in None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return  Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.followed_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.username






class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    comments = db.relationship('Comment',backref='post',lazy='dynamic')

    # 这里要特别注意一些测试数据，当为空的时候就会有报错。
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,99)).first()
            # 这里注意下是sentences不是sentence
            p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,user_count-1)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    def on_changeed_body(target,value,oldvalue,initiator):
        allowed_tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),tags=allowed_tags,strip=True))

db.event.listen(Post.body,'set',Post.on_changeed_body)


class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser



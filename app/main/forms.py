from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,Regexp,ValidationError
from ..models import Role,User


class NameForm(FlaskForm):
    # 原来书上使用的是Require现在已经废弃改成DataRequire前面导入的时候也相应修改
    name = StringField('姓名:', validators=[DataRequired()])
    submit = SubmitField('提交')

class EditProfileForm(FlaskForm):
    name = StringField('真实姓名：', validators=[Length(0,64)])
    location = StringField('地址：', validators=[Length(0,64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('用户名：',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, ' 'numbers, dots or underscores')])
    confirmed = BooleanField('允许登陆')
    role = SelectField('角色',coerce=int)
    name = StringField('真实姓名：', validators=[Length(0, 64)])
    location = StringField('地址：', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('该Email地址已经被注册')
    def validate_username(self,field):
        if field.data != self.user.username and \
            User.query.filter_by(username = field.data).first():
            raise  ValidationError('该用户名已经被注册')


class PostForm(FlaskForm):
    body = TextAreaField('写出你的想法',validators=[DataRequired()])
    submit = SubmitField('提交')


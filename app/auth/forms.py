from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    # 原来书上使用的是Require现在已经废弃改成DataRequire前面导入的时候也相应修改
    email = StringField('Email:',validators=[DataRequired(),Email(),Length(1,64)])
    password = PasswordField('密码：', validators=[DataRequired()])
    # name = StringField('姓名:',validators=[DataRequired()])
    remeberme = BooleanField('记住登陆')
    submit = SubmitField('提交')

class RegisterationForm(FlaskForm):
    # 这里需要注意的是DataReuired后面是有括号的，被坑过一回
    email = StringField('Email:',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('用户名：',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, ' 'numbers, dots or underscores')])
    password = PasswordField('密 码：',validators=[DataRequired(),EqualTo('password2',message='密码必须和下面的匹配')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('注 册')

    # validate_开头的后面跟着字段名的方法，这个方法就和常规的验证函数一起被调用
    # 验证email是否已被注册
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册')
    # 验证用户名是否已被注册
    def validate_username(self,field):
        if User.query.filter_by(username = field.data).first():
            raise ValidationError('用户名已经存在')

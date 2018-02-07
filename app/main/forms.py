from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length


class NameForm(FlaskForm):
    # 原来书上使用的是Require现在已经废弃改成DataRequire前面导入的时候也相应修改
    name = StringField('姓名:', validators=[DataRequired()])
    submit = SubmitField('提交')

class EditProfileForm(FlaskForm):
    name = StringField('真实姓名：', validators=[Length(0,64)])
    location = StringField('地址：', validators=[Length(0,64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')


from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    # 原来书上使用的是Require现在已经废弃改成DataRequire前面导入的时候也相应修改
    name = StringField('姓名',validators=[DataRequired()])
    submit = SubmitField('提交')

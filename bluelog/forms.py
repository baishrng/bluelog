from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Optional, URL
from flask_ckeditor import CKEditorField

from models import CategoryModel


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1,20)])
    password = PasswordField('密码', validators=[DataRequired(), Length(8,128)])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1,60)])
    category = SelectField('分类', coerce=int, default=1) # coerce=int 表示强制为int类型
    body = CKEditorField('主体', validators=[DataRequired()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in CategoryModel.query.order_by(CategoryModel.name).all()]

class CategoryForm(FlaskForm):
    name = StringField("名称", validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField("提交")

    def validate_name(self, field):
        if CategoryModel.quert.filter_bu(name=field.data).first():
            raise ValidationError(message="分类名不能重复")

class CommentForm(FlaskForm):
    author = StringField("姓名", validators=[DataRequired(), Length(1,30)])
    email = StringField("邮箱", validators=[DataRequired(), Length(1,254), Email()])
    site = StringField("网站", validators=[Optional(), URL(), Length(0,255)])
    body = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField()

class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()
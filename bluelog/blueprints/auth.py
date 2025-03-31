from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, logout_user, login_required

from forms import LoginForm
from models import AdminModel
from utils import redirect_back

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form =LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = AdminModel.query.first()
        if admin:
            # 验证用户名和密码
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember=remember)
                flash('欢迎回来！', 'info')
                return redirect_back()
            flash("用户名或密码错误！", 'warning')
        else:
            flash("账户不存在", 'warning')
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("退出成功！", 'info')
    return redirect_back()
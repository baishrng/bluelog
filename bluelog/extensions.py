from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_caching import Cache
from flask_sslify import SSLify

bootstrap = Bootstrap4()
db = SQLAlchemy()
moment = Moment()
ckeditor = CKEditor()
mail = Mail()
csrf = CSRFProtect()
migrate = Migrate()
toolbar = DebugToolbarExtension()   # 调试程序
cache = Cache()     # 缓存
# sslify = SSLify()   # SSL 转发功能

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # 未登录则会重定向到登录界面
login_manager.login_message_category = 'warning'    # 设置消息的类别
login_manager.login_message = "请先登录"    # 设置消息

@login_manager.user_loader
def load_user(user_id):
    from models import AdminModel
    user = AdminModel.query.get(int(user_id))
    return user
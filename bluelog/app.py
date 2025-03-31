import click
from flask import Flask, render_template, request
import os
from flask_wtf.csrf import CSRFError
from flask_login import current_user
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

from blueprints.auth import bp as auth_bp
from blueprints.blog import bp as blog_bp
from blueprints.admin import bp as admin_bp
from config import config
from extensions import (bootstrap, db, moment, ckeditor, mail, login_manager,
                        csrf, migrate, toolbar, cache, sslify)
from models import AdminModel, CategoryModel, CommentModel


def create_app(config_name:str=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_logging(app)   # 注册日志处理器
    register_extensions(app)    # 注册扩展（扩展初始化）
    register_blueprints(app)    # 注册蓝图
    register_commands(app)  # 注册自定义shell命令
    register_errors(app)    # 注册错误处理函数
    register_shell_context(app) # 注册shell上下文处理函数
    register_template_context(app)  # 注册模板上下文处理函数

    return app

def register_logging(app:Flask):
    """注册日志处理器"""

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] % (remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    app.logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 文件路径, 最大文件尺寸, 备份数量
    file_handler = RotatingFileHandler('logs/bluelog.log', maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=os.getenv('MAIL_SERVER'),
        fromaddr=os.getenv('MAIl_USERNAME'),
        toaddrs=os.getenv('BLUELOG_ADMIN_EMAIL'),
        subject='Application errors',
        credentials=(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(mail_handler)

def register_extensions(app:Flask):
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    toolbar.init_app(app)
    cache.init_app(app)
    sslify.init_app(app)

def register_blueprints(app:Flask):
    app.register_blueprint(blog_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

def register_shell_context(app:Flask):
    @app.shell_context_processor
    def make_shell_context():
        return {'db':db}

def register_template_context(app:Flask):
    @app.context_processor
    def make_template_context():
        admin = AdminModel.query.first()
        categories = CategoryModel.query.order_by(CategoryModel.name).all()

        if current_user.is_authenticated:
            unread_comments = CommentModel.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None

        return dict(admin=admin, categories=categories, unread_comments=unread_comments)

def register_errors(app:Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    # 捕捉 CSRF 错误
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        # description = e.description
        description = "会话过期或失效，请返回上一页面重试"
        return render_template('errors/400.html', description=description), 400

def register_commands(app:Flask):
    @app.cli.command()
    @click.option('--category', default=10, help="分类的数量默认为10")
    @click.option('--post', default=50, help="文章数量默认为50")
    @click.option('--comment', default=500, help="评论数量默认为50")
    def forge(category, post, comment):
        '''生成虚拟分类、文章、评论数据'''
        from fakes import fake_posts, fake_admin, fake_comments, fake_categories

        db.drop_all()
        db.create_all()

        click.echo('正在生成管理员...')
        fake_admin()

        click.echo(f"正在生成{category}条分类")
        fake_categories(category)

        click.echo(f"正在生成{post}篇文章")
        fake_posts(post)

        click.echo(f"正在生成{comment}条评论")
        fake_comments(comment)

        click.echo("数据生成完成!")

    @app.cli.command()
    @click.option('--username', prompt=True, help="登录用户名")
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help="登录密码")
    def init(username, password):
        '''初始化博客'''
        click.echo("初始化数据库......")
        db.create_all()

        admin = AdminModel.query.first()
        if admin:
            click.echo("管理员账号已经存在......")
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('正在创建临时的管理员账户......')
            admin = AdminModel(
                username=username,
                blog_title='xin的博客',
                blog_sub_title="No, i am the real thing.",
                name='七月',
                about='关于你'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = CategoryModel.query.first()
        if category is None:
            click.echo("正在初始化默认分类......")
            category = CategoryModel(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo("完成！")



if __name__ == '__main__':
    pass

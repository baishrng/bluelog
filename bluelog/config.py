import os

basedir = os.path.abspath(os.path.dirname(__file__))    # 获取当前文件的文件目录绝对路径

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用对象修改跟踪

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '<EMAIL>')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '<PASSWORD>')
    MAIL_DEFAULT_SENDER = ('Bluelog', MAIL_USERNAME)

    BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL', '<EMAIL>')
    BLUELOG_POST_PRE_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PRE_PAGE = 15

    BLUELOG_THEMES = {'perfect_blue': "Perfect Blue", "black_swan":"Black Swan"}

    SSL_DISABLED = True


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'data-dev.db')
    DEBUG_TB_ENABLED = True     # 打开 Flask-DebugToolBar
    DEBUG_TB_PROFILER_ENABLED = True    # 打开性能分析器
    SQLALCHEMY_RECORD_QUERIES = True    # 开启 sqlalcheny 的查询记录
    CACHE_NO_NULL_WARNING = True   # 关闭 Cache 设置为 null 的提示信息

class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SSQLALCHENY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data.db'))
    CACHE_TYPE = 'simple'  # 设置 Cache 后端类型


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
import unittest

from flask import url_for

from bluelog.extensions import db
from bluelog.models import AdminModel
from bluelog.app import create_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app('testing')
        self.context = app.test_request_context()  # 请求上下文
        self.context.push()
        self.client = app.test_client()  # 模拟请求客户端
        self.runner = app.test_cli_runner()  # 测试命令执行器

        db.create_all()
        user = AdminModel(name='xin', username='xin', about='I am a man.', blog_title='三月春风似剪刀',
                          blog_sub_title='a test')
        user.set_password('12345678')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'xin'
            password = '12345678'

        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)

    def test_result(self):
        self.assertEqual('20', '20')


if __name__ == '__main__':
    unittest.main()

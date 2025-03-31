import random

from sqlalchemy.exc import IntegrityError
from extensions import db
from models import AdminModel, CategoryModel, PostModel, CommentModel
from faker import Faker

faker = Faker("zh-CN")

def fake_admin():
    admin = AdminModel(
        username='admin',
        blog_title='Bluelog',
        blog_sub_title="No, i am the real thing.",
        name='baishng',
        about="Um, l, Mima Kirigoe, had a fun time as a member of CHAM..."
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()

def fake_categories(count:int=10):
    category = CategoryModel(name='默认')
    db.session.add(category)

    for i in range(count):
        category = CategoryModel(name=faker.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

def fake_posts(count:int=50):
    for i in range(count):
        post = PostModel(
            title=faker.sentence(),
            body=faker.text(2000),
            category=CategoryModel.query.get(random.randint(1, CategoryModel.query.count())),
            timestamp=faker.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()

def fake_comments(count:int=500):
    for i in range(count):
        comment = CommentModel(
            author=faker.name(),
            email=faker.email(),
            site=faker.url(),
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            reviewed=True,
            post=PostModel.query.get(random.randint(1, PostModel.query.count()))
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        # 未审核评论
        comment = CommentModel(
            author=faker.name(),
            email=faker.email(),
            site=faker.url(),
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            reviewed=False,
            post=PostModel.query.get(random.randint(1, PostModel.query.count()))
        )
        db.session.add(comment)

        # 管理员发表的评论
        comment = CommentModel(
            author='Mima Kirigoe',
            email='mima@example.com',
            site='example.com',
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=PostModel.query.get(random.randint(1, PostModel.query.count()))
        )
        db.session.add(comment)
    db.session.commit()

    # 回复
    for i in range(salt):
        comment = CommentModel(
            author=faker.name(),
            email=faker.email(),
            site=faker.url(),
            body=faker.sentence(),
            timestamp=faker.date_time_this_year(),
            reviewed=True,
            replied=CommentModel.query.get(random.randint(1, CommentModel.query.count())),
            post=PostModel.query.get(random.randint(1, PostModel.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


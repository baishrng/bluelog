from flask import (Blueprint, request, current_app, url_for,
                   render_template, flash, redirect, abort, make_response)
from flask_login import current_user

from emails import send_new_comment_email, send_new_reply_email
from forms import AdminCommentForm, CommentForm
from models import PostModel, CategoryModel, CommentModel
from extensions import db, cache
from utils import redirect_back

bp = Blueprint('blog', __name__, url_prefix='/')

@bp.route('/')
@cache.cached(timeout=30*60)    # 设置缓存，过期时间为 30分钟
def index():
    page = request.args.get('page', 1, type=int)    # 从查询字符串获取当前页数
    per_page = current_app.config['BLUELOG_POST_PRE_PAGE']  # 每页数量
    print(per_page)
    pagination = PostModel.query.order_by(PostModel.timestamp.desc()).paginate(page=page, per_page=per_page) # 分页对象
    posts = pagination.items    # 当前页数的记录列表
    return render_template('blog/index.html', pagination=pagination, posts=posts)

@bp.route('/about')
def about():
    return render_template('blog/about.html')

@bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = CategoryModel.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PRE_PAGE']
    pagination = (PostModel.query.with_parent(category).order_by(PostModel.timestamp.desc()).
                  paginate(page=page, per_page=per_page))
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)

@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
@cache.cached(timeout=5*30, query_string=True)  # 设置缓存，过期时间为5分钟，并将查询参数的散列值作为缓存的键
def show_post(post_id):
    post = PostModel.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PRE_PAGE']
    pagination = (CommentModel.query.with_parent(post).order_by(CommentModel.timestamp.desc()).
                  paginate(page=page, per_page=per_page))
    comments = pagination.items

    # 发表评论表单处理
    if current_user.is_authenticated:   # 如果当前用户已登录，使用管理员表单
        form = AdminCommentForm()
        form.author.data = current_user.name    # 隐藏字段
        form.email.data = current_app.config['BLUELOG_EMAIL']   # 隐藏字段
        form.site.data = url_for('blog.index')  # 隐藏字段
        from_admin = True
        reviewed = True
    else:   # 未登录则使用普通表单
        form = CommentForm()
        from_admin = False
        reviewed = False

    # 发表评论表单处理
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = CommentModel(author=author, email=email, site=site, body=body,
                               from_admin=from_admin, reviewed=reviewed, post=post)
        replied_id = request.args.get('reply')
        if replied_id:  # 判断该评论是否是回复
            replied_comment = CommentModel.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:   # 根据登录状态的不同显示不同的提示消息
            flash("评论发表成功！", 'success')
        else:
            flash("感谢！您的评论经过审核后将会发布!", "info")
            send_new_comment_email(post)    # 发送邮件提醒管理员
        return redirect(url_for(".show_post", post_id=post.id))

    return render_template('blog/post.html', post=post, pagination=pagination, comments=comments)

@bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = CommentModel.query.get_or_404(comment_id)
    return redirect(url_for('.show_post', post_id=comment.post_id, reply=comment_id,
                            author=comment.author) + "#comment-form")



@bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30*24*60*60)
    return response
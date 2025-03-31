from flask import Blueprint, request, current_app, render_template, flash, redirect, url_for
from flask_login import login_required

from extensions import db
from forms import PostForm
from models import PostModel, CategoryModel, CommentModel
from utils import redirect_back

bp = Blueprint('admin', __name__, url_prefix='/admin')


# 注册一个钩子函数，使得这个蓝图下的所有视图函数在请求之前都需要登录，
# 避免忘记在视图函数下方添加 @login_required 标记
@bp.before_request
@login_required
def before_request():
    pass


@bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = CategoryModel.query.get(form.category.data)
        post = PostModel(title=title, boby=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash("文章创建成功", 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    else:
        return render_template('admin/new_post.html', form=form)


@bp.route('/post/manage')
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_MANAGE_POST_PER_PAGE']
    pagination = (PostModel.query.order_by(PostModel.timestamp.desc()).
                  paginate(page=page, per_page=per_page))
    posts = pagination.items
    return render_template('admin/manage_post.html', posts=posts, pagination=pagination)


@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = PostModel.query.get(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = CategoryModel.query.get(form.category.data)
        db.session.commit()
        flash("文章修改成功！", 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    else:
        form.title.data = post.title  # 预定义表单中的title字段值
        form.body.data = post.body
        form.category.daa = post.category_id
        return render_template('admin/edit_post.html', form=form)


@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = PostModel.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("文章删除成功!", 'success')
    return redirect_back()


@bp.route('/new_category')
def new_category():
    pass


@bp.route('/manage_category')
@login_required
def manage_category():
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = CommentModel.query.filter_by(reviewed=False)
    elif filter_rule == "admin":
        filtered_comments = CommentModel.query.filter_by(from_admin=True)
    else:
        filtered_comments = CommentModel.query

    pagination = filtered_comments.order_by(CommentModel.timestamp.desc()).paginate(page=page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@bp.route('/comment/manage')
def manage_comment():
    pass


@bp.route('/set-comment/<int:post_id>', methods=['POST'])
@login_required
def set_comment(post_id):
    post = PostModel.query.get_or_404(post_id)
    if post.set_comment:
        post.set_comment = False
        flash("已关闭评论功能！", 'info')
    else:
        post.set_comment = True
        flash('已开启评论功能！', 'info')
    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post.id))


@bp.route('/commit/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_commit(comment_id):
    comment = CommentModel.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('评论审核通过！', 'success')
    return redirect_back()


@bp.route('/commit/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = CommentModel.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除！', 'success')
    return redirect_back()


@bp.route('/category/<int:category_id>/delete>', methods=['POST'])
@login_required
def delete_category(category_id):
    if category_id == 1:
        flash("默认分类无法删除！", 'warning')
        return redirect_back()
    category = CategoryModel.query.get_or_404(category_id)
    category.delete()  # 调用 category 对象的 delete() 方法删除分类
    flash("分类删除成功！", 'success')
    return redirect(url_for('admin.manage_category'))


@bp.route('/new_link')
def new_link():
    pass


@bp.route('/manage_link')
def manage_link():
    pass


@bp.route('/settings')
def settings():
    pass

from datetime import datetime
from flask import render_template, redirect, url_for, make_response, request, abort, flash
from flask_login import current_user, login_required

from . import main_blueprint
from .forms import *
from ..models import *
from ..decorators import permission_required


@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit() and current_user.can(Permission.WRITE):
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        qury = current_user.followed_posts
    else:
        qury = Post.query

    page = request.args.get('page', 1, type=int)
    pagination = qury.order_by(Post.timestamp.desc()).paginate(
        page, error_out=False, per_page=current_app.config.get('FLASKY_POSTS_PER_PAGE', 5))
    posts = pagination.items
    return render_template('index.html', time=datetime.utcnow(), form=form,
                           posts=posts, pagination=pagination, show_followed=show_followed)


@main_blueprint.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main_blueprint.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('comment success')
    page = request.args.get('page', 1, int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=5, error_out=False)
    comments = pagination.items

    return render_template('post.html', posts=[post], pagination=pagination, comments=comments, form=form)


@main_blueprint.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('post updated.')
        return redirect(url_for('main.post', id=id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main_blueprint.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('user invalid')
        redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('already following')
    else:
        current_user.follow(user)
        db.session.commit()
        flash('following OK.')
    return redirect(url_for('main.user', username=username))


@main_blueprint.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('user invalid')
        redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('not following')
    else:
        current_user.unfollow(user)
        db.session.commit()
        flash('unfollow OK.')
    return redirect(url_for('main.user', username=username))


@main_blueprint.route('/followers/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('user invalid')
        redirect(url_for('main.index'))
    page = request.args.get('page', 1, int)
    pagination = user.followers.paginate(page, per_page=5, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', pagination=pagination, user=user, endpoint='main.followers',
                           follows=follows, titel='Followers of')


@main_blueprint.route('/followed_by/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('user invalid')
        redirect(url_for('main.index'))
    page = request.args.get('page', 1, int)
    pagination = user.followed.paginate(page, per_page=5, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', pagination=pagination, user=user, endpoint='main.followed_by',
                           follows=follows, titel='Followed by')


@main_blueprint.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=3*60)
    return resp


@main_blueprint.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=3*60)
    return resp

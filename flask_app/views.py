from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user 
from .models import Post, User, Comment, Likes, followers
from . import db 
from werkzeug.security import generate_password_hash

views = Blueprint("views", __name__) 
@views.route('/')
def index():
    return render_template('index.html',user = current_user)
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route("/process-post", methods=['GET', 'POST'])
@login_required
def process_post(): 
    if request.method == "POST": 
        title = request.form.get('title')
        text = request.form.get('text')
        if not title: 
            flash('Post must have a title' ,category='error') 
        if not text: 
            flash('Post must contain content', category='error') 
        else: 
            post=Post(title=title,text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created', category='success') 
            return redirect(url_for('views.home'))
    return render_template('createpost.html', user = current_user) 

@views.route('/delete-post/<id>') 
@login_required
def delete_post(id): 
    post = Post.query.filter_by(id=id).first() 
    
    if not post: 
        flash('Post does not exist.', category='error') 
    elif current_user.id != post.author:
        flash('You do not have permission to delete post', category='error')
    else: 
        db.session.delete(post) 
        db.session.commit()
        flash('Post has been deleted.', category='success')

    return redirect ( url_for('views.home')) 

@views.route("/posts/<username>")
@login_required
def posts(username): 
    user = User.query.filter_by(username=username).first()
    if not user: 
        flash('No user found.', category='error')
        return redirect(url_for('views.home'))
    posts = user.posts
    return render_template('post.html', user=user, posts=posts, username=username) 

@views.route("/create-comment/<id>", methods=['POST'])
@login_required
def comment(id):
    text = request.form.get('text')
    if not text: 
        flash('Comment must contain content.',category='error')
        return redirect(url_for('views.home'))
    else: 
        post = Post.query.filter_by(id = id)
        if post: 
            comment = Comment(text = text, author=current_user.id, post_id =id)
            db.session.add(comment)
            db.session.commit()
        else: 
            flash('Post does not exist', category='error')
        return redirect(url_for('views.home'))

@views.route('/delete-comment/<id>')
@login_required
def delete_comment(id): 
    comment = Comment.query.filter_by(id=id).first() 
    
    if not comment: 
        flash('Comment does not exist.', category='error') 
    elif current_user.id != comment.author:
        flash('You do not have permission to delete comment', category='error')
    else: 
        db.session.delete(comment) 
        db.session.commit()
        flash('Comment has been deleted.', category='success')

    return redirect ( url_for('views.home')) 

@views.route('/like-post/<id>', methods=['GET'])
@login_required 
def like_post(id):
    post = Post.query.filter_by(id=id).first() 
    like = Likes.query.filter_by(author =current_user.id, post_id=id).first()
    if not post: 
        flash('Post does not exist', category='error') 
    elif like: 
        db.session.delete(like)
        db.session.commit() 
    else: 
        like = Likes(author=current_user.id, post_id=id)
        db.session.add(like) 
        db.session.commit() 
        
    return redirect(url_for('views.home')) 

@views.route('/view-profile/<int:id>')
@login_required 
def view_profile(id): 
    user = User.query.filter_by(id=id).first()
    posts  = current_user.posts
    if not user: 
        flash('User does not exist', category='error')
    return render_template('view_profile.html', user = current_user, posts = posts) 


@views.route('/update-post/<int:id>', methods = ['POST', 'GET'])
@login_required
def update_post(id):
    post = Post.query.filter_by(id=id).first() 
    if not post:
        flash('Post does not exist', category='error') 
    if request.method == "POST": 
        post.title = request.form.get('title')
        post.text = request.form.get('text')
        db.session.commit()
        flash('Post updated', category='success') 
        return redirect(url_for('views.home'))
    return render_template('update_post.html', user = current_user, post = post) 

@views.route('/update-user/<int:id>', methods = ['POST', 'GET'])
@login_required
def update_user(id):
    user = User.query.filter_by(id=id).first()
    posts = current_user.posts
    if not user: 
        flash('User does not exist.', category='error')
    if request.method == "POST": 
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.username = request.form.get('username') 
        user.email = request.form.get('email')

        if len(user.username) < 2:
            flash('User name is too short.')
        elif len(user.email) < 4: 
            flash("Email is invalid.", category='error') 
        else: 
            db.session.commit()
            flash('User updated', category='success') 
            return render_template('view_profile.html', user = current_user, posts = posts)
    return render_template('update_user.html', user = current_user) 

@views.route('/follow/<int:id>', methods = ['POST'])
@login_required
def follow_user(id):
    user = User.query.filter_by(id=id).first() 
    if not user:
        flash('User does not exist', category='error')
    if user == current_user:
        flash('You cannot follow yourself', category='error')
        return redirect(url_for('views.home'))
    else:
        current_user.follow(user)
        db.session.commit() 
    return redirect(url_for('views.home')) 

@views.route('/unfollow/<int:id>', methods = ['POST'])
@login_required
def unfollow_user(id):
    user = User.query.filter_by(id=id).first() 
    if not user:
        flash('User does not exist', category='error')
    if user == current_user:
        flash('You cannot unfollow yourself', category='error')
    else:
        current_user.unfollow(user)
        db.session.commit() 
    return redirect(url_for('views.home')) 


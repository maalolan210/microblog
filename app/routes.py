import os
from flask import render_template, flash, redirect, url_for, request, send_file
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, UploadForm
from app.models import User, Post
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from werkzeug.utils import secure_filename, send_file

# a dict store the avatar path for each user
path = {}
############ before request

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

############ index

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = current_user.followed_posts().all()
    # home page avatar displaying
    global path
    if current_user.username in path:
        user_path = {'path': path[current_user.username]}
        return render_template("index.html", title='Home Page', form=form,
                            posts=posts, path=user_path)
    else:
        return render_template("index.html", title='Home Page', form=form,
                            posts=posts)
##### show the logged in users
@app.route('/showLoggedin')
@login_required
def showLoggedin():
    
    # get all logged in users
    logged_in_users = User.query.filter_by(status=True).all()
    print(len(logged_in_users))
    users = []
    for user in logged_in_users:
        print(user.username)
        users.append({'name': user.username, 'path': user.path})

    return render_template("loggedInUsers.html", title='Logged in', users=users)
  
############ login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        # set the user's status to True, which means logged in
        user.login_set_status()
        print(user.status)
        db.session.commit()
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


############ logout

@app.route('/logout')
def logout():
    # set the user's status to False, which means logged out

    user = User.query.filter_by(username=current_user.username).first()
    user.logout_set_status()
    db.session.commit()
    logout_user()
    
    
    return redirect(url_for('index'))



############ register

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


############ send image back
# @app.route('/user/' + path)
# def get_image():
#     print("yes")
#     return send_file('/user/' + path, mimetype='image/jpeg')


############ user

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()

    global path
    # store the path of the avatar into user.path in user's database
    user.path = path[current_user.username]
    db.session.commit()
    print("user")
    print(user.path)
    user_path = {'path': user.path}
    
    return render_template('user.html', user=user, posts=posts, form=form, path=user_path)


############ upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save("app/static/" + filename)
        # record the image path into a global variable because can't access user here
        global path
        path[current_user.username] = filename
        print("test")
        print(path)
        flash('Upload successfully!')
        return redirect(url_for('upload'))

    return render_template('upload.html', form=form)



############ edit profile


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)



############ follow

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))



############ unfollow

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))



############ explore

@app.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)

from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import jinja2
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogyourlife@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "JaCIWXViOStUvThg"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__ (self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='user')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['/', 'blog', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

@app.route('/')
def index():
        users = User.query.all()
        return render_template('index.html', blog_users=users)

@app.route('/blog', methods=['GET'])
def blog():
    if len(request.args) > 0:
        if request.args.get("id"):
            blog = Blog.query.get(request.args.get("id"))
            user = User.query.get(blog.user_id)
            return render_template('individual_blog.html', blog=blog, user=user)
        elif request.args.get("user"):
            user = User.query.get(request.args.get("user"))
            blogs = Blog.query.filter_by(user_id=user.id).all()
            return render_template('single_user.html', blogs=blogs, user=user)
    else:
        users = User.query.all()
        blogs = Blog.query.all()
        return render_template('list_blogs.html', blogs=blogs, users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check to see if user entered in all fields
        # Check if user exists
        # Check if password is correct
        # Store session when user logs in

        username = request.form['username']
        password = request.form['password']

        username_err = ""
        password_err = ""

        if not username:
            username_err = "Username field cannot be left blank."
        if not password:
            password_err = "Password field cannot be left blank."

        if not username_err and not password_err:
            user = User.query.filter_by(username=username).first()
            if user:
                if password == user.password:
                    session['user'] = username
                    return redirect('/newpost')
                else:
                    password_err = "The password that was entered is incorrect."
                    return render_template('login.html', username=username, username_err=username_err, password_err=password_err)
            else:
                username_err = "This user does not exist"
                return render_template('login.html', username=username, username_err=username_err, password_err=password_err)
        else:
            return render_template('login.html', username=username, username_err=username_err, password_err=password_err)
    else:        
        return render_template('login.html')

@app.route('/logout')
def logout():
    del session['user']
    return redirect('/blog')

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if not blog_title:
            return render_template('add_a_blog.html', title_error="You must enter a blog title.")
        elif not blog_body:
            return render_template('add_a_blog.html', body_error="You must enter a blog body.")
        else:
            user = User.query.filter_by(username=session['user']).first()
            new_blog = Blog(blog_title, blog_body, user)

            db.session.add(new_blog)
            db.session.commit()

            return redirect(f'/blog?id={new_blog.id}')
    else:
        return render_template('add_a_blog.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Check if user entered in fields
    # Check if passwords match
    # Check if user already exists in database
    # Store user in database

    pattern = re.compile('.{3,20}')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        username_err = ""
        password_err = ""
        confirm_password_err = ""

        if not pattern.match(username):
            username_err = "Username must contain 3-20 characters."
        elif ' ' in username:
            username_err = "Username cannot contain any spaces."
        elif User.query.filter_by(username=username).first():
            username_err = "This username is taken."

        if not pattern.match(password):
            password_err = "Password must contain 3-20 characters."
        elif ' ' in password:
            password_err = "Password cannot contain any spaces."

        if not pattern.match(confirm_password):
            confirm_password_err = "Password must contain 3-20 characters."
        elif ' ' in confirm_password:
            confirm_password_err = "Password cannot contain any spaces."
        elif password != confirm_password:
            confirm_password_err = "Passwords do not match."

        if not username_err and not password_err and not confirm_password_err:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            session['user'] = new_user.username
            
            return redirect('/newpost')
        else:
            return render_template('signup.html', username=username, username_err=username_err, password_err=password_err, confirm_password_err=confirm_password_err)
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    app.run()
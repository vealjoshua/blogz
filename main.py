from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import jinja2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.String(255))

    def __init__ (self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():
    if len(request.args) > 0:
        blog = Blog.query.get(request.args.get("id"))
        return render_template('blog_entry.html', blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('index.html', blogs=blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        new_blog = Blog(blog_title, blog_body)

        db.session.add(new_blog)
        db.session.commit()

        return redirect(f'/blog?id={new_blog.id}')
    else:
        return render_template('add_a_blog.html')

if __name__ == '__main__':
    app.run()
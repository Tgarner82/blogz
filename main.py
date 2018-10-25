from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:strider1@localhost:8889/blogz' 
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'strider'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    user_blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(999))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        



@app.route('/', methods=['POST','GET'])
def index():
    users = User.query.all()
    return render_template('index.html',users=users)

@app.route('/blog', methods=['POST','GET'])
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/single_blog', methods=['GET'])
def single_blog():
    blog_id = int(request.args.get('id'))
    blog = Blog.query.get(blog_id)
    return render_template('singleblog.html', blog=blog)

@app.route('/userblog', methods=['GET'])
def user_blog():
    user_id = int(request.args.get('user'))
    blogs = Blog.query.filter_by(owner_id=user_id)
    return render_template('userblog.html', blogs=blogs)
   
@app.route('/newpost', methods=['POST','GET'])
def newpost():
    error = ''
    if request.method == 'POST':
        blog_name = request.form['title']
        blog_body = request.form['body']

        if len(blog_name) == 0 or len(blog_body) == 0:
            error = 'Please enter text.'
        else:
            blog_owner = User.query.filter_by(username = session['username']).first()
            new_blog = Blog(blog_name, blog_body, blog_owner)
            db.session.add(new_blog)
            db.session.commit()


            return redirect('/single_blog?id='+str(new_blog.id))
   
    return render_template('newpost.html', error=error)

@app.before_request
def require_login():
    allowed_routes = ['signup', 'login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/signup', methods=['POST','GET'])
def signup():
    user_error = ''
    password_error = ''
    verify_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == '':
            user_error = 'Please do not leave an empty field.'
        else:
            username = username 
            if len(username) < 3 or len(username) > 20:
                user_error = 'User name must be longer than 3 and shorter than 20 characters.'
            else:
                username = username
                if username:
                    for x in username:
                        if x.isspace():
                            user_error = 'Please do not use a space.'
                        else:
                            username = username
        if password == '':
            password_error = 'Please do not leave an empty field.'
        else:
            password=password
            if len(password) < 3 or len(password) > 20:
                password_error = 'User name must be longer than 3 and shorter than 20 characters.'
                password_error = ''
            else:
                password=password
                if password:
                    for x in password:
                        if x.isspace():
                            password_error = 'Please do not use a space'
                            password_error =''
                        else:
                            password=password
        if verify == '':
            verify_error = 'Please do not leave an empty field.'
        else:
            verify=verify
            if verify != password:
                verify_error = 'Password must match.'
            else:
                verify=verify
        if not user_error and not password_error and not verify_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/')
            else:
                return '<h1>User Already Exist.</h1>'
    
    return render_template('signup.html', user_error=user_error, password_error=password_error, verify_error=verify_error)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            return '<h1>User Name does not exist!</h1>'
        else:
            user=user
            if user.password != password:
                return '<h1>Password is incorrect!</h2>'
            else:
                user.password=user.password
                if user and user.password == password:
                    session['username'] = username
                    flash('Logged in.')
                    return redirect('/newpost')
                else:
                    return redirect('/signup')

    return render_template('login.html')


@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['username']
    return redirect('/blog')

    
if __name__ == '__main__':
    app.run()
from app import app
from flask import render_template
from app.forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Duke'}
    posts = [
        {
        'author' : {'username': 'John'},
        'body' : 'Beautiful day in Bamenda!'
        },
        {
            'author' : {'username': 'Precious'},
            'body' : 'Beautiful day in Yaounde'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts = posts)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)
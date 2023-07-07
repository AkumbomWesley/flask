import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    #configuring the sqlite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db') #gets location of apps database from SQLALCHEMY_DATABASE_URI and database url from environment variable or a configured app.db database
    SQLALCHEMY_TRACK_MODIFICATIONS = False #This prevents flask sqlalchemy from sending a signal to the application every time a change is about to be made in the database
    
    #configuring the email server (to recieve error notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['keyzwesley@gmail.com']
    
    #Number of items to be displayed per page
    POSTS_PER_PAGE = 3
    
    #languages
    LANGUAGES = ['en', 'es', 'fr']
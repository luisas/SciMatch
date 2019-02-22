# This file contains an example Flask-User application.
# To keep the example simple, we are applying some unusual techniques:
# - Placing everything in one file
# - Using class-based configuration (instead of file-based configuration)
# - Using string-based templates (instead of file-based templates)

import datetime
from flask import Flask, request, render_template_string, render_template
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin


# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://luisasantus:password@localhost/scimatch?charset=utf8'    # File-based SQL database'    # File-based SQL database
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'SciMatchApp@gmail.com'
    MAIL_PASSWORD = 'AinaGabriLuisa'
    MAIL_DEFAULT_SENDER = '"SciMatch" <noreply@example.com>'

    # Flask-User settings
    USER_APP_NAME = "SciMatch"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"


def create_app():
    """ Flask application factory """

    # Create Flask app load app.config
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')

    # Initialize Flask-BabelEx
    babel = Babel(app)

    # Initialize Flask-SQLAlchemy
    db = SQLAlchemy(app)

    # Define the User data-model.
    # NB: Make sure to add flask_user UserMixin !!!
    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        email = db.Column(db.String(255), nullable=False, unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')

        # User information
        first_name = db.Column(db.String(100), nullable=False, server_default='')
        last_name = db.Column(db.String(100), nullable=False, server_default='')

        # Define the relationship to Role via UserRoles
        roles = db.relationship('Role', secondary='user_roles')

    # Define the Role data-model
    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


    class City(db.Model):
        __tablename__ = 'city'
        name = db.Column(db.String(100), nullable=False, server_default='',primary_key=True)

    class Preference(db.Model):
        __tablename__= 'preference'
        id = db.Column(db.Integer(), primary_key=True)

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User, RoleClass=Role)

    # Create all database tables
    db.create_all()

    # To delete
    #city = City(name="Barcelona")
    #city2= City(name="Honolulu")
    #db.session.add(city)
    #db.session.add(city2)
    #db.session.commit()
    if not Role.query.filter(Role.name == 'Applicant').first():
        role = Role (name = "Applicant")
        role2 = Role( name ="Group")
        db.session.add(role)
        db.session.add(role2)
        db.session.commit()

    # Create 'member@example.com' user with no roles
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(
            email='member@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            email='admin@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()

    # The Home page is accessible to anyone

    # Selects which home page to use. If the user is logged in then it checks if
    # it is an applicant or a group and shows the right view accordingly.
    @app.route('/')
    def home_page():
        role_name ="Guest"
        if not current_user.is_authenticated:
            return render_template("/home_page.html")
        else:
            role_id = UserRoles.query.filter_by( user_id = current_user.id).first().role_id
            role_name = Role.query.filter_by( id = role_id).first().name
            if role_name == "Applicant":
                matches = City.query.order_by(City.name).all()
                return render_template("/home_page_applicant.html",matches=matches, role=role_name)
            elif role_name == "Group":
                return render_template("/home_page_group.html",role=role_name)

    def change_pref():
        dropdown_list = City.query.order_by(City.name).all()
        return render_template("/change_pref.html",dropdown_list = dropdown_list)
    app.add_url_rule('/change', 'change_pref', change_pref)

    def profile_applicant():
        return render_template("/profile_applicant.html")
    app.add_url_rule('/profile_applicant', 'profile_applicant', profile_applicant)

    def chat_applicant():
        return render_template("/chat_applicant.html")
    app.add_url_rule('/chat_applicant', 'chat_applicant', chat_applicant)




    return app

# Start development web server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

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
import uuid
import pandas




# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:Aina100995@@localhost/scimatch10?charset=utf8'    # File-based SQL database'    # File-based SQL database
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
        gender = db.Column(db.String(100), nullable=False, server_default='')
        birthday = db.Column(db.Date,server_default="1990/12/10")

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

    class Country(db.Model):
        __tablename__ = 'country'
        abbreviation_fips = db.Column(db.String(5), nullable=False, server_default='',primary_key=True)
        name = db.Column(db.String(100),nullable=False)

    class City(db.Model):
        __tablename__ = 'city'
        id = id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        country_abbreviation_fips = db.Column(db.String(5), db.ForeignKey('country.abbreviation_fips', ondelete='CASCADE'))

    class Preference(db.Model):
        __tablename__= 'preference'
        id = db.Column(db.Integer(), primary_key=True)

    class Position(db.Model):
        __tablename__='position'
        name = db.Column(db.String(100), nullable=False, primary_key=True)

    class Education(db.Model):
        __tablename__ = 'education'
        id = db.Column(db.Integer, primary_key=True)
        user_id= db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
        description= db.Column(db.String(1000), nullable=True, server_default='Write a short description of your education.')
        #degree = db.Column(db.String(10))
        #name = db.Column(db.String(100))
        #graduation_date = db.Column(db.Date)

    class Experience(db.Model):
        __tablename__ = 'experience'
        id = db.Column(db.Integer, primary_key=True)
        user_id= db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
        description= db.Column(db.String(1000), nullable=True, server_default='Write a short description of your experience.')

    class UserHasEducation(db.Model):
        __tablename__ = 'user_has_education'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
        education_id = db.Column(db.Integer, db.ForeignKey('education.id', ondelete='CASCADE'))

    class PI(db.Model):
        __tablename__ = 'pi'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)
        surname = db.Column(db.String(50), nullable=False)
        group_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))

    class Institution(db.Model):
        __tablename__ = 'institution'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False )
        link= db.Column(db.String(100), nullable=False)
        city= db.Column(db.String(50), nullable=False)

    class InstitutionHasGroup(db.Model):
        __tablename__ = 'institution_has_group'
        id = db.Column(db.Integer(), primary_key=True)
        #Group_id
        user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
        institution_id = db.Column(db.Integer, db.ForeignKey('institution.id', ondelete='CASCADE'))



    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User, RoleClass=Role, PositionClass=Position, UserHasEducationClass = UserHasEducation, PIClass = PI, InstitutionClass = Institution, EducationClass = Education, ExperienceClass= Experience)

    # Create all database tables
    db.create_all()


    #file_name = "static/database_initialization/GEODATASOURCE-COUNTRY.TXT"
    #df = pandas.read_csv(file_name)
    #df.to_sql(con=db, index_label='id', name=country, if_exists='replace')


    # To delete
    #city = City(name="Barcelona")
    #city2= City(name="Honolulu")
    #db.session.add(city)
    #db.session.add(city2)
    #db.session.commit()
    if not Position.query.filter(Position.name == 'Bioinformatician').first():
       pos1 = Position(name = "Bioinformatician")
       pos2 = Position(name ="Lab technician")
       db.session.add(pos1)
       db.session.add(pos2)
       db.session.commit()


    #Create 'member@example.com' user with no roles
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(
            email='member@example.com',
            email_confirmed_at=datetime.datetime.utcnow(),
            password=user_manager.hash_password('Password1'),
            gender = "F"

        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()

    # # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    # if not User.query.filter(User.email == 'admin@example.com').first():
    #     user = User(
    #         email='admin@example.com',
    #         email_confirmed_at=datetime.datetime.utcnow(),
    #         password=user_manager.hash_password('Password1'),
    #     )
    #     db.session.add(user)
    #     db.session.commit()


    if not Role.query.filter(Role.name == 'Applicant').first():
        role = Role (name = "Applicant")
        role2 = Role( name ="Group")
        db.session.add(role)
        db.session.add(role2)
        db.session.commit()

    # The Home page is accessible to anyone

    # Selects which home page to use. If the user is logged in then it checks if
    # it is an applicant or a group and shows the right view accordingly.
    @app.route('/')
    def home_page():
        role_name ="Guest"
        if current_user is None:
            return render_template("/home_page.html")

        if not current_user.is_authenticated:
                return render_template("/home_page.html")
        else:
                role_id = UserRoles.query.filter_by( user_id = current_user.id).first().role_id
                role_name = Role.query.filter_by( id = role_id).first().name
                if role_name == "Applicant":
                    matches = Position.query.order_by(Position.name).all()
                    return render_template("/home_page_applicant.html",matches=matches, role=role_name)
                elif role_name == "Group":
                    return render_template("/home_page_group.html",role=role_name)

    def who():
      return render_template("/who.html")
    app.add_url_rule('/who', 'who', who)

    def why():
      return render_template("/why.html")
    app.add_url_rule('/why', 'why', why)

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

    def add_position():
        return render_template("/flask_user/add_position.html")
    app.add_url_rule('/add_position', 'add_position', add_position)

    return app

# Start development web server
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

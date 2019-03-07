# Installation instructions

## Flask User steps done

[Documentation](https://flask-user.readthedocs.io/en/latest/basic_app.html)

#### Create virtual enviroment

```bash
python3 -m venv venv
```

### activate

. venv/bin/activate


### Install Flask-User
if needed {
  pip install --upgrade pip
  pip install --upgrade setuptools
  pip install Flask-login
  pip install SQLAlchemy
}
#pip install Flask-User
pip install "Flask-User<0.7"


### RUN
export FLASK_APP=app
export FLASK_ENV=development
flask run

# If error[48]
sudo lsof -i:5000
sudo kill pid(Second column)

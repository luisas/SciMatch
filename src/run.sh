export FLASK_APP=app
export FLASK_ENV=development
pip install --upgrade pip
pip install --upgrade setuptools
pip install flask_babelex
pip install cryptography
pip install "Flask-User<0.7"
pip install mysqlclient
flask run

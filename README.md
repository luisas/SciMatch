# SciMatch

## Documentation

# Getting started

### Step 1

```
cd app
```
and then run manually all the commands in activate.sh

### Step 2: Set DB (only when updated to new mySQL version)

Create DB called scimatch
```
mysql -p
create database scimatch
```
in app/__init__.py

change
```
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://luisasantus:password@localhost/scimatch?charset=utf8'
```
with your username (instead of luisasantus ) and psw(instead of password)!!


### Step 3
```
cd ..
bash run.sh
```

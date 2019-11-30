# CS 425 Course Project

## I. Preparation and Installation

### 1.1. Software

Make sure you are on **Ubuntu 18.04** to develop and test.

Execute the following commands to install necessary packages:

```bash
sudo apt update
sudo apt install build-essential python3 python3-dev python3-distutils libssl-dev
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; sudo -H python3 get-pip.py
```

### 1.2. Application

(optional) Install virtualenvwrapper for easy management 

```bash
sudo -H pip install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv cs425
```

Install requirement.txt

```bash
pip install -r requirements.txt
```

### 3. Database

We are using MySQL, and import an SQL file which includes database, table
creations and initial data importing.
**Change the path in "Create Table.sql" as needed**.
Most of the data are created by Python under `util_scripts`.

```bash
sudo apt install libmysqlclient-dev mysql-server
# Create database user
sudo mysql
```

```sql
CREATE USER 'cs425proj'@'localhost' IDENTIFIED BY 'proj@CS425';
GRANT ALL PRIVILEGES ON *.* TO 'cs425proj'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# Login again with the new user cs425proj
mysql -u cs425proj -p
# Import "Create Table.sql"  to initialize databse and import initial data
mysql -u cs425proj -p < "Create Table.sql"
```

```sql
CREATE DATABASE cs425projdb;
use cs425projdb
```
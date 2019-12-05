# CS 425 Course Project

## I. Preparation and Installation

### 1.1. Software

Make sure you are on **Ubuntu 18.04** to develop and test.

Execute the following commands to install necessary packages:

```bash
sudo apt update
sudo apt install build-essential python3 python3-dev python3-distutils libssl-dev
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; sudo -H python3 get-pip.py

git clone https://github.com/SiyuSuzyZhang/2019FallCS425.git
```

### 1.2. Database

We are using MySQL, and import an SQL file which includes database, table
creations and initial data importing.
**Change the path in "Create Table.sql" as needed**.
Most of the data are created by Python under `util_scripts`.

```bash
wget -c https://repo.mysql.com//mysql-apt-config_0.8.14-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.14-1_all.deb 
# If using WSL, Select mysql-5.7 first
sudo apt update
sudo apt install mysql-server
# Now select mysql-8.0
sudo dpkg -i mysql-apt-config_0.8.14-1_all.deb 
sudo apt update
sudo apt install mysql-server

sudo apt install libmysqlclient-dev
sudo vi /etc/init.d/mysql
# (search for a line ". /usr/share/mysql/mysql-helpers" and change it to
# ". /usr/share/mysql-8.0/mysql-helpers")
sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf
# add at the end
# secure_file_priv = ""
sudo service mysql start
# Create database user
sudo mysql -u root -p
```

```sql
CREATE USER 'cs425proj'@'localhost' IDENTIFIED BY 'proj@CS425';
GRANT ALL PRIVILEGES ON *.* TO 'cs425proj'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# Import "Create Table.sql"  to initialize databse and import initial data
mysql -u cs425proj -p < "sqls/Create Table.sql"
```

### 1.3. Application

(optional) Install virtualenvwrapper for easy management 

```bash
sudo -H pip install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv cs425
workon cs425

```

Install requirement.txt

```bash
pip install -r requirements.txt
```


## II. Start your application

```bash
# under cs425proj
# first time only
~/.virtualenvs/cs425/bin/python manage.py migrate
# start mysql
sudo service mysql start
# start server
~/.virtualenvs/cs425/bin/python manage.py runserver_plus
```

Open local browser and go to `localhost:8000`

To test, you can use a test user

```
First Name: Test
Last Name: User
Account No: 1234567890
Username: testuser
Password: 123456
Card Number: 1111222233334444 for low credit/balance test
             1111222233330001 has high credit/balance
```

## III. Organization

### 3.1 The bad: all the functions are in the same file: views

### 3.2 Showcase page

```
URL: /
INFO: Show how a store webfront would be like
ENTRY: views.index(request)
```

### 3.3 Shopping

```
URL: 1  /shop/<siteid>/
     2  ............../page-<page>
     3  ............../ptype/<ptype>/
     4  ............................/page-<page>
     5  ............../manu/<manu>/
     6  ........................../<mapage-<page>
     7  ............../package/<pack>/
     8  ............................./page-<page>
INFO: List products with different conditions
      1,2 shows all products with pagination, 1 is equal to 2 when page is 1
      3,4 shows all products of a type
      5,6 shows all products from a manufacturer
      7,8 shows all products in a package
ENTRY: views.shop(request, siteid=10001, ptype=0, manu=0, pack=0, page=1)
```

```
URL: 1  /shop/<siteid>/addToCard (!don't open directly)
     2  ............../cart
INFO: 1. An entry for shop page ajax sending POST request to update cart
      2. Show cart info
ENTRY: views.cart(request, siteid=10001)
```

```
URL: /shop/<siteid>/checkout/
INFO: Show checkout page
ENTRY: views.checkout(request, siteid=10001)
```

```
URL: /shop/<siteid>/doCheckout/ (!don't open directly)
INFO: POST requests are sent from checkout page, to do checkout action
      If success, page will jump to show order detail
ENTRY: views.doCheckout(request, siteid=10001)
```

```
URL: /shop/<siteid>/login/
INFO: Show login page, have a siteid because we simulate a user visiting a store
      or store website
ENTRY: views.login(request, siteid=10001)
```

```
URL: /shop/<siteid>/doLoginOrSignup/ (!don't open directly)
INFO: POST requests are sent from login page, to do login or signup
ENTRY: views.doLoginOrSignup(request, siteid=10001)
```

### 3.4 Order Detail

```
URL: 1  /order/<orderid>/
     2  ................/<paycard>
INFO: Both will display an order.
      1 will show order if logged in and you have the order
      2 will show order if orderid and paycard match
ENTRY: views.orderdetail(request, orderid=None, paycard=None)
```

### 3.5 Account

```
URL: /account/
INFO: Show account information. It also receive POST request to modify info
ENTRY: views.account(request)
```

```
URL: 1  /account/orders/
     2  .............../page-<page>
INFO: show order list with pagination
ENTRY: views.orderlist(request, page=1)
```

```
URL: /account/bills/
INFO: Show monthly bills
ENTRY: views.bills(request)
```


```
URL: /account/checkout_confirm_account (!don't open directly)
INFO: login account when on the checkout page, receiving POST
ENTRY: views.checkout_confirm_account(request)
```

```
URL: /logout/
INFO: logout, remove loggedin flag in session data
ENTRY: views.logout(request)
```

### 3.6 Report

```
URL: /report/
INFO: Show Sale by state donut graph report
ENTRY: views.report(request)
```

```
URL: /report/report1/
INFO: Show Daily sale report
ENTRY: views.report1(request)
```

```
URL: /report/report2/
INFO: Show montly change sale report
ENTRY: views.report2(request)
```

```
URL: /report/lowstock/
INFO: Show low stock (<10) items
ENTRY: views.report_low_stock(request)
```

```
URL: /report/restock_100/ (!don't open directly)
INFO: restock requested items by 100 via POST from lowstock page
ENTRY: views.restock_100(request)
```
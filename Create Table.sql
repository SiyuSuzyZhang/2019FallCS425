CREATE TABLE Category 
(Product_Type char(50) NOT NULL, 
Manufactor char(50) NOT NULL, 
Package char(50) NOT NULL, 
Product_ID int(20) NOT NULL, 
PRIMARY KEY(Product_Type, Manufactor, Package, Product_ID), 
FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID));

CREATE TABLE Product 
(Product_ID int(20) NOT NULL, 
Product_Name char(50) NOT NULL, 
Product_Price int(10) NOT NULL, 
PRIMARY KEY(Product_ID));

CREATE TABLE Product_Order
(Product_ID int(20) NOT NULL, 
Order_ID int(20) NOT NULL,
PRIMARY KEY(Product_ID, Order_ID),
FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID),
FOREIGN KEY (Order_ID) REFERENCES Order1(Order_ID));

CREATE TABLE Inventory
(Product_ID int(20) NOT NULL, 
Site_ID int(20) NOT NULL,
Product_Amount int(10),
PRIMARY KEY(Product_ID, Site_ID),
FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID),
FOREIGN KEY (Site_ID) REFERENCES Stock(Site_ID));

CREATE TABLE Stock 
(Site_ID int(20) NOT NULL, 
Stock_Type char(20) NOT NULL, 
Product_Amount int(10), 
Address_ID int(10) NOT NULL,
PRIMARY KEY(Site_ID),
FOREIGN KEY (Address_ID) REFERENCES Address(Address_ID));

CREATE TABLE Address
(Address_ID int(10) NOT NULL,
Address_Line_1 char(30) NOT NULL,
Address_Line_2 char(30),
City char(10) NOT NULL,
State char(10) NOT NULL,
Zipcode int(10) NOT NULL,
PRIMARY KEY(Address_ID));



CREATE TABLE Order1
(Order_ID int(20) NOT NULL, 
Order_Price int(20) NOT NULL,
Order_Type char(20) NOT NULL,  
Address_ID int(10) NOT NULL,
Customer_ID int(10),
Card_Num int(20) NOT NULL,
PRIMARY KEY(Order_ID),
FOREIGN KEY (Address_ID) REFERENCES Address(Address_ID),
FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
FOREIGN KEY (Card_Num) REFERENCES Card(Card_Num));

CREATE TABLE Shippment
(Tracking_Num int(20),
ShipperName char(20) NOT NULL,
Order_ID int(20) NOT NULL,
PRIMARY KEY(Tracking_Num),
FOREIGN KEY (Order_ID) REFERENCES Order1(Order_ID));

CREATE TABLE Address_Cumtomer
(Address_ID int(10) NOT NULL,
Customer_ID int(10),
PRIMARY KEY(Address_ID, Customer_ID),
FOREIGN KEY (Address_ID) REFERENCES Address(Address_ID),
FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID));

CREATE TABLE Customer
(Customer_ID int(10),
Firstname char(10),
Lastname char(10),
Phone_num int(15),
PRIMARY KEY(Customer_ID));


CREATE TABLE Account
(Account_Num int(10),
Username char(10),
Password char(10),
Email char(20),
Customer_ID int(10),
PRIMARY KEY(Account_Num),
FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID));

CREATE TABLE Customer_Card
(Customer_ID int(10),
Card_Num int(20) NOT NULL,
PRIMARY KEY(Customer_ID, Card_Num),
FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
FOREIGN KEY (Card_Num) REFERENCES Card(Card_Num));

CREATE TABLE Card
(Card_Num int(20) NOT NULL,
Card_Type char(10) NOT NULL,
Creditline int (15),
PRIMARY KEY(Card_Num));

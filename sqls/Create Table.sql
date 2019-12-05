DROP DATABASE IF EXISTS cs425projdb;

CREATE DATABASE cs425projdb;

use cs425projdb;

CREATE TABLE ProductType
(
    TypeID INT(5) NOT NULL,
    TypeName VARCHAR(20) NOT NULL,
    PRIMARY KEY(TypeID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/producttype_dat.csv' INTO TABLE ProductType FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';

CREATE TABLE Manufacturer
(
    ManufacturerID INT(5) NOT NULL,
    ManufacturerName VARCHAR(20) NOT NULL,
    PRIMARY KEY(ManufacturerID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/manufacturer_dat.csv' INTO TABLE Manufacturer FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';

CREATE TABLE Package
(
    PackageID INT(5) NOT NULL,
    PackageName VARCHAR(128) NOT NULL,
    PRIMARY KEY(PackageID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/package_dat.csv' INTO TABLE Package FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';

CREATE TABLE Product 
(
    ProductID INT(10) NOT NULL, 
    ProductName VARCHAR(50) NOT NULL, 
    ProductPrice INT(10) NOT NULL, 
    ManufacturerID INT(5) NOT NULL,
    PRIMARY KEY(ProductID),
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturer(ManufacturerID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/product_dat.csv' INTO TABLE Product FIELDS TERMINATED BY ',';

CREATE TABLE Address
(
    AddressID INT(10) NOT NULL AUTO_INCREMENT,
    StreetNumber VARCHAR(10) NOT NULL,
    Street VARCHAR(64) NOT NULL,
    Line2 VARCHAR(64) DEFAULT '',
    City VARCHAR(32) NOT NULL,
    State VARCHAR(10) NOT NULL,
    Zipcode VARCHAR(6) NOT NULL,
    PRIMARY KEY(AddressID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/address_dat.csv' INTO TABLE Address FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';

CREATE TABLE Stock
(
    SiteID INT(5) NOT NULL AUTO_INCREMENT, 
    StockType VARCHAR(10) NOT NULL, 
    AddressID INT(10) DEFAULT NULL,
    PRIMARY KEY (SiteID),
    FOREIGN KEY (AddressID) REFERENCES Address(AddressID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/site_dat.csv' INTO TABLE Stock FIELDS TERMINATED BY ',';


CREATE TABLE Customer
(
    CustomerID INT(10) NOT NULL AUTO_INCREMENT,
    FirstName VARCHAR(10) NOT NULL,
    LastName VARCHAR(10) NOT NULL,
    PhoneNumber VARCHAR(15),
    AccountNumber CHAR(10) NOT NULL UNIQUE,
    Username VARCHAR(32) NOT NULL UNIQUE,
    Password VARCHAR(64) NOT NULL,
    Email VARCHAR(64),
    PRIMARY KEY(CustomerID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/customer_dat.csv' INTO TABLE Customer FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n';

CREATE TABLE Card
(
    CardNum CHAR(16) NOT NULL,
    CardType VARCHAR(8) NOT NULL,
    Credit INT (15),
    PRIMARY KEY(CardNum)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/card_dat.csv' INTO TABLE Card FIELDS TERMINATED BY ',';

CREATE TABLE Inventory
(
    ProductID INT(10) NOT NULL AUTO_INCREMENT, 
    SiteID INT(10) NOT NULL,
    ProductAmount INT(10) NOT NULL DEFAULT 0,
    PRIMARY KEY(ProductID, SiteID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (SiteID) REFERENCES Stock(SiteID),
    CONSTRAINT chk_amount CHECK(ProductAmount >= 0)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/inventory_dat.csv' INTO TABLE Inventory FIELDS TERMINATED BY ',';

CREATE TABLE CusOrder
(
    OrderID INT(20) NOT NULL AUTO_INCREMENT, 
    OrderPrice INT(20) NOT NULL,
    SiteID INT(10) NOT NULL,

    TrackingNumber CHAR(8) DEFAULT NULL,
    ShipperName VARCHAR(20) DEFAULT NULL,
    
    CustomerID INT(10) DEFAULT NULL,
    
    AddressID INT(10) DEFAULT NULL,
    
    CardNum CHAR(16) DEFAULT NULL,
    
    OrderTime DATETIME NOT NULL,
    FOREIGN KEY (SiteID) REFERENCES Stock(SiteID),
    FOREIGN KEY (AddressID) REFERENCES Address(AddressID),
    FOREIGN KEY (CardNum) REFERENCES Card(CardNum),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    PRIMARY KEY(OrderID),
    CONSTRAINT chk_frequent CHECK(CustomerID is NOT NULL or CardNum is NOT NULL)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/cusorder_dat.csv' INTO TABLE CusOrder FIELDS TERMINATED BY ',';

CREATE TABLE OrderFor
(
    OrderID INT(10) NOT NULL,
    ProductID INT(10) NOT NULL, 
    Amount INT(10) NOT NULL,
    PRIMARY KEY(ProductID, OrderID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (OrderID) REFERENCES CusOrder(OrderID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/orderfor_dat.csv' INTO TABLE OrderFor FIELDS TERMINATED BY ',';

CREATE TABLE ProductTypeR
(
    ProductID INT(10) NOT NULL,
    TypeID INT(5) NOT NULL,
    PRIMARY KEY (ProductID, TypeID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (TypeID) REFERENCES ProductType(TypeID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/producttyper_dat.csv' INTO TABLE ProductTypeR FIELDS TERMINATED BY ',';

CREATE TABLE PackageProduct
(
    PackageID INT(5) NOT NULL,
    ProductID INT(10) NOT NULL,
    PRIMARY KEY (PackageID, ProductID),
    FOREIGN KEY (PackageID) REFERENCES Package(PackageID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/packageproduct_dat.csv' INTO TABLE PackageProduct FIELDS TERMINATED BY ',';


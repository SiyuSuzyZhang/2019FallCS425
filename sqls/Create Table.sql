DROP DATABASE cs425projdb;

CREATE DATABASE cs425projdb;

use cs425projdb;

CREATE TABLE ProductType
(
    TypeID INT(5) NOT NULL,
    TypeName VARCHAR(20) NOT NULL,
    PRIMARY KEY(TypeID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/producttype_dat.csv' INTO TABLE ProductType FIELDS TERMINATED BY ',';

CREATE TABLE Manufacturer
(
    ManufacturerID INT(5) NOT NULL,
    ManufacturerName VARCHAR(20) NOT NULL,
    PRIMARY KEY(ManufacturerID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/manufacturer_dat.csv' INTO TABLE Manufacturer FIELDS TERMINATED BY ',';

CREATE TABLE Package
(
    PackageID INT(5) NOT NULL,
    PackageName VARCHAR(128) NOT NULL,
    PRIMARY KEY(PackageID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/package_dat.csv' INTO TABLE Package FIELDS TERMINATED BY ',';

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
    AddressID INT(10) NOT NULL,
    StreetNumber VARCHAR(10) NOT NULL,
    Street VARCHAR(64) NOT NULL,
    Line2 VARCHAR(64) DEFAULT NULL,
    City VARCHAR(32) NOT NULL,
    State VARCHAR(10) NOT NULL,
    Zipcode VARCHAR(6) NOT NULL,
    PRIMARY KEY(AddressID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/address_dat.csv' INTO TABLE Address FIELDS TERMINATED BY ',';

CREATE TABLE Stock
(
    SiteID INT(5) NOT NULL, 
    StockType VARCHAR(10) NOT NULL, 
    AddressID INT(10) DEFAULT NULL,
    PRIMARY KEY (SiteID),
    FOREIGN KEY (AddressID) REFERENCES Address(AddressID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/site_dat.csv' INTO TABLE Stock FIELDS TERMINATED BY ',';


CREATE TABLE Customer
(
    CustomerID INT(10) NOT NULL,
    FirstName VARCHAR(10) NOT NULL,
    LastName VARCHAR(10) NOT NULL,
    PhoneNumber VARCHAR(15),
    AccountNumber CHAR(10) NOT NULL UNIQUE,
    Username VARCHAR(32) NOT NULL,
    Password VARCHAR(64) NOT NULL,
    Email VARCHAR(64),
    PRIMARY KEY(CustomerID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/customer_dat.csv' INTO TABLE Customer FIELDS TERMINATED BY ',';

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
    ProductID INT(10) NOT NULL, 
    SiteID INT(10) NOT NULL,
    ProductAmount INT(10) NOT NULL DEFAULT 0,
    PRIMARY KEY(ProductID, SiteID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    FOREIGN KEY (SiteID) REFERENCES Stock(SiteID)
);

LOAD DATA INFILE '/home/siyu/2019FallCS425/initial_data/inventory_dat.csv' INTO TABLE Inventory FIELDS TERMINATED BY ',';

CREATE TABLE CusOrder
(
    OrderID INT(20) NOT NULL, 
    OrderPrice INT(20) NOT NULL,
    SiteID INT(10) NOT NULL,

    TrackingNumber CHAR(8) NOT NULL UNIQUE,
    ShipperName VARCHAR(20) NOT NULL,
    
    CustomerID INT(10) DEFAULT NULL,
    
    AddressID INT(10) NOT NULL,
    
    CardNum CHAR(16) NOT NULL,
    
    OrderTime DATETIME NOT NULL,
    FOREIGN KEY (SiteID) REFERENCES Stock(SiteID),
    FOREIGN KEY (AddressID) REFERENCES Address(AddressID),
    FOREIGN KEY (CardNum) REFERENCES Card(CardNum),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    PRIMARY KEY(OrderID)
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


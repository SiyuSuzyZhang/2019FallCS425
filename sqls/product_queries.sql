# Genernal

-- Query all product types
SELECT * FROM  ProductType ORDER BY TypeName;

-- Query all packages
SELECT * FROM Package ORDER BY PackageName;

-- Query all stock sites
SELECT SiteID, StockType, City, State
FROM Stock
LEFT JOIN Address USING(AddressID);

-- Query all manufacturers and number of products they manufacture
SELECT ManufacturerID, ManufacturerName, Count(*)
FROM Manufacturer
JOIN Product USING(ManufacturerID)
GROUP BY ManufacturerID
ORDER BY ManufacturerName;

-- Query products sales across all time, select top 12 as featured products
SELECT ProductID, ProductName, ProductPrice, SUM(OrderFor.amount) as sales
FROM Product
JOIN OrderFor USING(ProductID)
GROUP BY ProductID
ORDER BY sales DESC
LIMIT 12;

-- Query product average sale per order across all time, top 6 as recommended
SELECT ProductID, ProductName, ProductPrice, AVG(OrderFor.amount) as sales
FROM Product
JOIN OrderFor USING(ProductID)
GROUP BY ProductID
ORDER BY sales DESC
LIMIT 6;

-- Query top 5 selling product types, for featured product types
SELECT TypeID, TypeName, SUM(amount) as sales
FROM ProductType
JOIN ProductTypeR Using(TypeID)
JOIN Product USING(ProductID)
JOIN OrderFor USING(ProductID)
GROUP BY TypeID
ORDER BY sales DESC
LIMIT 5;

-- Find top 4 selling products in a certain type
SELECT ProductID, ProductName, ProductPrice, SUM(OrderFor.amount) as sales
FROM Product
JOIN OrderFor USING(ProductID)
JOIN ProductTypeR USING(ProductID)
WHERE TypeID = 10015
GROUP BY ProductID
ORDER BY sales DESC
LIMIT 4;

# Shop Page
-- Query all products and their inventory given a siteid
SELECT ProductID, ProductName, ProductPrice, ProductAmount
FROM Product
LEFT JOIN Inventory USING(ProductID)
WHERE Inventory.SiteID = 10001
LIMIT 10 15;
-- A certain type
SELECT ProductID, ProductName, ProductPrice, ProductAmount
FROM Product
LEFT JOIN ProductTypeR USING(ProductID)
LEFT JOIN Inventory USING(ProductID)
WHERE TypeID = 10001 AND Inventory.SiteID = 10001
LIMIT 10, 15
-- A certain manufacturer
SELECT ProductID, ProductName, ProductPrice, ProductAmount
FROM Product
LEFT JOIN Inventory USING(ProductID)
WHERE ManufacturerID = 10001 AND Inventory.SiteID = 10001
LIMIT 10, 15
-- A certain package
SELECT ProductID, ProductName, ProductPrice, ProductAmount
FROM Product
JOIN PackageProduct USING(ProductID)
LEFT JOIN Inventory USING(ProductID)
WHERE PackageID = 10001 AND Inventory.SiteID = 10001
LIMIT 10, 15

-- For the purpose of pagination, we need to get the number of products first
SELECT count(*) FROM Product;
-- A certain type
SELECT count(*) 
FROM Product 
LEFT JOIN ProductTypeR 
USING(ProductID) 
WHERE TypeID = 10001;
-- A certain manufacturer
SELECT count(*) 
FROM Product 
WHERE ManufacturerID = 10001;
-- A certain package
SELECT count(*) 
FROM Product 
JOIN PackageProduct USING (ProductID)
WHERE PackageID = 10001;


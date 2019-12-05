# Cart/Checkout
-- Show products in cart/checkout
SELECT ProductID, ProductName, ProductPrice, ProductAmount
FROM Product
LEFT JOIN Inventory USING(ProductID)
WHERE Inventory.SiteID = 10001 AND ProductID in (100001,100002,100003);

# When placing order, the followings are executed in one transaction
-- Insert address if not exist
SELECT AddressID
FROM Address
WHERE StreetNumber = '{}' AND Street = '{}' AND Line2 = '{}'
    AND City = '{}' AND State = '{}' AND Zipcode = '{}';

INSERT INTO Address
(StreetNumber, Street, Line2, City, State, Zipcode)
VALUES
('{}', '{}', '{}', '{}', '{}', '{}');

-- In a loop, decrease inventory. This might fail if ProductAmount becomes negative
-- thanks to check. When it fails, the transaction will abort
UPDATE Inventory
SET ProductAmount = ProductAmount - {}
WHERE ProductID = {} AND SiteID = {};

-- Create CusOrder after amount has decreased
INSERT INTO CusOrder
(OrderPrice, SiteID, TrackingNumber, ShipperName, CustomerID, AddressID, CardNum, OrderTime)
VALUES
({},{},{},{},{},{},{},'{}');

-- Build OrderFor relation
INSERT INTO OrderFor
VALUES
({},{},{});

# Query all orders
-- get total numbers
SELECT count(*)
FROM CusOrder
WHERE CustomerID = {}
ORDER BY OrderTime DESC

-- get orders
SELECT *
FROM CusOrder
WHERE CustomerID = {}
ORDER BY OrderTime DESC
LIMIT {}, {}

-- query order by orderID and CustomerID
SELECT *
FROM CusOrder
WHERE OrderID = {} AND CustomerID = {}
-- query order by orderID and CardNum
SELECT *
FROM CusOrder
WHERE OrderID = {} AND CardNum = {}
-- query store address to show an address for in-store order
SELECT Stock.AddressID, StreetNumber, Street, Line2, City, State, Zipcode
FROM Address
JOIN Stock
WHERE SiteID = {}
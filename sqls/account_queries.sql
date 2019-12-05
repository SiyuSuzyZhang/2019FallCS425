-- Sign up as frequent customer
INSERT INTO Customer
(FirstName, LastName, AccountNumber, Username, Password)
VALUES
('{}', '{}', '{}', '{}', '{}')

-- Login in using username and password
SELECT *
FROM Customer
WHERE Username = '{}' AND Password = '{}';

-- Login in using account number (simulating in-store)
SELECT *
FROM Customer
WHERE AccountNumber = {};

-- Update multiple in a transaction
UPDATE Customer
SET {} = '{}'
WHERE CustomerID = {}

-- Show montly bills
SELECT YEAR(OrderTime) as OrderYear, MONTH(OrderTime) as OrderMonth, SUM(OrderPrice) as Bill
FROM CusOrder
WHERE CustomerID = {} AND CardNum IS NULL
GROUP BY OrderYear, OrderMonth
ORDER BY OrderYear DESC, OrderMonth DESC;
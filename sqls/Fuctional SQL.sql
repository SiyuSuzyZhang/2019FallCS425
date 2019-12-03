# Queries

## Index page

-- Query all product types
SELECT * FROM  ProductType ORDER BY TypeName;

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

-- Query all stock sites
SELECT SiteID, StockType, City, State
FROM Stock
LEFT JOIN Address USING(AddressID);

### Sign in

--sql
	--input username
	--input password

	select user_id from account
		where username = 'input_username' 
		and password = 'input_password';

### Sign up
--sql
	--auto generate auto_user_id;
	--input information;	
	--examine the same username
	select UserName from Account
		where UserName = 'input username';
	select Email from Account
		where Email = 'input email';

	--if username is unique, then create a new account.
	insert into customers 
	values (	'auto_Customer_ID',
		'input_Firstname',
		'input_Lastname',
		'Phone_num' 		
		);

### Edit information
--sql
	update table customers
	set Firstname = 'input_first_name',	 
	     Lastname = 'input_last_name',
	     Phone_num = 'input_phone_number',
	where user_id = 'the current userid';

### Set payment method
--sql

	insert into Card
	values(	'Caed-Num',
		'Card_Type',
		'Creditline');

### Check creditline
--sql
	select Creditline from Card
		where Card_num = 'input_card_num';

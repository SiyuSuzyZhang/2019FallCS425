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

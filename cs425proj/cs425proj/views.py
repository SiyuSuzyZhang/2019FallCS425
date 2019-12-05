from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import math, json

def get_stock_sites(context=None):
    if context is None:
        context = {}
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SiteID, StockType, City, State
            FROM Stock
            LEFT JOIN Address USING(AddressID)
            """)
        rows = cursor.fetchall()
    sites = [(row[0], row[1].strip().capitalize() if row[1].strip() != 'warehouse' else 'Online', row[2], row[3]) for row in rows]
    context['sites'] = sites
    return context

def get_all_product_types(context=None):
    if context is None:
        context = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ProductType ORDER BY TypeName")
        rows = cursor.fetchall()
    productTypes = [(row[0], row[1].strip()) for row in rows]
    context['productTypes'] = productTypes
    return context

def get_all_packages(context=None):
    if context is None:
        context = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Package ORDER BY PackageName")
        rows = cursor.fetchall()
    packages = [(row[0], row[1].strip()) for row in rows]
    context['packages'] = packages
    return context

def get_all_manufacturers(context=None):
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT ManufacturerID, ManufacturerName, Count(*)
                FROM Manufacturer
                JOIN Product USING(ManufacturerID)
                GROUP BY ManufacturerID
                ORDER BY ManufacturerName""")
        rows = cursor.fetchall()
    manufacturers = [(row[0], row[1].strip(), row[2]) for row in rows]
    context['manufacturers'] = manufacturers
    return context


def index(request):
    context = {}
    context = get_all_product_types(context)
    context = get_all_manufacturers(context)
    context = get_all_packages(context)
    
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, SUM(OrderFor.amount) as sales
                FROM Product
                JOIN OrderFor USING(ProductID)
                GROUP BY ProductID
                ORDER BY sales DESC
                LIMIT 12""")
        rows = cursor.fetchall()
    featured_products = [(row[0], row[1].strip(), row[2]) for row in rows]

    
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, AVG(OrderFor.amount) as sales
                FROM Product
                JOIN OrderFor USING(ProductID)
                GROUP BY ProductID
                ORDER BY sales DESC
                LIMIT 6""")
        rows = cursor.fetchall()
    rec_products = [(row[0], row[1].strip(), row[2]) for row in rows]

    
    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT TypeID, TypeName, SUM(amount) as sales
                FROM ProductType
                JOIN ProductTypeR Using(TypeID)
                JOIN Product USING(ProductID)
                JOIN OrderFor USING(ProductID)
                GROUP BY TypeID
                ORDER BY sales DESC
                LIMIT 5""")
        rows = cursor.fetchall()
    top_types = [(row[0], row[1].strip(), row[2]) for row in rows]
    featured_types = []
    for feat_type in top_types:
        atype = {
            'id': feat_type[0],
            'name': feat_type[1],
        }
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, SUM(OrderFor.amount) as sales
                FROM Product
                JOIN OrderFor USING(ProductID)
                JOIN ProductTypeR USING(ProductID)
                WHERE TypeID = {}
                GROUP BY ProductID
                ORDER BY sales DESC
                LIMIT 4""".format(feat_type[0]))
            rows = cursor.fetchall()
        atype['prods'] = [(row[0], row[1].strip(), row[2]) for row in rows]
        featured_types.append(atype)

    context['featured_products'] = featured_products
    context['featured_types'] = featured_types
    context['rec_products_p1'] = rec_products[:3]
    context['rec_products_p2'] = rec_products[3:]
    context['siteloc'] = 'Showcase'
    context = get_stock_sites(context)
    return render(request, 'cs425proj/index.html', context)

def clear_cart(session, siteid):
    session['cart'] = {
        'siteid': siteid,
        'prods': {},
        'total': 0
    }

def check_cart_switch(session, siteid):
    if session.has_key('cart'):
        if session['cart']['siteid'] != siteid:
            session['cart'] = {
                'siteid': siteid,
                'prods': {},
                'total': 0
            }
    else:
        session['cart'] = {
            'siteid': siteid,
            'prods': {},
            'total': 0
        }
    # also clean up prods that have zero quantities
    mycart = session['cart']
    prodids = list(mycart['prods'].keys())
    for prodid in prodids:
        v = mycart['prods'][prodid]
        if v == 0:
            del mycart['prods'][prodid]
    session['cart'] = mycart

def shop(request, siteid=10001, ptype=0, manu=0, pack=0, page=1):
    session = request.session
    check_cart_switch(session, siteid)
    items_in_cart = session['cart']['total']

    siteid = int(siteid)
    ptype = int(ptype)
    manu = int(manu)
    page = int(page)
    pack = int(pack)
    context = get_stock_sites()
    context = get_all_product_types(context)
    context = get_all_manufacturers(context)
    context = get_all_packages(context)
    items_per_page = 18
    if ptype ==0 and manu == 0 and pack == 0:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM Product")
            anum = cursor.fetchone()
        num_prods = anum[0]
        totalpages = math.ceil(1.0*num_prods/items_per_page)
        if page <= 0 or page > totalpages:
            page = 1
        start_index = (page-1)*items_per_page

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, ProductAmount
                FROM Product
                LEFT JOIN Inventory USING(ProductID)
                WHERE Inventory.SiteID = {}
                LIMIT {}, {}""".format(siteid, start_index, items_per_page))
            rows = cursor.fetchall()
        products = [(row[0], row[1].strip(), row[2], row[3]) for row in rows]
    elif ptype != 0:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT count(*) 
                    FROM Product 
                    LEFT JOIN ProductTypeR 
                    USING(ProductID) 
                    WHERE TypeID = {}""".format(ptype))
            anum = cursor.fetchone()
        num_prods = anum[0]
        totalpages = math.ceil(1.0*num_prods/items_per_page)
        if page <= 0 or page > totalpages:
            page = 1
        start_index = (page-1)*items_per_page
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, ProductAmount
                FROM Product
                LEFT JOIN ProductTypeR USING(ProductID)
                LEFT JOIN Inventory USING(ProductID)
                WHERE TypeID = {} AND Inventory.SiteID = {}
                LIMIT {}, {}""".format(ptype, siteid, start_index, items_per_page))
            rows = cursor.fetchall()
        products = [(row[0], row[1].strip(), row[2], row[3]) for row in rows]
        context['bytype'] = ptype
    elif manu != 0:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT count(*) 
                    FROM Product 
                    WHERE ManufacturerID = {}""".format(manu))
            anum = cursor.fetchone()
        num_prods = anum[0]
        totalpages = math.ceil(1.0*num_prods/items_per_page)
        if page <= 0 or page > totalpages:
            page = 1
        start_index = (page-1)*items_per_page
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, ProductAmount
                FROM Product
                LEFT JOIN Inventory USING(ProductID)
                WHERE ManufacturerID = {} AND Inventory.SiteID = {}
                LIMIT {}, {}""".format(manu, siteid, start_index, items_per_page))
            rows = cursor.fetchall()
        products = [(row[0], row[1].strip(), row[2], row[3]) for row in rows]
        context['bymanu'] = manu
    elif pack != 0:
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT count(*) 
                    FROM Product 
                    JOIN PackageProduct USING (ProductID)
                    WHERE PackageID = {}""".format(pack))
            anum = cursor.fetchone()
        num_prods = anum[0]
        totalpages = math.ceil(1.0*num_prods/items_per_page)
        if page <= 0 or page > totalpages:
            page = 1
        start_index = (page-1)*items_per_page
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ProductID, ProductName, ProductPrice, ProductAmount
                FROM Product
                JOIN PackageProduct USING(ProductID)
                LEFT JOIN Inventory USING(ProductID)
                WHERE PackageID = {} AND Inventory.SiteID = {}
                LIMIT {}, {}""".format(pack, siteid, start_index, items_per_page))
            rows = cursor.fetchall()
        products = [(row[0], row[1].strip(), row[2], row[3]) for row in rows]
        context['bypack'] = pack

    context['products'] = products

    cururl = '/shop/{}'.format(siteid)
    if ptype:
        cururl += '/ptype/{}'.format(ptype)
    elif manu:
        cururl += '/manu/{}'.format(manu)
    elif pack:
        cururl += '/package/{}'.format(pack)
    context['cururl'] = cururl
    context['items_in_cart'] = items_in_cart
    context['siteloc'] = 'Shop'
    context['shopat'] = int(siteid)
    context['prevpage'] = page-1
    context['curpage'] = page
    context['nextpage'] = page+1 if page + 1 <= totalpages else -1
    context['pages'] = list(range(1, totalpages+1))
    return render(request, 'cs425proj/index.html', context)

def checkout(request, siteid=10001):
    session = request.session
    check_cart_switch(session, siteid)
    if session['cart']['total'] == 0:
        return redirect('/shop/{}/'.format(siteid))
    context = {}
    context = get_stock_sites(context)
    mycart = session['cart']
    prod_in_cart = mycart['prods']
    prodids_in_cart = mycart['prods'].keys()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ProductID, ProductName, ProductPrice, ProductAmount
            FROM Product
            LEFT JOIN Inventory USING(ProductID)
            WHERE Inventory.SiteID = {} AND ProductID in ({})
            """.format(siteid, ",".join(prodids_in_cart)))
        rows = cursor.fetchall()
    show_carts = [(row[0], row[1].strip(), row[2], row[3], prod_in_cart[str(row[0])], row[2]*prod_in_cart[str(row[0])]) for row in rows]
    cart_total = 0
    for row in show_carts:
        cart_total += row[-1]
    context['items_in_cart'] = mycart['total']
    context['show_carts'] = show_carts
    context['cart_total'] = cart_total
    context['siteloc'] = 'Shop'
    context['subloc'] = 'Checkout'
    context['shopat'] = int(siteid)
    return render(request, 'cs425proj/checkout.html', context)

def scrambleAddress(shipping):
    try:
        all_states = ["Alabama","AL","Alaska","AK","Arizona","AZ","Arkansas","AR","California","CA","Colorado","CO","Connecticut","CT","Delaware","DE","Florida","FL","Georgia","GA","Hawaii","HI","Idaho","ID","Illinois","IL","Indiana","IN","Iowa","IA","Kansas","KS","Kentucky","KY","Louisiana","LA","Maine","ME","Maryland","MD","Massachusetts","MA","Michigan","MI","Minnesota","MN","Mississippi","MS","Missouri","MO","Montana","MT","Nebraska","NE","Nevada","NV","New Hampshire","NH","New Jersey","NJ","New Mexico","NM","New York","NY","North Carolina","NC","North Dakota","ND","Ohio","OH","Oklahoma","OK","Oregon","OR","Pennsylvania","PA","Rhode Island","RI","South Carolina","SC","South Dakota","SD","Tennessee","TN","Texas","TX","Utah","UT","Vermont","VT","Virginia","VA","Washington","WA","West Virginia","WV","Wisconsin","WI","Wyoming","WY"]
        address1 = shipping['address1'].strip()
        address2 = shipping['address2'].strip()
        city = shipping['city'].strip()
        state = shipping['state'].strip()
        if state not in all_states:
            return None
        zipcode = shipping['zipcode'].strip()
        street_no = int(address1.split(" ")[0])
        street_name = " ".join(address1.split(" ")[1:])
        if not(int(zipcode)>10000 and int(zipcode)<99999):
            return None
        return {
            'StreetNumber': street_no,
            'Street': street_name,
            'Line2': address2,
            'City': city,
            'State': state,
            'Zipcode': zipcode,
        }
    except:
        return None
@csrf_exempt
def doCheckout(request, siteid=10001):
    session = request.session
    siteid = int(siteid)
    if request.method == "POST":
        success = True
        info = "Something Wrong"
        now = datetime.now()
        try:
            if session.has_key('loggedin') and session['loggedin']:
                cusid = session['user']['CustomerID']
            else:
                cusid = 'NULL'
            post_data = request.POST.dict()
            checkout_type = post_data["type"]
            card = post_data["card"]
            card_credit = 0
            shipping = post_data["shipping"]

            good_address = scrambleAddress(post_data)
            if siteid == 10001 and good_address is None:
                e = "You need to input a valid shipping address for an online order"
                raise Exception(1001,e)
            
            # check card
            if checkout_type == "normal":
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT *
                        FROM Card
                        WHERE CardNum = '{}'""".format(card)
                    )
                    one = cursor.fetchone()
                if one is None:
                   raise Exception(1002, "Card not found")
                card_credit = one[2]
                card = "'{}'".format(card)
            else:
                card = 'NULL'
            mycart = session['cart']
            prod_in_cart = mycart['prods']
            prodids_in_cart = mycart['prods'].keys()
            cart_total = 0
            # get order total
            if len(prodids_in_cart) > 0:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT ProductID, ProductName, ProductPrice, ProductAmount
                        FROM Product
                        LEFT JOIN Inventory USING(ProductID)
                        WHERE Inventory.SiteID = {} AND ProductID in ({})
                        """.format(siteid, ",".join(prodids_in_cart)))
                    rows = cursor.fetchall()
                show_carts = [(row[0], row[1].strip(), row[2], row[3], prod_in_cart[str(row[0])], row[2]*prod_in_cart[str(row[0])]) for row in rows]
                for row in show_carts:
                    cart_total += row[-1]
            else:
                raise Exception(1003, "Please add items then checkout")

            if checkout_type == "normal" and cart_total > card_credit:
                # check balance
                raise Exception(1004, "Your credit/balance on the card is insufficient")
            
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Online first create address
                    if siteid == 10001:
                        import random
                        shippers = ['Fedex', 'USPS', 'UPS', 'EMS', 'DHL']
                        TrackingNumber = "'{}'".format(random.randint(10000000, 99999999))
                        ShipperName = "'{}'".format(shippers[random.randint(0, 4)])
                        
                        cursor.execute("""
                            SELECT AddressID
                            FROM Address
                            WHERE StreetNumber = '{}' AND Street = '{}' AND Line2 = '{}'
                                AND City = '{}' AND State = '{}' AND Zipcode = '{}'
                            """.format(good_address['StreetNumber'], good_address['Street'], good_address['Line2'],
                                        good_address['City'], good_address['State'], good_address['Zipcode']))
                        row = cursor.fetchone()
                        if row is not None:
                            AddressID = row[0]
                        else:
                            cursor.execute("""
                            INSERT INTO Address
                            (StreetNumber, Street, Line2, City, State, Zipcode)
                            VALUES
                            ('{}', '{}', '{}', '{}', '{}', '{}')
                            """.format(good_address['StreetNumber'], good_address['Street'], good_address['Line2'],
                                        good_address['City'], good_address['State'], good_address['Zipcode']))
                            AddressID = cursor.lastrowid                       
                    else:
                        TrackingNumber = 'NULL'
                        ShipperName = 'NULL'
                        AddressID = 'NULL'
                    # reduce inventory
                    for prodid, amount in prod_in_cart.items():
                        cursor.execute("""
                            UPDATE Inventory
                            SET ProductAmount = ProductAmount - {}
                            WHERE ProductID = {} AND SiteID = {}
                        """.format(amount, prodid, siteid))

                    sql = """
                    INSERT INTO CusOrder
                    (OrderPrice, SiteID, TrackingNumber, ShipperName, CustomerID, AddressID, CardNum, OrderTime)
                    VALUES
                    ({},{},{},{},{},{},{},'{}')
                    """.format(cart_total, siteid, TrackingNumber, ShipperName, cusid, AddressID, card, str(now))
                    cursor.execute(sql)
                    orderid = cursor.lastrowid
                    #then create OrderFor
                    for prodid, amount in prod_in_cart.items():
                        cursor.execute("""
                            INSERT INTO OrderFor
                            VALUES
                            ({},{},{})
                        """.format(orderid, prodid, amount))
            if card != 'NULL':
                reurl = '/order/{}/{}/'.format(orderid, card[1:-1])
            else:
                reurl = '/order/{}/'.format(orderid)
            success = True
            info = reurl
            clear_cart(session, siteid)
        except Exception as e:
            success = False
            if e.args[0] == 3819:
                info = "We don't have sufficient stock for some of your chosen products."
            else:
                info = e.args[1]

        ret_dat = json.dumps({
            "success": success,
            "info": info
        })
        return HttpResponse(ret_dat, content_type='application/json')



@csrf_exempt
def cart(request, siteid=10001):
    session = request.session
    if session.has_key('cart'):
        if session['cart']['siteid'] != siteid:
            session['cart'] = {
                'siteid': siteid,
                'prods': {},
                'total': 0
            }
    else:
        session['cart'] = {
            'siteid': siteid,
            'prods': {},
            'total': 0
        }
    mycart = session['cart']
    if request.method == "POST":
        post_data = request.POST.dict()
        action = post_data['action']
        prodid = post_data['prodid']
        if action == 'add_one':
            prodids = prodid.split("-")
            for prodid in prodids:
                if prodid not in mycart['prods']:
                    mycart['prods'][prodid] = 0
                mycart['prods'][prodid] += 1
                mycart['total'] += 1
        elif action == 'minus_one':
            if prodid not in mycart['prods']:
                mycart['prods'][prodid] = 0

            mycart['prods'][prodid] -= 1
            if mycart['prods'][prodid] <= 0:
                mycart['prods'][prodid] = 0

            mycart['total'] -= 1
            if mycart['total'] <= 0:
                mycart['total'] = 0

        elif action == 'remove':
            if prodid in mycart['prods']:
                mycart['total'] -= mycart['prods'][prodid]
                del mycart['prods'][prodid]
        session['cart'] = mycart
        ret_dat = json.dumps(mycart)
        return HttpResponse(ret_dat, content_type='application/json')
    
    else:
        context = {}
        context = get_stock_sites(context)
        mycart = session['cart']
        prod_in_cart = mycart['prods']
        prodids_in_cart = mycart['prods'].keys()
        cart_total = 0

        if len(prodids_in_cart) > 0:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ProductID, ProductName, ProductPrice, ProductAmount
                    FROM Product
                    LEFT JOIN Inventory USING(ProductID)
                    WHERE Inventory.SiteID = {} AND ProductID in ({})
                    """.format(siteid, ",".join(prodids_in_cart)))
                rows = cursor.fetchall()
            show_carts = [(row[0], row[1].strip(), row[2], row[3], prod_in_cart[str(row[0])], row[2]*prod_in_cart[str(row[0])]) for row in rows]
            for row in show_carts:
                cart_total += row[-1]
        else:
            show_carts = []
        context['items_in_cart'] = mycart['total']
        context['show_carts'] = show_carts
        context['cart_total'] = cart_total
        context['siteloc'] = 'Shop'
        context['subloc'] = 'Cart'
        context['shopat'] = int(siteid)
        return render(request, 'cs425proj/cart.html', context)

def logout(request):
    session = request.session
    if session.has_key('loggedin'):
        del session['loggedin']
        if session.has_key('user'):
            del session['user']
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@csrf_exempt
def checkout_confirm_account(request):
    session = request.session
    success = True
    if session.has_key('loggedin') and session['loggedin']:
        ret_dat = json.dumps({"success": success})
        return HttpResponse(ret_dat, content_type='application/json')

    if request.method == "POST":
        post_data = request.POST.dict()
        if "Account Number" in post_data:
            try:
                anumber = int(post_data["Account Number"])
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT *
                        FROM Customer
                        WHERE AccountNumber = {}""".format(anumber)
                    )
                    row = cursor.fetchone()
                session['user'] = {
                    'CustomerID': row[0],
                    'FirstName': row[1],
                    'LastName': row[2],
                    'PhoneNumber': row[3],
                    'AccountNumber': row[4],
                    'Username': row[5],
                    'Email': row[7],
                }
                session['loggedin'] = True
            except:
                success = False
                session['loggedin'] = False
                if session.has_key('user'):
                    del session['user']
            
        elif "Username" in post_data and "Password" in post_data:
            username = post_data["Username"]
            password = post_data["Password"]
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT *
                        FROM Customer
                        WHERE Username = '{}' AND Password = '{}'""".format(
                            username, password
                        )
                    )
                    row = cursor.fetchone()
                session['user'] = {
                    'CustomerID': row[0],
                    'FirstName': row[1],
                    'LastName': row[2],
                    'PhoneNumber': row[3],
                    'AccountNumber': row[4],
                    'Username': row[5],
                    'Email': row[7],
                }
                session['loggedin'] = True
            except:
                success = False
                session['loggedin'] = False
                if session.has_key('user'):
                    del session['user']
    ret_dat = json.dumps({"success": success})
    return HttpResponse(ret_dat, content_type='application/json')

def orderdetail(request, orderid=None, paycard=None):
    context = {}
    context = get_stock_sites(context)
    session = request.session
    if orderid is not None and paycard is None:
        #require to login
        if session.has_key('loggedin') and session['loggedin']:
            cusid = session['user']['CustomerID']
            ordersql = """
            SELECT *
            FROM CusOrder
            WHERE OrderID = {} AND CustomerID = {}
            """.format(orderid, cusid)
        else:
            return render(request, '404.html')
    elif orderid is not None:
        ordersql = """
            SELECT *
            FROM CusOrder
            WHERE OrderID = {} AND CardNum = {}
            """.format(orderid, paycard)
    with connection.cursor() as cursor:
        cursor.execute(ordersql)
        row = cursor.fetchone()
        if row is None:
            return render(request, '404.html')
        order = {
            'OrderID': row[0],
            'OrderPrice': row[1],
            'SiteID': row[2],
            'TrackingNumber': row[3],
            'ShipperName': row[4],
            'CustomerID': row[5],
            'AddressID': row[6],
            'CardNum': row[7],
            'OrderTime': row[8]
        }
    if order['CardNum'] is None:
        order['payment'] = 'Bill Later'
    else:
        order['payment'] = order['CardNum']
    if order['CustomerID'] is None:
        order['cusname'] = 'guest'
        order['ordertype'] = 'Guest Order'
    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT FirstName
                FROM Customer
                WHERE CustomerID = {}
            """.format(order['CustomerID']))
            row = cursor.fetchone()
        order['cusname'] = row[0]
        order['ordertype'] = 'Frequent Customer'
    context["order"] = order
    if order['AddressID'] is not None:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM Address
                WHERE AddressID = {}
                """.format(order['AddressID']))
            row = cursor.fetchone()
    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Stock.AddressID, StreetNumber, Street, Line2, City, State, Zipcode
                FROM Address
                JOIN Stock
                WHERE SiteID = {}
                """.format(order['SiteID']))
            row = cursor.fetchone()
    addr_info = {}
    addr_info['address1'] = ' '.join([row[1], row[2]])
    addr_info['address2'] = row[3]
    addr_info['city'] = row[4]
    addr_info['state'] = row[5]
    addr_info['zipcode'] = row[6]
    context['addr_info'] = addr_info
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ProductID, ProductName, ProductPrice, Amount
            FROM OrderFor
            JOIN Product USING(ProductID)
            WHERE OrderID = {}
            """.format(order['OrderID']))
        rows = cursor.fetchall()
    order_items = [(row[0], row[1], row[2], row[3], row[2]*row[3]) for row in rows]
    context['order_items'] = order_items
    context['siteloc'] = 'Order'
    return render(request, 'cs425proj/order-detail.html', context)

def login(request, siteid=10001):
    context = {}
    context = get_stock_sites(context)
    session = request.session
    check_cart_switch(session, siteid)

    context['siteloc'] = "Login/Signup"
    context['shopat'] = int(siteid)
    return render(request, 'cs425proj/login.html', context)

@csrf_exempt
def doLoginOrSignup(request, siteid=10001):
    session = request.session
    if session.has_key("loggedin") and session["loggedin"]:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    if request.method == "POST":
        try:
            post_data = request.POST.dict()
            action = post_data['action']
            if action == 'signup':
                firstname = post_data['firstname'].strip()
                lastname = post_data['lastname'].strip()
                username = post_data['username'].strip()
                password = post_data['password'].strip()
                if len(firstname) == 0 or len(lastname) == 0 or len(username) == 0 or len(password) == 0:
                    raise Exception(999, "Invalid information")
                import random
                an = random.randint(1111111111, 9999999999)
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO Customer
                        (FirstName, LastName, AccountNumber, Username, Password)
                        VALUES
                        ('{}', '{}', '{}', '{}', '{}')
                    """.format(firstname, lastname, an, username, password))
                    cusid = cursor.lastrowid
                    cursor.execute("""
                        SELECT *
                        FROM Customer
                        WHERE CustomerID = {}""".format(cusid)
                    )
                    row = cursor.fetchone()
                session['user'] = {
                    'CustomerID': row[0],
                    'FirstName': row[1],
                    'LastName': row[2],
                    'PhoneNumber': row[3],
                    'AccountNumber': row[4],
                    'Username': row[5],
                    'Email': row[7],
                }
                session['loggedin'] = True
            elif action == 'login':
                if 'accountno' in post_data:
                    accountno = post_data['accountno'].strip()
                    if len(accountno) == 0:
                        raise Exception(1000, 'Account number invalid')

                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT *
                            FROM Customer
                            WHERE AccountNumber = {}""".format(accountno)
                        )
                        row = cursor.fetchone()
                    if row is None:
                        raise Exception(1001, 'Account number not found')
                    session['user'] = {
                        'CustomerID': row[0],
                        'FirstName': row[1],
                        'LastName': row[2],
                        'PhoneNumber': row[3],
                        'AccountNumber': row[4],
                        'Username': row[5],
                        'Email': row[7],
                    }
                    session['loggedin'] = True
                elif 'username' in post_data and 'password' in post_data:
                    username = post_data['username']
                    password = post_data['password']
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT *
                            FROM Customer
                            WHERE Username = '{}' AND Password = '{}'""".format(
                                username, password
                            )
                        )
                        row = cursor.fetchone()
                    if row is None:
                        raise Exception(1002, 'Login information error')
                    session['user'] = {
                        'CustomerID': row[0],
                        'FirstName': row[1],
                        'LastName': row[2],
                        'PhoneNumber': row[3],
                        'AccountNumber': row[4],
                        'Username': row[5],
                        'Email': row[7],
                    }
                    session['loggedin'] = True
            success = True
            info = 'Congrats!'
        except Exception as e:
            success = False
            info = e.args
        ret_dat = json.dumps({
            'success': success,
            'info': info
        })
        return HttpResponse(ret_dat, content_type='application/json')
@csrf_exempt
def account(request):
    session = request.session
    context = {}
    context = get_stock_sites(context)
    context['siteloc'] = 'Account'
    if not (session.has_key('loggedin') and session['loggedin']):
        if session.has_key('cart'):
            siteid = session['cart']['siteid']
        else:
            siteid = 10001
        return redirect('/shop/{}/login/'.format(siteid))
    if request.method == 'POST':
        post_data = request.POST.dict()
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    for key, v in post_data.items():
                        sql = """
                        UPDATE Customer
                        SET {} = '{}'
                        WHERE CustomerID = {}
                        """.format(key, v, session['user']['CustomerID'])
                        cursor.execute(sql)
            user = session['user']
            for key, v in post_data.items():
                if key != 'Password':
                    user[key] = v
            session['user'] = user
        except:
            pass
        return HttpResponse(json.dumps("Done"), content_type='application/json')
    return render(request, "cs425proj/account.html", context)


def orderlist(request, page=1):
    page = int(page)
    session = request.session
    if not (session.has_key('loggedin') and session['loggedin']):
        if session.has_key('cart'):
            siteid = session['cart']['siteid']
        else:
            siteid = 10001
        return redirect('/shop/{}/login/'.format(siteid))
    else:
        cusid = session['user']['CustomerID']
    context = {}
    context = get_stock_sites(context)
    context['siteloc'] = 'My Orders'
    order_per_page = 7
    sql_count = """
            SELECT count(*)
            FROM CusOrder
            WHERE CustomerID = {}
            ORDER BY OrderTime DESC
        """.format(cusid)
    with connection.cursor() as cursor:
        cursor.execute(sql_count)
        total_orders = cursor.fetchone()[0]
    totalpages = math.ceil(1.0*total_orders/order_per_page)
    start_index = (page-1)*order_per_page
    sql = """
        SELECT *
        FROM CusOrder
        WHERE CustomerID = {}
        ORDER BY OrderTime DESC
        LIMIT {}, {}
    """.format(cusid, start_index, order_per_page)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    all_orders = [
        {
            'OrderID': row[0],
            'OrderPrice': row[1],
            'SiteID': row[2],
            'TrackingNumber': row[3],
            'ShipperName': row[4],
            'CustomerID': row[5],
            'AddressID': row[6],
            'CardNum': row[7],
            'OrderTime': row[8],
            'OrderType': 'Online' if row[2] == 10001 else 'In-Store', 
            'OrderJustTime':row[8].time(),
            'OrderDate': row[8].date()
        } for row in rows
    ]
    context['all_orders'] = all_orders
    context['prevpage'] = page-1
    context['curpage'] = page
    context['nextpage'] = page+1 if page + 1 <= totalpages else -1
    context['pages'] = list(range(1, totalpages+1))
    context['cururl'] = '/account/orders'

    
    return render(request, "cs425proj/account.html", context)

def report(request):
    sql = """
        SELECT State, Count(*)
        FROM 
        (
            SELECT State
            FROM CusOrder
            INNER JOIN Address USING (AddressID)
            UNION ALL
            SELECT State
            FROM CusOrder
            INNER JOIN Stock USING (SiteID)
            INNER JOIN Address ON Stock.AddressID = Address.AddressID
            WHERE Stock.StockType = 'store'
        ) tmpt
        GROUP BY State;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    data1 = [
        {
            "name": row[0],
            "value": row[1]
        } for row in rows
    ]
    
    sql = """
        SELECT State, AVG(OrderPrice)
        FROM 
        (
            SELECT State, OrderPrice
            FROM CusOrder
            INNER JOIN Address USING (AddressID)
            UNION ALL
            SELECT State, OrderPrice
            FROM CusOrder
            INNER JOIN Stock USING (SiteID)
            INNER JOIN Address ON Stock.AddressID = Address.AddressID
            WHERE Stock.StockType = 'store'
        ) tmpt
        GROUP BY State;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    data2 = [
        {
            "name": row[0],
            "value": float(row[1]),
        } for row in rows
    ]
    
    context = {}
    context = get_stock_sites(context)
    context['siteloc'] = "Report"
    context['report_data'] = [
        {
            "reportid": "report-1",
            "reporttitle": "(Online/In-store) Orders by State",
            "data": data1},
        {
            "reportid": "report-2",
            "reporttitle": "(Online/In-store) Sales Per Order by State",
            "data": data2
            }
    ]
    return render(request, "cs425proj/report.html", context);

def report1(request):
    sql = """
    SELECT DATE(OrderTime) as OrderDate, SUM(OrderPrice)
    FROM CusOrder
    GROUP BY OrderDate 
    ORDER BY OrderDate ASC;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    data1 = "date,sales\\n"
    for row in rows:
        data1+= "{},{}\\n".format(str(row[0]), int(row[1]))
    
    context = {}
    context = get_stock_sites(context)
    context['siteloc'] = "Report"
    context['report_data'] = [
        {
            "reportid": "report-1",
            "reporttitle": "Sales by Date",
            "data": data1
        }
    ]
    return render(request, "cs425proj/report1.html", context);

def report2(request):
    sql = """
    with OrderPriceLast(OrderTime, LastPrice) AS 
        (
            SELECT DATE_ADD(OrderTime, INTERVAL 1 MONTH), 
                OrderPrice 
            From CusOrder
        ),
        OrderPriceThis(OrderTIme, ThisPrice) AS
        (
            SELECT OrderTime, OrderPrice
            From CusOrder
        )
    SELECT ThisPrices.OrderYear, ThisPrices.OrderMonth, (ThisSales - LastSales)/ThisSales*100
    FROM
    (
        SELECT YEAR(OrderTime) AS OrderYear, MONTH(OrderTime) as OrderMonth, SUM(ThisPrice) as ThisSales
        FROM OrderPriceThis
        GROUP BY OrderYear, OrderMonth
    ) ThisPrices
    INNER JOIN
    (
        SELECT YEAR(OrderTime) AS OrderYear, MONTH(OrderTime) as OrderMonth, SUM(LastPrice) as LastSales
        FROM OrderPriceLast
        GROUP BY OrderYear, OrderMonth
    ) LastPrices
    ON ThisPrices.OrderYear = LastPrices.OrderYear AND ThisPrices.OrderMonth = LastPrices.OrderMonth
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    data1 = "date,sales\\n"
    numnow = len(rows)
    i = 0
    for row in rows:
        if i == numnow-1:
            break
        data1+= "{}-{:02d}-01,{}\\n".format(row[0],row[1], float(row[2]))
        i+=1
    
    context = {}
    context = get_stock_sites(context)
    context['siteloc'] = "Report"
    context['report_data'] = [
        {
            "reportid": "report-1",
            "reporttitle": "Sale Changes",
            "data": data1
        }
    ]
    return render(request, "cs425proj/report2.html", context);

def bills(request):
    session = request.session
    if not (session.has_key('loggedin') and session['loggedin']):
        if session.has_key('cart'):
            siteid = session['cart']['siteid']
        else:
            siteid = 10001
        return redirect('/shop/{}/login/'.format(siteid))
    else:
        cusid = session['user']['CustomerID']
    
    sql = """
    SELECT YEAR(OrderTime) as OrderYear, MONTH(OrderTime) as OrderMonth, SUM(OrderPrice) as Bill
    FROM CusOrder
    WHERE CustomerID = {} AND CardNum IS NULL
    GROUP BY OrderYear, OrderMonth
    ORDER BY OrderYear DESC, OrderMonth DESC
    """.format(cusid)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    bills = [(row[0], row[1], row[2]) for row in rows]
    context = {}
    context = get_stock_sites(context)
    context['bills'] = bills
    context['siteloc'] = 'Monthly Bills'
    return render(request, "cs425proj/account.html", context);

def report_low_stock(request):
    sql = """
        SELECT ProductID, ProductName, ManufacturerName, ProductAmount,
                SiteID, StockType, StreetNumber, Street, City, State, Zipcode
        FROM Product
        LEFT JOIN Manufacturer USING (ManufacturerID)
        LEFT JOIN Inventory USING (ProductID)
        LEFT JOIN Stock USING (SiteID)
        LEFT JOIN Address USING (AddressID)
        WHERE Inventory.ProductAmount < 10;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    low_stock_items = [
        {
            'ProductID': row[0],
            'ProductName': row[1],
            'ManufacturerName': row[2],
            'ProductAmount': row[3],
            'SiteID': row[4],
            'StockType': row[5],
            'StreetNumber': row[6],
            'Street': row[7],
            'City': row[8],
            'State': row[9],
            'Zipcode': row[10]
        } for row in rows
    ]
    context = {}
    context = get_stock_sites(context)
    context["low_stock_items"] = low_stock_items
    context["siteloc"] = "Stock Manage"
    return render(request, "cs425proj/lowstock.html", context)

@csrf_exempt
def restock_100(request):
    if request.method == 'POST':
        post_data = request.POST.dict()
        msg = post_data['msg']
        parts = msg.split("-")
        ProductID = parts[0]
        SiteID = parts[1]
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ManufacturerName
                FROM Product
                JOIN Manufacturer USING (ManufacturerID)
                WHERE ProductID = {}
            """.format(ProductID))
            row = cursor.fetchone()
        if row:
            ManuName = row[0]
        else:
            ManuName = "Unknown"
        sql = """
            UPDATE Inventory
            SET ProductAmount = ProductAmount + 100
            WHERE ProductID = {} AND SiteID = {}
        """.format(ProductID, SiteID)
        success = True
        info = ManuName
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except Exception as e:
            success = False
            info = e.args
        ret_dat = json.dumps({
            'success': success,
            'info': info
        })
        return HttpResponse(ret_dat, content_type='application/json')
from django.shortcuts import render

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

def shop(request, siteid=10001, ptype=0, manu=0, page=1):
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
    items_in_cart = session['cart']['total']

    siteid = int(siteid)
    ptype = int(ptype)
    manu = int(manu)
    page = int(page)
    context = get_stock_sites()
    context = get_all_product_types(context)
    context = get_all_manufacturers(context)
    items_per_page = 18
    if ptype ==0 and manu == 0:
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
    else:
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

    context['products'] = products

    cururl = '/shop/{}'.format(siteid)
    if ptype:
        cururl += '/ptype/{}'.format(ptype)
    elif manu:
        cururl += '/manu/{}'.format(manu)
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
    if request.method == "POST":
        success = True
        info = "Something Wrong"
        now = datetime.now()
        try:
            if session.has_key['loggedin'] and session['loggedin']:
                cusid = session['user']['CustomerID']
            else:
                cusid = '\\N'
            post_data = request.POST.dict()
            checkout_type = post_data["type"]
            card = post_data["card"]
            card_credit = 0
            shipping = post_data["shipping"]

            good_address = scrambleAddress(shipping)

            if siteid != 10001 and good_address is None:
                info = "You need to input a valid shipping address for an online order"
                raise Exception(info)
            
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
                   raise Exception("Card not found")
                card_credit = one[2]
                card = "'{}'".format(card)
            else:
                card = '\\N'

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
                raise Exception("Please add items then checkout")

            if checkout_type == "normal" and cart_total > card_credit:
                # check balance
                raise Exception("Your credit/balance on the card is insufficient")
            
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # reduce inventory
                    for prodid, amount in prod_in_cart.items():
                        cursor.execute("""
                            UPDATE Inventory
                            SET ProductAmount = ProductAmount - {}
                            WHERE ProductID = {} AND SiteID = {}
                        """.format(amount, prodid, siteid))
                    #then create CusOrder
                    if siteid == 10001:
                        import random
                        shippers = ['Fedex', 'USPS', 'UPS', 'EMS', 'DHL']
                        TrackingNumber = "'{}'".format(random.randint(10000000, 99999999))
                        ShipperName = "'{}'".format(shippers[random.randint(0, 4)])
                        # Online first create address
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
                            ('{}', '{}', '{}', '{}', '{}', '{}'))
                            """.format(good_address['StreetNumber'], good_address['Street'], good_address['Line2'],
                                        good_address['City'], good_address['State'], good_address['Zipcode']))
                            AddressID = cursor.lastrowid                       
                    else:
                        TrackingNumber = "\\N"
                        ShipperName = "\\N"
                        AddressID = "\\N"

                    sql = """
                    INSERT INTO CusOrder
                    (OrderPrice, SiteID, TrackingNumber, ShipperName, CustomerID, AddressID, CardNum, OrderTime)
                    VALUES
                    ({},{},{},{},{},{},{},{})
                    """.format(cart_total, siteid, TrackingNumber, ShipperName, cusid, AddressID, card, now.isoformat())
                    cursor.execute(sql)
                    orderid = cursor.lastrowid
                    #then create OrderFor
                    for prodid, amount in prod_in_cart.items():
                        cursor.execute("""
                            INSERT INTO OrderFor
                            VALUES
                            ({},{},{})
                        """.format(orderid, prodid, amount))
        except Exception as e:
            sucess = False
            info = e




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
            if prodid not in session['cart']['prods']:
                session['cart']['prods'][prodid] = 0
            session['cart']['prods'][prodid] += 1
            session['cart']['total'] += 1
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
        print(post_data)
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
            print(username)
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
                }
                session['loggedin'] = True
            except:
                success = False
                session['loggedin'] = False
                if session.has_key('user'):
                    del session['user']
    ret_dat = json.dumps({"success": success})
    return HttpResponse(ret_dat, content_type='application/json')


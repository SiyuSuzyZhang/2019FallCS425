from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.db import connection

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

def index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ProductType ORDER BY TypeName")
        rows = cursor.fetchall()
    productTypes = [(row[0], row[1].strip()) for row in rows]

    with connection.cursor() as cursor:
        cursor.execute("""
                SELECT ManufacturerID, ManufacturerName, Count(*)
                FROM Manufacturer
                JOIN Product USING(ManufacturerID)
                GROUP BY ManufacturerID
                ORDER BY ManufacturerName""")
        rows = cursor.fetchall()
    manufacturers = [(row[0], row[1].strip(), row[2]) for row in rows]
    
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

    context = {
        'productTypes': productTypes,
        'manufacturers': manufacturers,
        'featured_products': featured_products,
        'featured_types': featured_types,
        'rec_products_p1': rec_products[:3],
        'rec_products_p2': rec_products[3:],
        'siteloc': 'Showcase'
    }
    context = get_stock_sites(context)
    return render(request, 'cs425proj/index.html', context)
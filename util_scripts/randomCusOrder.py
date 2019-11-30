import random
from datetime import datetime, timedelta

random.seed(117)

site = 10000
snum = 9

debit = 30000
credit = 40000

debitnum = 100
creditnum = 100

low_max = 15
high_max = 50

days = 700
day_start = datetime(2018, 1, 1)

shippers = ['Fedex', 'USPS', 'UPS', 'EMS']
products = {100001:30,100002:50,100003:70,100004:25,100005:45,100006:65,100007:85,100008:20,100009:40,100010:60,100011:150,100012:170,100013:250,100014:350,100015:160,100016:380,100017:700,100018:1100,100019:1900,100020:850,100021:1200,100022:2000,100023:40,100024:80,100025:120,100026:100,100027:150,100028:120,100029:180,100030:500,100031:700,100032:900,100033:1100,100034:1100,100035:900,100036:850,100037:800,100038:600,100039:150,100040:170,100041:200,100042:130,100043:160,100044:200,100045:220,100046:190,100047:250,100048:500,100049:700,100050:550,100051:750,100052:1200,100053:800,100054:1250,100055:1300,100056:1100,100057:1150,100058:1300,100059:1200,100060:200,100061:380,100062:700,100063:350,100064:230,100065:1100,100066:1800,100067:2500,100068:800,100069:1000,100070:1500,100071:700,100072:1700,100073:2000,100074:1200,100075:1200,100076:130,100077:180,100078:250,100079:200,100080:220,100081:230,100082:5000,100083:7000}

ordernum = 1000001

of_f = open("orderfor_dat.csv", "w")
co_f = open("cusorder_dat.csv", "w")

def generateOrderFor(oid):
    big = 1 if random.randint(1, 100) >= 87 else 0
    b_low = 7
    b_high = 15
    b_item_max = 9
    s_low = 1
    s_high = 6
    s_item_max = 3
    productids = list(products.keys())
    random.shuffle(productids)

    if big:
        pnum = random.randint(b_low, b_high)
        im = b_item_max
    else:
        pnum = random.randint(s_low, s_high)
        im = s_item_max
    price = 0
    for pid in productids[:pnum]:
        amount = random.randint(1, im)
        price += amount * products[pid]
        of_f.write("{},{},{}\n".format(oid, pid, amount))
    return price


for i in range(0, days+1):
    thisday = day_start + timedelta(days=i)
    high = 1 if random.randint(1, 100) > 80 else 0
    if high == 1:
        daily = random.randint(high_max/2, high_max)
    else:
        daily = random.randint(0, low_max)

    for j in range(0, daily):
        oid = ordernum
        ordernum += 1
        siteID = site + random.randint(0, snum)
        if siteID == site:
            siteID += 1
        tnum = random.randint(10000000, 99999999)
        shipper = shippers[random.randint(0, 3)]

        custype = random.randint(1, 10)
        if custype < 4:
            custype = 0
        else:
            custype = 1
        creditcard = 1 if random.randint(1, 10) > 4 else 0
        if custype == 0:
            cusid = ""
            addrid = random.randint(1000009, 1000079)
            if creditcard == 1:
                cnum = "22223333444{}".format(credit + random.randint(1, creditnum))
            else:
                cnum = "11112222333{}".format(debit + random.randint(1, debitnum))
        else:
            cusnum = random.randint(1000001, 1000057)
            cusid = "{}".format(cusnum)
            if creditcard == 1:
                cnum = "22223333444{}".format(credit + cusnum-1000001 + 10)
            else:
                cnum = "11112222333{}".format(debit + cusnum-1000001 + 10)
            addrid = 1000009 + cusnum-1000001
        

        hr = random.randint(0, 23)
        mi = random.randint(0, 59)
        ss = random.randint(0, 59)
        order_price = generateOrderFor(oid)

        order_datetime = datetime(thisday.year, thisday.month, thisday.day, hr, mi, ss)
        co_f.write("{},{},{},{},{},{},{},{},{}\n".format(oid, order_price, siteID, tnum, shipper,
                                        cusid, addrid, cnum, order_datetime))   

of_f.close()
co_f.close()


import random
random.seed(117)

num_product = 83
num_site = 9

for i in range(1, num_product+1):
    for j in range(1, num_site+1):
        pid = 100000 + i
        sid = 10000 + j
        amt = random.randint(0, 501)
        print("{},{},{}".format(pid, sid, amt))
from datetime import datetime
import time

a = datetime.now()
time.sleep(5)
b = datetime.now()
time.sleep(5)
c = datetime.now()
t1 = b-a
t2 = c-b

print(a)
print(b)
print(c)
print(t1, t2)
print(t1+t2)
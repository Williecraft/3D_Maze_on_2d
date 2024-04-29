from datetime import datetime

start = datetime.now()

while True:
    now = datetime.now()
    times = now-start
    print(repr(times))
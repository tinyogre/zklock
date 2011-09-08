
import zklock, time

zklock.connect()
z = zklock.Lock('test')

if z.acquire():
    time.sleep(20)
    z.release()


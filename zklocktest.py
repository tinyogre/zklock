#
# To test this, first have a running local zookeeper installation 
# (See http://zookeeper.apache.org/)
# Next, open a couple of shells
# Run this in the first one, watch the output.  It will create a lock and hold it for 20 seconds.
# Run it again in the second one, watch that it doesn't acquire the lock until the fist instance exits,
# and then holds the lock itself for 20 seconds after acquiring it.
#
# You can speed things up by killing the first instance after you
# start the second.  The second should immediately acquire the lock.
#
import zklock, time

zklock.connect()
z = zklock.Lock('test')

if z.acquire():
    print "zklocktest: Lock acquired"
    time.sleep(20)
    z.release()

print "zklocktest: Exiting"


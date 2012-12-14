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

# You can specify a host to connect().  The default is localhost and
# the default ZooKeeper port.
zklock.connect()

# This creates a global lock named 'test'.  Any other zklock connected
# to the same ZooKeeper instance and trying to create a lock of the
# same name will be blocked while this program holds the lock named 'test'
z = zklock.Lock('test')

 try:
     if z.acquire():
         print "zklocktest: Lock acquired"
         time.sleep(20)
         z.release()
 except:
     z.release()

with zklock.ScopedLock("scoped_lock_test", block=False) as z:
    if z.acquired:
        print "Locked!"
        time.sleep(20)
    else:
        print "Could not obtain lock!"
print "zklocktest: Exiting"

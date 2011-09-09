
import zookeeper, threading
import sys

connected=False
conn_cv = threading.Condition( )
reconnect_host = ''

ZOO_OPEN_ACL_UNSAFE = {"perms":0x1f, "scheme":"world", "id" :"anyone"};
ROOT="/ZkLock"

# locks is a hash by lock name, each value being a list of locks that are waiting for that name.
locks = {}

def my_connection_watcher(handle,type,state,path):
    global connected, conn_cv
    conn_cv.acquire()
    connected = True
    conn_cv.notifyAll()
    conn_cv.release()

def my_lock_watcher(handle,type,state,path):
    global locks
    if not path in locks:
        return

    # Notify everyone that's blocked on this lock that should wake up and see if they acquired the lock 
    # (Which happens when they have the oldest entry in the list of waiters)
    locklist = locks[path]
    for lock in locklist:
        lock.cv.acquire()
        lock.cv.notifyAll()
        lock.cv.release()

def connect(host=None):
    global conn_cv, connected, handle
    global reconnect_host

    if host is None:
        host = "localhost:2181"

    reconnect_host = host

    conn_cv.acquire()
    handle = zookeeper.init(host, my_connection_watcher, 10000)
    while not connected:
        conn_cv.wait()
    conn_cv.release()

    connected = False
    while not connected:
        try:
            zookeeper.create(handle, ROOT, "1", [ZOO_OPEN_ACL_UNSAFE], 0)
            connected = True
        except zookeeper.NodeExistsException as e:
            # No worries
            connected = True
        except zookeeper.ConnectionLossException:
            continue
        except:
            raise

def reconnect():
    connect(reconnect_host)

class Lock:
    def __init__(self, name):
        self.name = ROOT + '/' + name
        self.cv = threading.Condition()
        created = False
        while not created:
            try:
                zookeeper.create(handle, self.name, "0", [ZOO_OPEN_ACL_UNSAFE], 0)
                created=True
            except zookeeper.NodeExistsException:
                # S'ok.
                created = True
            except zookeeper.ConnectionLossException:
                continue

        self.znode = None

    def createNode(self):
        # the EPHEMERAL flag creates a new unique node name with an increasing sequence
        created = False
        while not created:
            try:
                self.znode = zookeeper.create(handle, self.name + '/lock', "0", [ZOO_OPEN_ACL_UNSAFE], zookeeper.EPHEMERAL | zookeeper.SEQUENCE)
                created = True
            except zookeeper.ConnectionLossException:
                reconnect()
                continue

    def acquire(self):
        # Here's what this does:
        # Creates a child node of the named node with a unique ID
        # Gets all the children of the named node
        # Looks to see if the node it just created is the lowest in sequence
        # If it is, the lock is ours!  Done!
        # If not, wait for the children callback to signal that there has been a change to children, then start over at step 2
        #
        # So it's not polling, but it will wake up any time another client starts waiting, in addition to any time a client goes away
        
        
        global handle
        global locks

        if not self.name in locks:
            locks[self.name] = []
        locks[self.name] += [self]

        exists = False
        self.createNode()
        self.keyname = self.znode[self.znode.rfind('/') + 1:]
        
        acquired = False
        self.cv.acquire()
        while not acquired:
            try:
                children = zookeeper.get_children(handle, self.name, my_lock_watcher)
            except zookeeper.ConnectionLossException:
                reconnect()
                continue

            children.sort()
            if len(children) == 0 or not self.keyname in children:
                # Disconnects or other errors can cause this
                self.createNode()
                continue

            if self.keyname == children[0]:
                # The lock is ours!
                acquired = True
            else:
                # Wait for a notification from get_children
                self.cv.wait()
        self.cv.release()

        locks[self.name].remove(self)
        return True

    def release(self):
        # All release has to do, if you follow the logic in acquire, is delete the unique ID that this lock created.  That will wake
        # up all the other waiters and whoever is first in line can then have the lock.
        global handle
        released = False
        while not released:
            try:
                zookeeper.delete(handle, self.znode)
                released = True
            except zookeeper.ConnectionLossException:
                reconnect()
        self.znode = None
        self.keyname = None

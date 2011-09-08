# Copyright (c) 2011 Joe Rumsey (joe@rumsey.org)
#
# This file is part of zklock (http://github.com/tinyogre/zklock)
# 
# zklock is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import zookeeper, threading
import sys

connected=False
conn_cv = threading.Condition( )

ZOO_OPEN_ACL_UNSAFE = {"perms":0x1f, "scheme":"world", "id" :"anyone"};
ROOT="/ZkLock"

locks = {}

def my_connection_watcher(handle,type,state,path):
    global connected, conn_cv
    conn_cv.acquire()
    connected = True
    conn_cv.notifyAll()
    conn_cv.release()

def my_lock_watcher(handle,type,state,path):
    print "lock_watcher: " + path
    
    global locks
    if not path in locks:
        return

    if path in locks:
        locklist = locks[path]
        for lock in locklist:
            lock.cv.acquire()
            lock.cv.notifyAll()
            lock.cv.release()
    

def connect(host=None):
    global conn_cv, connected, handle

    if host is None:
        host = "localhost:2181"
    conn_cv.acquire()
    handle = zookeeper.init(host, my_connection_watcher, 10000)
    while not connected:
        conn_cv.wait()
    conn_cv.release()

    try:
        zookeeper.create(handle, ROOT, "1", [ZOO_OPEN_ACL_UNSAFE], 0)
    except zookeeper.NodeExistsException as e:
        print 'Root "' + ROOT + '" of lock tree already exists'
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

class Lock:
    def __init__(self, name):
        self.name = ROOT + '/' + name
        self.cv = threading.Condition()
        try:
            zookeeper.create(handle, self.name, "0", [ZOO_OPEN_ACL_UNSAFE], 0)
        except zookeeper.NodeExistsException:
            # S'ok.
            pass

        self.znode = None

    def createNode(self):
        self.znode = zookeeper.create(handle, self.name + '/lock', "0", [ZOO_OPEN_ACL_UNSAFE], zookeeper.EPHEMERAL | zookeeper.SEQUENCE)

    def acquire(self):
        global handle
        global locks

        if not self.name in locks:
            locks[self.name] = []
        locks[self.name] += [self]

        exists = False
        self.createNode()
        print "Created znode: " + str(self.znode)
        self.keyname = self.znode[self.znode.rfind('/') + 1:]
        print self.keyname
        
        acquired = False
        self.cv.acquire()
        while not acquired:
            children = zookeeper.get_children(handle, self.name, my_lock_watcher)
            children.sort()
            print str(children)
            if len(children) == 0 or not self.keyname in children:
                # Disconnects can cause this
                print "Creating new child because " + self.keyname + " is not in children"
                self.createNode()
                continue

            if self.keyname == children[0]:
                print "Acquired lock on " + self.name
                # The lock is ours!
                acquired = True
            else:
                print "Waiting..."
                # Wait for a notification from get_children
                self.cv.wait()
        self.cv.release()

        locks[self.name].remove(self)
        return True

    def release(self):
        global handle
        zookeeper.delete(handle, self.znode)
        self.znode = None
        self.keyname = None

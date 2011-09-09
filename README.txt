Copyright (c) 2011 Joe Rumsey (joe@rumsey.org)
Released under the LGPL, see COPYING.txt for details

zklock is a python package that provides a simple distributed mutex
implementation using zookeeper as the back end.

* HOW TO INSTALL

$ pip install zklock

Or get it from github, see http://github.com/tinyogre/zklock for details

zklock requires zkpython.  Additionally, installing zkpython requires
the zookeeper C library be installed first.  You can download and
learn about ZooKeeper here: http://zookeeper.apache.org/.  Though
ZooKeeper is written in Java, the C library is part of the main
distribution.

* WHY DOES THIS EXIST

I'm writing a mobile game that includes an online turn based
mode.  I started investigating Cassandra for storage of games, but
almost immediately found that I needed some kind of row level locking
to avoid races with both players updating the same game.  Turns in
this game are simultaneously executed, and I accept a save from
whoever submits it first.  Stored chat has a similar issue.

The web interface is built in python with Django.  So I needed a lock
mechanism for Cassandra in python.  I found existing ZooKeeper
solutions in Java, but none in Python.  So here's this.  It's cribbed
from several other Java examples out there, but not translated.

* HOW TO USE THIS

See zklocktest.py on github for a simple example.


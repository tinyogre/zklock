from distutils.core import setup

setup(name='zklock',
      version='0.1',
      author='Joe Rumsey',
      author_email='joe@rumsey.org',
      url='http://github.com/tinyogre/zklock',
      description='zklock provides a simple distributed locking mechanism using zookeeper',
      classifiers=['Programming Language :: Python', 
                   'Programming Language :: Python :: 2.6',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Operating System :: OS Independent',
                   'Intended Audience :: Developers',
                   'Development Status :: 3 - Alpha'],
      py_modules = ['zklock']
      )

bud
===

author: Peter Hoffmann

Overview
--------

bud runs stuff for you

Installation / Usage
--------------------

To install use pip:

    $ pip install bud


Or clone the repo:

    $ git clone https://github.com/hoffmann/bud.git
    $ python setup.py install

Contributing
------------

TBD

Example
-------

TBD


TODO
-----
Logging

    http://stackoverflow.com/questions/4984428/python-subprocess-get-childrens-output-to-file-and-terminal



Allow configuration in budfile:

    config:    
        include:
            - ~/bud.yml
        log: ~/logs/bud/


Usage

    #run predefined task
    bud [taskname]


    # use bud.yml configuration instead of global ~/.bud.yml
    bud -c bud.yml [taskname]


    # run oneshot task
    bud -r 'ls -hla'



Bud Configuration
-----------------


    vars:
        key: value
        key2: value2




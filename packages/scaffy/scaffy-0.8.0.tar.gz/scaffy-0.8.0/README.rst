######
scaffy
######

.. readme_inclusion_marker

**scaffy** is a small tool to create, manage and apply project scaffolds (or
any directory scaffold for that matter). It includes a web service that allows
storing the scaffolds remotely.

Installation
============

.. code-block:: shell

    $ pip install scaffy


Contributing
============

Setting up development repo
---------------------------

.. code-block:: shell

    $ git clone git@github.com:novopl/scaffy.git
    $ cd scaffy
    $ virtualenv env
    $ source ./env/bin/activate
    $ python setup.py develop
    $ pip install -r ops/devrequirements.txt

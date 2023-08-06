Pyngboard |build-status|
=========================

This project provides a python library for accessing `Pingboard <http://docs.pingboard.apiary.io>`_ resources.

Installation
=============
To install pyngboard you can use pip:

.. code-block:: bash

    $ pip install pyngboard

Usage and Credentials
=====================

You'll need a Pingboard `client_id` and `client_secret` and use it as constructor args:

.. code-block:: python

  from pyngboard import PingboardClient
  client=PingboardClient(client_id='<a_client_id>', client_secret='<a_client_secret>')

You can also skip constructor args and library will lookup credentials in the following order:

  1. Environment variables `PINGBOARD_CLIENT_ID` and `PINGBOARD_CLIENT_SECRET`
  2. A `.pingboard` file located at user home with the following content:

     .. code-block:: properties

       client_id=<a_client_id>
       client_secret=<a_client_secret>


License
========

This project's source code and it's documentation is released under the `MIT License <https://opensource.org/licenses/MIT>`_.

.. |build-status| image:: https://travis-ci.org/tsouza/pyngboard.svg?branch=master
   :target: https://travis-ci.org/tsouza/pyngboard

pyATS Easypy Component
======================

pyATS is an end-to-end testing ecosystem, specializing in data-driven and 
reusable testing, and engineered to be suitable for Agile, rapid development 
iterations. Extensible by design, pyATS enables developers start with small, 
simple and linear test cases, and scale towards large, complex and asynchronous 
test suites.

pyATS is initially developed internally in Cisco, and is now available to the
general public starting late 2017 through `Cisco DevNet`_. Visit the pyATS
home page at

    https://developer.cisco.com/site/pyats/

.. _Cisco DevNet: https://developer.cisco.com/


Easypy Package
--------------

This is a sub-component of pyATS that aggregates script runs into encapsulated
environments, collects logs into archives, and sends reporting emails.

Requirements
------------

pyATS currently supports Python 3.4+ on Linux & Mac systems. Windows platforms
are not yet supported.

Quick Start
-----------

.. code-block:: console

    # install pyats as a whole
    $ pip install pyats

    # to upgrade this package manually
    $ pip install --upgrade pyats.easypy

    # to install alpha/beta versions, add --pre
    $ pip install --pre pyats.easypy

For more information on setting up your Python development environment,
such as creating virtual environment and installing ``pip`` on your system, 
please refer to `Virtual Environment and Packages`_ in Python tutorials.

.. _Virtual Environment and Packages: https://docs.python.org/3/tutorial/venv.html


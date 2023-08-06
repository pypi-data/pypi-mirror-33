.. image:: https://travis-ci.org/davebryson/py-abci.svg?branch=master
  :target: https://https://travis-ci.org/davebryson/py-abci

.. image:: https://codecov.io/gh/davebryson/py-abci/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/davebryson/py-abci

.. image:: https://img.shields.io/pypi/v/abci.svg
  :target: https://pypi.python.org/pypi/abci

Build blockchain applications in Python for Tendermint

Version
-------
Supports ABCI v0.12.0 and latest Tendermint

Installation
------------
Requires Python >= 3.6.5

``pip install abci``  OR ``python setup.py install``

Generating Protobuf
-------------------
*ONLY* needed for developing this code base, not to create apps.  If you
just want to create apps, goto Getting Started

1. Install protoc
2. Install go
3. Install gogo protobuf via go
4. Run `make gogo`


Getting Started
---------------
1. Extend the BaseApplication class
2. Implement the Tendermint ABCI callbacks - see https://github.com/tendermint/abci
3. Run it

See the example app ``counter.py`` application under the ``examples`` directory
here: https://github.com/davebryson/py-abci/blob/master/examples/counter.py

.. --- mode: rst ---

=====
unipy
=====



|Travis|_  |AppVeyor|_  |Coveralls|_  |Readthedocs|_   
|PyPi|_  |Python35|_  |Python36|_ |DOI|_


.. |Travis| image:: https://travis-ci.org/pydemia/unipy.svg?branch=master
.. _Travis: https://travis-ci.org/pydemia/unipy

.. |AppVeyor| image:: https://ci.appveyor.com/api/projects/status/github/pydemia/unipy?branch=master&svg=true
.. _AppVeyor: https://ci.appveyor.com/project/pydemia/unipy/history

.. |Coveralls| image:: https://coveralls.io/repos/github/pydemia/unipy/badge.svg?branch=master&service=github
.. _Coveralls: https://coveralls.io/github/pydemia/unipy

.. |Readthedocs| image:: https://readthedocs.org/projects/unipy/badge/?version=latest
.. _Readthedocs: http://unipy.readthedocs.io/en/latest/?badge=latest

.. |PyPi| image:: https://badge.fury.io/py/unipy.svg
.. _PyPi: https://badge.fury.io/py/unipy.svg

.. |Python35| image:: https://img.shields.io/badge/python-3.5-blue.svg 
.. _Python35: https://badge.fury.io/py/unipy.svg 

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg 
.. _Python36: https://badge.fury.io/py/unipy.svg 

.. |DOI| image:: https://zenodo.org/badge/21369/pydemia/unipy.svg
.. _DOI: https://zenodo.org/badge/latestdoi/21369/pydemia/unipy


Documentation
=============



Features
========

- database connection:

  - get ``pandas.DataFrame`` from:
  
    - ``mysql``
    - ``mariadb``
    - ``postgresql``
    - ``ibm DB2``
    - ``oracleDB``

  - import ``pandas.DataFrame`` to:
  
    - ``mysql``
    - ``mariadb``

- Mathmatics:

  - Coordinate plane

- Statistics:

  - Hypothesis Test
  - Multivariate Analysis
    - Variance Inflation Factor
    - Stepwise Elimination with VIF
    - Feature Selection

- Sample Datasets:

  - Adult(UCI)
  - Wine Quality(UCI)


Structure
=========

- database

  - getQuery
  - importQuery

- math

  - geometry
 
- statsmod

  - getQuery
  - importQuery
  
- tools

  - printWrappers

- sample

  - datasets
    - dataManager
  - sample
  
- tests

  - test
  
- docs

  - readme


Issues
======

``cx_Oracle`` Setting
====================

0. Install this:
```sh
sudo apt-get install build-essential unzip python-dev libaio-dev  
```

1. Download `instant-client` from [here](http://www.oracle.com/technetwork/topics/linuxx86-64soft-092277.html)  
2. Unzip `instantclient-basic-linux.x64-11.2.0.4.0.zip` (Since 12c is not supported yet)
```sh
cd ~/apps
unzip ~/jdbcDriver/oracle-client/instantclient-basic-linux.x64-11.2.0.4.0.zip  
```
3. Set `ORACLE_HOME` environment variable  
```sh
vim ~/.bashrc  
```

```vim
# Oracle Instant Client PATH
export ORACLE_HOME="/home/pydemia/apps/instantclient_11_2"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
```

3. Set symlink

```sh
cd $ORACLE_HOME  
ln -s libclntsh.so.11.1   libclntsh.so  
```

4. Edit `/etc/ld.so.conf.d/oracle.conf`  
```sh
sudo ldconfig  
```

-----

```sh
sudo vim /etc/profile.d/oracle.sh  
```

```vim
# Oracle Instant Client PATH  
export ORACLE_HOME="/home/pydemia/apps/instantclient_11_2"  
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME  
```


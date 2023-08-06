About
=====
``testing.elasticsearch`` automatically setups a elasticsearch instance in a temporary directory, and destroys it after testing.

.. image:: https://travis-ci.org/criteo-forks/testing.elasticsearch.svg?branch=master
   :target: https://travis-ci.org/criteo-forks/testing.elasticsearch

.. image:: https://coveralls.io/repos/criteo-forks/testing.elasticsearch/badge.png?branch=master
   :target: https://coveralls.io/r/criteo-forks/testing.elasticsearch?branch=master

.. image:: https://codeclimate.com/github/criteo-forks/testing.elasticsearch/badges/gpa.svg
   :target: https://codeclimate.com/github/criteo-forks/testing.elasticsearch


Install
=======
Use pip::

   $ pip install testing.elasticsearch6

And ``testing.elasticsearch6`` requires Elasticsearch server in your PATH.


Usage
=====
Create Elasticsearch instance using ``testing.elasticsearch.Elasticsearch``::

  import testing.elasticsearch
  from sqlalchemy import create_engine

  # Lanuch new Elasticsearch server
  with testing.elasticsearch.Elasticsearch() as elasticsearch:
      # connect to Elasticsearch (using elasticsearch-py)
      es = Elasticsearch(**elasticsearch.dsn())

      #
      # do any tests using Elasticsearch...
      #

  # Elasticsearch server is terminated here


``testing.elasticsearch.Elasticsearch`` generates temporary config files and data directories.
On deleting Elasticsearch object, it terminates Elasticsearch instance and removes temporary files and directories.

If you want a database including indexes and any fixtures for your apps,
use ``copy_data_from`` keyword::

  # uses a copy of specified data directory of Elasticsearch.
  elasticsearch = testing.elasticsearch.Elasticsearch(copy_data_from='/path/to/your/index')


For example, you can setup new Elasticsearch server for each testcases on setUp() method::

  import unittest
  import testing.elasticsearch

  class MyTestCase(unittest.TestCase):
      def setUp(self):
          self.elasticsearch = testing.elasticsearch.Elasticsearch()

      def tearDown(self):
          self.elasticsearch.stop()


Requirements
============
* Python 2.7, 3.6

License
=======
Apache License 2.0


History
=======

1.0.0 (2016-08-20)
-------------------
* Drop python 2.6, 3.2 support
* Depend on testing.common.database >= 2.0.0
* Set booting timeout to 20sec
* Fix bugs:

  - #1: find_elasticsearch_yaml_path() does not refer elasticsearch_home argument
  - #2: Make ES_PATH absolute

0.9.1 (2016-02-04)
-------------------
* Depend on ``testing.common.database`` package

0.9.0 (2015-12-13)
-------------------
* First release

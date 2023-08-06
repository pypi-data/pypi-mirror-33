|banner|

.. raw:: html

   <h1 align="center">

oceandb-mongodb-driver

.. raw:: html

   </h1>

..

    🐳  `Mongo DB <https://www.mongodb.com/>`_  driver (Python).

.. |banner| image:: doc/img/repo-banner@2x.png
   :target: https://oceanprotocol.com

.. image:: https://img.shields.io/pypi/v/oceandb-mongodb-driver.svg
        :target: https://pypi.python.org/pypi/oceandb-mongodb-driver

.. image:: https://travis-ci.com/oceanprotocol/oceandb-mongodb-driver.svg?token=pA8zcB6SCxKW5MHpqs6L&branch=master
        :target: https://travis-ci.com/oceanprotocol/oceandb-mongodb-driver

.. image:: https://readthedocs.org/projects/oceandb-mongodb-driver/badge/?version=latest
        :target: https://oceandb-mongodb-driver.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




MongoDB driver to connect implementing OceanDB.

* Free software: Apache Software License 2.0
* Documentation: https://oceandb-mongodb-driver.readthedocs.io.


How to use it
-------------

First of all we have to specify where is allocated our config.
To do that we have to pass the following argument:

.. code-block:: python

    --config=/path/of/my/config
..

If you do not provide a configuration path, by default the config is expected in the config folder.

In the configuration we are going to specify the following parameters to

.. code-block:: python

    [oceandb]

    [oceandb]

    enabled=true            # In order to enable or not the plugin
    module=mongodb          # You can use one the plugins already created. Currently we have mongodb and bigchaindb.
    module.path=            # You can specify the location of your custom plugin.
    db.hostname=localhost   # Address of your MongoDB.
    db.port=9985            # Port of your Mongodb.

    db.username=user        # If you are using authentication, mongodb username.
    db.password=password    # If you are using authentication, mongodb password.
    db.name=test            # Mongodb database name
    db.collection=col       # Mongodb collection name

..

Once you have defined this the only thing that you have to do it is use it:

.. code-block:: python

    oceandb = OceanDb(conf)
    oceandb.write({"id": 1, "value": "test"})

..

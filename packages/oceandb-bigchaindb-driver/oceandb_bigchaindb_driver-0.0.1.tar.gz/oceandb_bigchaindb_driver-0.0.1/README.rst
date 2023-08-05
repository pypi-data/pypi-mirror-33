|banner|

.. raw:: html

   <h1 align="center">

oceandb-bigchaindb-driver

.. raw:: html

   </h1>

..

    🐳 Ocean DB BigchainDB driver (Python).

.. |banner| image:: doc/img/repo-banner@2x.png
   :target: https://oceanprotocol.com

.. image:: https://img.shields.io/pypi/v/oceandb-bigchaindb-driver.svg
        :target: https://pypi.python.org/pypi/oceandb-bigchaindb-driver

.. image:: https://img.shields.io/travis/oceanprotocol/oceandb-bigchaindb-driver.svg
        :target: https://travis-ci.com/oceanprotocol/oceandb-bigchaindb-driver

.. image:: https://readthedocs.org/projects/oceandb-plugin-system/badge/?version=latest
        :target: https://oceandb-plugin-system.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/oceanprotocol/oceandb-bigchaindb-driver/shield.svg
     :target: https://pyup.io/repos/github/oceanprotocol/oceandb-bigchaindb-driver/
     :alt: Updates



BigchainDB driver to connect implementing OceanDB.

* Free software: Apache Software License 2.0
* Documentation: https://oceandb-plugin-system.readthedocs.io.


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

    enabled=true
    #location of plugin class
    module=bdb
    module.path=./oceandb_bigchaindb_driver/plugin.py
    db.hostname=localhost
    db.port=9984
    db.namespace=name
    db.app_id=
    db.app_key=
..

Once you have defined this the only thing that you have to do it is use it:

.. code-block:: python

    oceandb = OceanDb(conf)
    oceandb.write({"value": "test"})

..

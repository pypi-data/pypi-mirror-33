#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oceandb_driver_interface.oceandb import OceanDb

bdb = OceanDb('./tests/oceandb.ini').plugin


def test_plugin_type_is_bdb():
    assert bdb.type == 'BigchainDB'


def test_plugin_write_and_read():
    tx_id = bdb.write({"value": "plugin"})
    assert bdb.read(tx_id)['data']['data']['value'] == 'plugin'
    bdb.delete(tx_id)


def test_update():
    tx_id = bdb.write({"value": "test"})
    assert bdb.read(tx_id)['data']['data']['value'] == 'test'
    bdb.update({"value": "testUpdated"}, tx_id)
    bdb.update({"value": "testUpdated2"}, tx_id)
    assert bdb.read(tx_id)['data']['data']['value'] == 'testUpdated2'
    bdb.delete(tx_id)


def test_plugin_list():
    tx1 = bdb.write({"value": "test1"})
    bdb.update({"value": "testUpdated"}, tx1)
    tx2 = bdb.write({"value": "test2"})
    tx3 = bdb.write({"value": "test3"})
    assert len(bdb.list()) == 3
    assert bdb.list()[0]['data']['data']['value'] == 'testUpdated'
    bdb.delete(tx1)
    bdb.delete(tx2)
    bdb.delete(tx3)
    assert len(bdb.list()) == 0


def test_plugin_query():
    tx_id = bdb.write({'example': 'BDB'})
    assert bdb.query('BDB')[0]['data']['example'] == "BDB"
    bdb.delete(tx_id)

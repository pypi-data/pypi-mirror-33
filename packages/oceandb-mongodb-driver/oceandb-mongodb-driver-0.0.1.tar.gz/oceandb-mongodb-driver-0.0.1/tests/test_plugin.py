#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oceandb_driver_interface.oceandb import OceanDb

mongo = OceanDb('./tests/oceandb.ini').plugin


def test_plugin_type_is_mongodb():
    assert mongo.type == 'MongoDB'


def test_plugin_write_and_read():
    object_id = mongo.write({"id": 1, "value": "test"})
    assert mongo.read(object_id)['id'] == 1
    assert mongo.read(object_id)['value'] == 'test'
    mongo.delete(object_id)


def test_update():
    object_id = mongo.write({"id": 1, "value": "test"})
    assert mongo.read(object_id)['value'] == 'test'
    mongo.update(object_id, {"id": 1, "value": "testUpdated"})
    assert mongo.read(object_id)['value'] == 'testUpdated'
    mongo.delete(object_id)


def test_plugin_list():
    object_id1=mongo.write({"id": 1, "value": "test1"})
    object_id2=mongo.write({"id": 2, "value": "test2"})
    object_id3=mongo.write({"id": 3, "value": "test3"})
    assert mongo.list().count() == 3
    assert mongo.list()[0]['value'] == 'test1'
    mongo.delete(object_id1)
    mongo.delete(object_id2)
    mongo.delete(object_id3)

def test_plugin_query():
    object_id=mongo.write({"id": 1, 'example': 'mongo'})
    assert mongo.query({'example': 'mongo'})[0]['example'] == "mongo"
    mongo.delete(object_id)

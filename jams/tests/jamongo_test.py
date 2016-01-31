from bson.objectid import ObjectId
import mongomock
from nose.tools import raises, eq_

import jams
from jams.jamongo import JamsMongo, convert_annotation_list


def test_local_jamsmongo():
    """TODO: Is this a bad idea?
    Maybe you don't want to have these tests rely on
    a local mongo instance."""
    mongo = JamsMongo()
    assert mongo is not None


def test_remote_jamsmongo():
    """TODO: Is this test useful? Don't know
    what you would actually connect to, but it would
    be nice to make sure you can do it."""
    connection_str = "mongodb://foo.bar.com:27017"
    mongo = JamsMongo(connection_str)
    assert mongo.connection_str == connection_str


def test_mock_jamsmongo():
    mongo = JamsMongo(client=mongomock.MongoClient())
    assert mongo is not None


def test_context_manager():

    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        assert mongo.db is not None

        assert isinstance(mongo.audio, mongomock.Collection)
        assert isinstance(mongo.annotations, mongomock.Collection)

        yield raises(KeyError)(mongo.__getattr__), "fred"


def test_insert_jams_metadata():
    def __test(collection, new_id, expected):
        result = collection.find_one(new_id,
                                     projection={'_id': False})

        eq_(result, expected)

    # Load an example jam
    fn = 'fixtures/valid.jams'
    jam = jams.load(fn)
    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        new_id = mongo.insert_jams_metadata(jam.file_metadata)

        yield __test, mongo.audio, new_id, jam.file_metadata.__json__


def test_convert_annotation_list():
    def __test(input_annotations, result):
        # TODO: What goes here?
        assert isinstance(result, list)

    fn = 'fixtures/valid.jams'
    jam = jams.load(fn)

    garbage_id = ObjectId()
    result = convert_annotation_list(jam.annotations, garbage_id)

    yield __test, jam.annotations, result


def test_insert_annotations():
    def __test(collection, input_list, ids):
        cursor = collection.find({
            "_id": {"$in": ids}},
            projection={"_id": False})

        assert cursor.count() == len(input_list)

    garbage_annotations = [
        dict(garbage="in"),
        dict(garbage="out")
    ]

    with JamsMongo(client=mongomock.MongoClient()) as mongo:
        new_ids = mongo.insert_annotations(garbage_annotations)

        yield __test, mongo.annotations, garbage_annotations, new_ids


def test_build_pivot_map():
    pass


def test_import_jams():
    """Test the end-to-end"""
    pass

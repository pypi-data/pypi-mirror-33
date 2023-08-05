# pylint: disable=invalid-name
from parameterized import parameterized

import pytest

from anji_orm import Model, StringField, BooleanField, IntField, DictField

from .base import CouchDBTestCase


class T1(Model):

    _table = 'non_table'

    c1 = IntField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = StringField()
    c4 = StringField(secondary_index=True)
    c5 = BooleanField()
    c6 = StringField()
    c7 = DictField()


@pytest.mark.couchdb
class QueryTestCase(CouchDBTestCase):

    @parameterized.expand([
        [T1.c3.one_of(1, 2), {"c3": {"$in": (1, 2)}}],
        [T1.c3 == 1, {"c3": {"$eq": 1}}],
        [T1.c3 > 1, {"c3": {"$gt": 1}}],
        [T1.c3 >= 1, {"c3": {"$gte": 1}}],
        [T1.c3 < 1, {"c3": {"$lt": 1}}],
        [T1.c3 <= 1, {"c3": {"$lte": 1}}],
        [T1.c3 != 1, {"c3": {"$ne": 1}}],
        [(T1.c3 <= 10) & (T1.c3 >= 5), {"c3": {"$lte": 10, "$gte": 5}}],
        [(T1.c3 < 10) & (T1.c3 >= 5), {"c3": {"$lt": 10, "$gte": 5}}],
        [(T1.c3 <= 10) & (T1.c3 > 5), {"c3": {"$lte": 10, "$gt": 5}}],
        [(T1.c3 < 10) & (T1.c3 > 5), {"c3": {"$lt": 10, "$gt": 5}}],
    ])
    def test_simple_build(self, query, selector):
        build_result = query.build_query()
        self.assertEqual(build_result["json"]["selector"], selector)
        self.assertEqual(build_result["url"], f"{T1._table}/_find")
        self.assertEqual(build_result["method"], "post")

    @parameterized.expand([
        [T1.c5 & (T1.c3 == 5), {"c5": {"$eq": True}, "c3": {"$eq": 5}}],
        [(T1.c3 == 5) & T1.c5, {"c5": {"$eq": True}, "c3": {"$eq": 5}}],
        [T1.c5 & (T1.c3 == 5) & (T1.c6 > 5), {"c5": {"$eq": True}, "c3": {"$eq": 5}, "c6": {"$gt": 5}}],
        [(T1.c3 == 5) & (T1.c6 > 5) & T1.c5, {"c5": {"$eq": True}, "c3": {"$eq": 5}, "c6": {"$gt": 5}}],
        [T1.c5.false() & (T1.c3 == 5), {"c5": {"$eq": False}, "c3": {"$eq": 5}}],
    ])
    def test_boolean_convert(self, query, selector):
        build_result = query.build_query()
        self.assertEqual(build_result["json"]["selector"], selector)
        self.assertEqual(build_result["url"], f"{T1._table}/_find")
        self.assertEqual(build_result["method"], "post")

    def test_table_query(self):
        build_result = T1.all().build_query()
        self.assertEqual(build_result["url"], f"{T1._table}/_find")
        self.assertEqual(build_result["method"], "post")
        self.assertEqual(build_result["json"]["selector"], {"_id": {"$gt": None}})

    @parameterized.expand([
        [T1.c7.c1 == 6, {"c7.c1": {"$eq": 6}}],
        [(T1.c7.c1 == 6) & (T1.c7.c2 > 5), {"c7.c1": {"$eq": 6}, "c7.c2": {"$gt": 5}}],
        [(T1.c7.c1 >= 6) & (T1.c7.c1 <= 10), {"c7.c1": {"$gte": 6, "$lte": 10}}],
    ])
    def test_nested_build(self, query, selector):
        build_result = query.build_query()
        self.assertEqual(build_result["json"]["selector"], selector)
        self.assertEqual(build_result["url"], f"{T1._table}/_find")
        self.assertEqual(build_result["method"], "post")

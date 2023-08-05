# pylint: disable=invalid-name
from parameterized import parameterized

import pytest

from anji_orm import Model, StringField, BooleanField

from .base import CouchDBTestCase


class T1(Model):

    _table = 'non_table'

    c1 = StringField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = StringField()
    c4 = StringField(secondary_index=True)
    c5 = BooleanField()


@pytest.mark.couchdb
class SamplingTest(CouchDBTestCase):

    def test_limit_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post',
                'json': {'selector': {'c1': {'$eq': 5}}, 'limit': 2}
            },
            (T1.c1 == 5).limit(2).build_query()
        )

    def test_skip_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post',
                'json': {'selector': {'c1': {'$eq': 5}}, 'skip': 2}
            },
            (T1.c1 == 5).skip(2).build_query()
        )

    def test_sample_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post', 'json': {'selector': {'c1': {'$eq': 5}}, 'limit': 10},
                '_context': {'post_processors': [None]}
            },
            (T1.c1 == 5).sample(2).build_query()
        )

    def test_complex_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post',
                'json': {'selector': {'c1': {'$eq': 5}}, 'limit': 10, 'skip': 3},
                '_context': {'post_processors': [None]}
            },
            (T1.c1 == 5).limit(10).skip(3).sample(2).build_query()
        )


@pytest.mark.couchdb
class OrderByTestCase(CouchDBTestCase):

    @parameterized.expand([
        (
            {
                'url': 'non_table/_find', 'method': 'post',
                'json': {'selector': {'c1': {'$eq': 5}}, 'sort': ['c2']},
            },
            (T1.c1 == 5).order_by(T1.c2.amount)
        ),
        (
            {
                'url': 'non_table/_find', 'method': 'post',
                'json': {'selector': {'c1': {'$eq': 5}}, 'sort': ['c3']},
            },
            (T1.c1 == 5).order_by(T1.c3.amount)
        ),
        (
            {
                'url': 'non_table/_find', 'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'sort': ['c2', 'c4']},
            },
            T1.all().order_by(T1.c2.amount, T1.c4.amount)
        ),
        (
            {
                'url': 'non_table/_find', 'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'sort': ['c2', 'c4', 'c3']},
            },
            T1.all().order_by(T1.c2.amount, T1.c4.amount, T1.c3.amount)
        ),
        (
            {
                'url': 'non_table/_find', 'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'sort': ['c4', 'c3', 'c2']},
            },
            T1.all().order_by(T1.c4.amount, T1.c3.amount, T1.c2.amount)
        )
    ])
    def test_order_sampling(self, target_query, ast_expr):
        self.assertQueryEqual(
            target_query,
            ast_expr.build_query()
        )


@pytest.mark.couchdb
class TableSamplingTest(CouchDBTestCase):

    def test_limit_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'limit': 2},
            },
            T1.all().limit(2).build_query()
        )

    def test_skip_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find', 'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'skip': 2},
            },
            T1.all().skip(2).build_query()
        )

    def test_sample_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'limit': 10},
                '_context': {'post_processors': [None]}
            },
            T1.all().sample(2).build_query()
        )

    def test_complex_sampling(self):
        self.assertQueryEqual(
            {
                'url': 'non_table/_find',
                'method': 'post',
                'json': {'selector': {'_id': {'$gt': None}}, 'limit': 10, 'skip': 3},
                '_context': {'post_processors': [None]}
            },
            T1.all().limit(10).skip(3).sample(2).build_query()
        )

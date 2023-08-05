# pylint: disable=invalid-name,singleton-comparison
import rethinkdb as R

from parameterized import parameterized
import pytest

from anji_orm import Model, StringField, BooleanField, DictField

from .base import RethinkDBTestCase


class T1(Model):

    _table = 'non_table'

    c1 = StringField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = StringField()
    c4 = StringField(secondary_index=True)
    c5 = BooleanField()
    c6 = DictField()


@pytest.mark.rethinkdb
class AggregatioTestCase(RethinkDBTestCase):

    @parameterized.expand([
        [
            R.table(T1._table).get_field('c6').get_field('c2').min(),
            T1.all().min(T1.c6.c2)
        ],
        [
            R.table(T1._table).get_field('c6').get_field('c3').max(),
            T1.all().max(T1.c6.c3)
        ],
        [
            R.table(T1._table).count(),
            T1.all().count()
        ],
        [
            R.table(T1._table).get_field('c6').get_field('t2').avg(),
            T1.all().avg(T1.c6.t2)
        ],
        [
            R.table(T1._table).get_field('c6').get_field('t2').sum(),
            T1.all().sum(T1.c6.t2)
        ],
        [
            R.table(T1._table).get_all(3, index='c1').filter(R.row['c3'] > 5).get_field('c6').get_field('t2').sum(),
            ((T1.c1 == 3) & (T1.c3 > 5)).sum(T1.c6.t2)
        ],
    ])
    def test_aggregation_query(self, target_query, ast_expr):
        self.assertQueryEqual(
            ast_expr.build_query(),
            target_query
        )


@pytest.mark.rethinkdb
class GroupTestCase(RethinkDBTestCase):

    @parameterized.expand([
        (
            R.table(T1._table).group(R.row['c2']).count(),
            T1.all().group(T1.c2).count()
        ),
        (
            R.table(T1._table).group(R.row['c2']).get_field('c3').max(),
            T1.all().group(T1.c2).max(T1.c3)
        ),
    ])
    def test_group_query(self, target_query, ast_expr):
        self.assertQueryEqual(
            ast_expr.build_query(),
            target_query
        )

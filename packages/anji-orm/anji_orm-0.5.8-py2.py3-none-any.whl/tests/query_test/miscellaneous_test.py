# pylint: disable=singleton-comparison
from parameterized import parameterized

from anji_orm import Model, StringField, BooleanField

from ..base import BaseTestCase


class T1(Model):

    _table = 'non_table'

    c1 = StringField()
    c2 = StringField()
    c3 = BooleanField()


class MiscellaneousTestCase(BaseTestCase):

    @parameterized.expand([
        (T1.c1, T1),
        (T1.c1 >= 5, T1),
        (T1.c1 > 5, T1),
        (T1.c1 <= 5, T1),
        (T1.c1 < 5, T1),
        (T1.c1 == 5, T1),
        (T1.c1 != 5, T1),
        ((T1.c1 >= 5) & (T1.c1 < 6), T1),
        ((T1.c1 >= 5) & (T1.c1 < 6) & (T1.c1 >= 5.3) & (T1.c1 < 5.5), T1)
    ])
    def test_model_ref(self, query, model):
        self.assertEqual(query.model_ref, model)

    @parameterized.expand([
        (T1.c3 & (T1.c1 >= 5), (T1.c3 == True) & (T1.c1 >= 5)),
        (~T1.c3 & (T1.c1 >= 5), (T1.c3 == False) & (T1.c1 >= 5)),
        (T1.c3.false() & (T1.c1 >= 5), (T1.c3 == False) & (T1.c1 >= 5)),
    ])
    def test_boolean_convert(self, implict_query, explict_query):
        self.assertEqual(implict_query, explict_query)

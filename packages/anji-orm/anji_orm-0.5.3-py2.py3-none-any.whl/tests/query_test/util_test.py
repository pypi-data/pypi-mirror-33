from enum import Enum
import unittest

from parameterized import parameterized

from anji_orm import Model, StringField, EnumField


class NotPrettyEnum(Enum):

    first = 'first'
    second = 'second'


class T1(Model):

    _table = 'non_table'

    c1 = StringField()
    c2 = StringField()
    c3 = EnumField(NotPrettyEnum)


class QueryUtilTest(unittest.TestCase):

    @parameterized.expand([
        [T1.c1 == T1.c2],
        [(T1.c1 == '5') & (T1.c2 == '6')],
        [(T1.c1 == T1.c2) & (T1.c2 == '6')],
        [(T1.c1 == T1.c2) & (T1.c1 == '6')]
    ])
    def test_true_complicated(self, query):
        self.assertTrue(query.complicated)

    @parameterized.expand([
        [T1.c1 == '5'],
        [(T1.c1 == '5') & (T1.c1 == '6')]
    ])
    def test_false_compicated(self, query):
        self.assertFalse(query.complicated)

    @parameterized.expand([
        (
            (NotPrettyEnum.first.name, NotPrettyEnum.second.name),
            T1.c1.one_of(NotPrettyEnum.first, NotPrettyEnum.second)
        ),
        (NotPrettyEnum.first.name, T1.c1 == NotPrettyEnum.first),
        (NotPrettyEnum.first.name, T1.c1 >= NotPrettyEnum.first),
        (NotPrettyEnum.first.name, T1.c1 <= NotPrettyEnum.first),
        (NotPrettyEnum.first.name, T1.c1 > NotPrettyEnum.first),
        (NotPrettyEnum.first.name, T1.c1 < NotPrettyEnum.first),
        (NotPrettyEnum.first.name, T1.c1 != NotPrettyEnum.first)
    ])
    def test_check_prettify_for_enum(self, enum, query):
        self.assertEqual(enum, query.right)

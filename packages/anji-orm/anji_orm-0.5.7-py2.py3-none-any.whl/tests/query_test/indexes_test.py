import unittest

from parameterized import parameterized

from anji_orm.core.indexes import (
    similar_part_iterator, IndexPolicy, IndexPolicySettings, IndexPolicySetting,
    is_subset
)
from anji_orm import Model, StringField


class T1(Model):

    _index_policy_settings: IndexPolicySettings = {
        IndexPolicySetting.only_single_index: ('c5',),
        IndexPolicySetting.additional_indexes: [
            ('c1:c2:c3', ['c1', 'c2', 'c3']),
            ('c1:c5:c3', ['c1', 'c5', 'c3'])
        ]
    }

    c1 = StringField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = StringField(secondary_index=True)
    c4 = StringField(secondary_index=True)
    c5 = StringField(secondary_index=True)


class T2(Model):

    c1 = StringField()
    c2 = StringField()


class UtilityTestCase(unittest.TestCase):

    def test_part_iterator(self):
        first = list(range(0, 10))
        second = list(range(0, 5)) + list(range(20, 30))
        self.assertEqual(
            list(similar_part_iterator(first, second)),
            list(range(0, 5))
        )

    @parameterized.expand([
        ([1, 2, 3], [1, 4, 3, 2], False, True),
        ([1, 2, 3], [1, 4, 3, 2], True, False),
        ([1, 2, 4], [1, 2, 3, 5], True, False),
        ([1, 2, 4], [1, 2, 3, 5], False, False),
    ])
    def test_subset_function(self, first, second, ordered, answer):
        self.assertEqual(
            is_subset(first, second, ordered=ordered),
            answer
        )


class GreedyTestCase(unittest.TestCase):

    @parameterized.expand([
        (['c1', 'c2', 'c3'], 'c1:c2:c3', [], False),
        (['c1', 'c2', 'c4', 'c3'], 'c1:c2', ['c4', 'c3'], True),
        (['c1', 'c2', 'c3', 'c4'], 'c1:c2:c3:c4', [], True),
        (['c1', 'c2', 'c4'], 'c1:c2:c4', [], True),
        (['c1', 'c2', 'c4'], 'c1:c2:c4', [], False),
    ])
    def test_index_selecting(self, fields, target_selected_index, target_rest, ordered):
        selected_index, rest = IndexPolicy.greedy.value.select_secondary_index(  # pylint: disable=no-member
            T1, fields, ordered=ordered
        )
        self.assertEqual(selected_index, target_selected_index)
        self.assertEqual(rest, target_rest)

    @parameterized.expand([
        [T2, [('_schema_version', ['_schema_version'])]]
    ])
    def test_index_build(self, model, index_list):
        self.assertEqual(
            IndexPolicy.greedy.value.build_index_list(model),  # pylint: disable=no-member
            index_list
        )


class GreedylessTestCase(unittest.TestCase):

    @parameterized.expand([
        (['c1', 'c2', 'c3'], 'c1:c2:c3', [], False),
        (['c1', 'c2', 'c4', 'c3'], 'c1:c2', ['c4', 'c3'], True),
        (['c1', 'c2', 'c3', 'c4'], 'c1:c2:c3:c4', [], True),
        (['c1', 'c2', 'c4'], 'c1:c2:c4', [], True),
        (['c1', 'c2', 'c4'], 'c1:c2:c4', [], False),
        (['c1', 'c2', 'c5'], 'c5', ['c1', 'c2'], False),
        (['c1', 'c2', 'c5'], 'c1:c2', ['c5'], True),
        (['c1', 'c2', 'c5', 'c4'], 'c1:c2', ['c5', 'c4'], True),
    ])
    def test_index_selecting(self, fields, target_selected_index, target_rest, ordered):
        selected_index, rest = IndexPolicy.greedyless.value.select_secondary_index(  # pylint: disable=no-member
            T1, fields, ordered=ordered
        )
        self.assertEqual(selected_index, target_selected_index)
        self.assertEqual(rest, target_rest)

    @parameterized.expand([
        [T2, [('_schema_version', ['_schema_version'])]]
    ])
    def test_index_build(self, model, index_list):
        self.assertEqual(
            IndexPolicy.greedyless.value.build_index_list(model),  # pylint: disable=no-member
            index_list
        )


class SingleIndedPolicyTestCase(unittest.TestCase):

    @parameterized.expand([
        (['c1', 'c2', 'c3'], 'c1', ['c2', 'c3'], False),
        (['c1', 'c3', 'c2'], 'c1', ['c3', 'c2'], True),
    ])
    def test_index_selecting(self, fields, target_selected_index, target_rest, ordered):
        selected_index, rest = IndexPolicy.single.value.select_secondary_index(  # pylint: disable=no-member
            T1, fields, ordered=ordered
        )
        self.assertEqual(selected_index, target_selected_index)
        self.assertEqual(rest, target_rest)

    @parameterized.expand([
        [T2, [('_schema_version', ['_schema_version'])]]
    ])
    def test_index_build(self, model, index_list):
        self.assertEqual(
            IndexPolicy.single.value.build_index_list(model),  # pylint: disable=no-member
            index_list
        )


class SinglemorePolicyTestCase(unittest.TestCase):

    @parameterized.expand([
        (['c1', 'c2', 'c4'], 'c1', ['c2', 'c4'], False),
        (['c1', 'c3', 'c4'], 'c1', ['c3', 'c4'], True),
        (['c1', 'c5', 'c3'], 'c1:c5:c3', [], True),
        (['c1', 'c3', 'c5'], 'c1', ['c3', 'c5'], True),
        (['c1', 'c5', 'c3'], 'c1:c5:c3', [], False),
        (['c1', 'c3', 'c5'], 'c1:c5:c3', [], False),
    ])
    def test_index_selecting(self, fields, target_selected_index, target_rest, ordered):
        selected_index, rest = IndexPolicy.singlemore.value.select_secondary_index(  # pylint: disable=no-member
            T1, fields, ordered=ordered
        )
        self.assertEqual(selected_index, target_selected_index)
        self.assertEqual(rest, target_rest)

    @parameterized.expand([
        [T2, [('_schema_version', ['_schema_version'])]]
    ])
    def test_index_build(self, model, index_list):
        self.assertEqual(
            IndexPolicy.singlemore.value.build_index_list(model),  # pylint: disable=no-member
            index_list
        )

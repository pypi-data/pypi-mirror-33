from anji_orm import Model, StringField, DatetimeField, DictField, IndexPolicy, IndexPolicySetting


class T1(Model):

    _table = 'test_table'

    _index_policy = IndexPolicy.singlemore
    _index_policy_settings = {
        IndexPolicySetting.additional_indexes: [
            ('c1:c2', ['c1', 'c2'])
        ]
    }

    c1 = StringField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = DatetimeField()
    c4 = DictField()
    c5 = StringField()

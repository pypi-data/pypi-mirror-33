from anji_orm import Model, StringField, DatetimeField, DictField


class T1(Model):

    _table = 'test_table'

    c1 = StringField(secondary_index=True)
    c2 = StringField(secondary_index=True)
    c3 = DatetimeField()
    c4 = DictField()
    c5 = StringField()

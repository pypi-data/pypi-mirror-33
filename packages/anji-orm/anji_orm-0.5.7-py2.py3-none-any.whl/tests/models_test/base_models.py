from enum import Enum

from anji_orm import EnumField, Model, StringField


class BaseEnum(Enum):

    first = 'first'
    second = 'second'
    magic = 'magic'


class BaseModel(Model):

    _table = 'not_base_table'

    test_field_3 = StringField(definer=True, secondary_index=True)
    test_field_1 = StringField()
    test_field_2 = StringField()


class BaseModelWithEnum(Model):

    _table = 'non_table'

    enum_field = EnumField(BaseEnum)
    test_field = StringField()

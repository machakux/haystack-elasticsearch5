from haystack.fields import SearchField


class DictField(SearchField):
    field_type = 'dict'

    def prepare(self, obj):
        return self.convert(super(DictField, self).prepare(obj))

    def convert(self, value):
        if value is None:
            return None
        return dict(value)

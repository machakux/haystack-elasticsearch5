from haystack.query import SearchQuerySet as BaseSearchQuerySet


class SearchQuerySet(BaseSearchQuerySet):

    def boost_fields(self, fields):
        """Boosts fields."""
        clone = self._clone()
        clone.query.add_boost_fields(fields)
        return clone

    def filter(self, *args, **kwargs):
        clone = self._clone()
        if args:
            return super(SearchQuerySet, self).filter(*args, **kwargs)
        clone.query.add_filter_context(**kwargs)
        return clone

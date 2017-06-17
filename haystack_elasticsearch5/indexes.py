# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import threading

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text
from django.utils.six import with_metaclass

from haystack.manager import SearchIndexManager
from haystack.indexes import *

from .fields import *


class Elasticsears5DeclarativeMetaclass(DeclarativeMetaclass):

    def __new__(cls, name, bases, attrs):
        attrs['fields'] = {}

        # Inherit any fields from parent(s).
        try:
            parents = [b for b in bases if issubclass(b, SearchIndex)]
            # Simulate the MRO.
            parents.reverse()

            for p in parents:
                fields = getattr(p, 'fields', None)

                if fields:
                    attrs['fields'].update(fields)
        except NameError:
            pass

        # Build a dictionary of faceted fields for cross-referencing.
        facet_fields = {}

        for field_name, obj in attrs.items():
            # Only need to check the FacetFields.
            if hasattr(obj, 'facet_for'):
                if not obj.facet_for in facet_fields:
                    facet_fields[obj.facet_for] = []

                facet_fields[obj.facet_for].append(field_name)

        built_fields = {}

        for field_name, obj in attrs.items():
            if isinstance(obj, SearchField):
                field = attrs[field_name]
                field.set_instance_name(field_name)
                built_fields[field_name] = field

        attrs['fields'].update(built_fields)

        # Assigning default 'objects' query manager if it does not already exist
        if not 'objects' in attrs:
            try:
                attrs['objects'] = SearchIndexManager(attrs['Meta'].index_label)
            except (KeyError, AttributeError):
                attrs['objects'] = SearchIndexManager(DEFAULT_ALIAS)

        return type.__new__(cls, name, bases, attrs)

DeclarativeMetaclass = Elasticsears5DeclarativeMetaclass


class Elasticsearch5SearchIndex(SearchIndex, with_metaclass(DeclarativeMetaclass, threading.local)):
    pass

SearchIndex = Elasticsearch5SearchIndex


class BasicSearchIndex(SearchIndex):
    text = CharField(document=True, use_template=True)


class Elasticsearch5ModelSearchIndex(ModelSearchIndex, SearchIndex):
    pass

ModelSearchIndex = Elasticsearch5ModelSearchIndex

try:
    from celery_haystack.indexes import CelerySearchIndex

    class Elasticsearch5CelerySearchIndex(CelerySearchIndex, SearchIndex):
        pass

    CelerySearchIndex = Elasticsearch5CelerySearchIndex
except ImportError:
    pass

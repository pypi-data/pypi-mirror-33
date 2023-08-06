# -*- coding:utf-8 -*-
from django.utils.encoding import force_text
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import RelatedField, SlugRelatedField, ManyRelatedField

__author__ = 'denishuang'


class RelatedChoicesMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(RelatedChoicesMetadata, self).get_field_info(field)
        # print field, hasattr(field, 'queryset'),isinstance(field, (RelatedField, ManyRelatedField)),field_info.get('read_only')
        if (not field_info.get('read_only') and isinstance(field, (RelatedField, ManyRelatedField))):
            if isinstance(field, ManyRelatedField):
                field = field.child_relation
                field_info['multiple'] = True
            if not hasattr(field, "queryset"):
                return field_info
            qset = field.queryset
            # if qset.count() < 1000:
            #     # print field
            #     field_info['choices'] = [
            #         {
            #             'value': r.pk,
            #             'display_name': unicode(r)
            #         }
            #         for r in qset.all()
            #         ]
            field_info['model'] = qset.model._meta.label_lower
        return field_info

    def determine_actions(self, request, view):
        actions = super(RelatedChoicesMetadata, self).determine_actions(request, view)
        search_fields = getattr(view, 'search_fields', [])
        from ..utils import modelutils
        cf = lambda f: f[0] in ['^', '@', '='] and f[1:] or f
        actions['SEARCH'] = search = {}
        search['search_fields'] = [modelutils.get_related_field_verbose_name(view.queryset.model, cf(f)) for f in
                                   search_fields]
        from django_tables2.utils import A
        ffs = A('filter_class._meta.fields').resolve(view, quiet=True) or getattr(view, 'filter_fields', [])
        search['filter_fields'] = isinstance(ffs, dict) and ffs.keys() or ffs
        search['ordering_fields'] = getattr(view, 'ordering_fields', [])
        return actions


class RelatedSlugMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(RelatedSlugMetadata, self).get_field_info(field)

        if (not field_info.get('read_only') and
                isinstance(field, SlugRelatedField) and
                hasattr(field, 'queryset')):
            qset = field.queryset
            from django.shortcuts import reverse
            field_info['list_url'] = reverse('%s-list' % qset.model._meta.model_name)
            field_info['slug_field'] = field.slug_field
        return field_info

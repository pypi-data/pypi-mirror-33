"""Tools for model using MongoEngine"""
from bson.dbref import DBRef
from bson.objectid import ObjectId
from datetime import datetime
from flask import abort
from mongoengine import EmbeddedDocument, DateTimeField, ImageGridFsProxy
from flask_mongoengine import Document
from mongoengine.base import EmbeddedDocumentList, BaseList


class ValidatorMixin(object):
    @classmethod
    def check_list(cls, data, fields=None):
        return [cls.check(item, fields) for item in data]

    @classmethod
    def check(cls, data, fields=None, silence_unknown_fields=True):
        if isinstance(fields, str):
            fields = fields.split(',')

        if fields is None:
            fields = cls._fields_ordered

        fields = set(fields)

        if not silence_unknown_fields:
            sent_fields = set(data.keys())
            diff = sent_fields - fields
            if len(diff) > 0:
                abort(400, 'Unknown fields: {}'.format(diff))

        cleaned_data = {}

        for field_name in fields:
            field_obj = getattr(cls, field_name)
            field_value = data.get(field_name)

            if field_value is None and not field_obj.required:
                continue

            try:
                field_obj.validate(field_value)
            except Exception as e:
                abort(400, 'Field: {}. Value: {}. Error: {}'.format(field_name, field_value, e))

            cleaned_data[field_name] = field_value

        return cleaned_data


class DictMixin(object):
    @classmethod
    def to_list_dict(cls, queryset_manager, fields=None, excluded=None, prefetch=None):
        res = []
        for item in queryset_manager:
            res.append(item.to_dict(fields, excluded, prefetch))

        return res

    def to_dict(self, fields=None, excluded=None, prefetch=None):
        """Convert object to dict

        :param fields: (list, str) - If fields is given then convert only precised fields
                                    Exp: 'id,name,created_at' or ['id', 'name', 'created_at']
                                    Support deep fields: 'id,user.password'
        :param excluded: (list, str) - Syntax is the same as fields but used for excluding fields.
        :param prefetch: whether convert or not related field to dict
        """

        if isinstance(prefetch, str):
            prefetch = prefetch.split(',')

        if isinstance(fields, str):
            fields = fields.split(',')

        if isinstance(excluded, str):
            excluded = excluded.split(',')

        fields = fields or self._fields_ordered

        # Get deep excluded: example: user.encrypted_password
        deep_excluded = {}
        if excluded:
            fields = [f for f in fields if f not in excluded]

            for e in excluded:
                if '.' not in e:
                    continue

                deep_name, deep_attr = e.split('.', 1)

                if deep_name not in deep_excluded:
                    deep_excluded[deep_name] = []

                deep_excluded[deep_name].append(deep_attr)

        # Get deep fields: example: user.id
        deep_fields = {}
        for f in fields:
            if '.' not in f:
                continue

            deep_name, deep_attr = f.split('.', 1)

            if deep_name not in deep_fields:
                deep_fields[deep_name] = []

            deep_fields[deep_name].append(deep_attr)

        # Rebuild level 1 fields if there is deep fields
        fields = [f for f in fields if '.' not in f]
        fields.extend(deep_fields.keys())

        d = {}
        for f in fields:
            attr = self._data.get(f, getattr(self, f))

            if isinstance(attr, DBRef):
                if prefetch and f in prefetch:
                    attr = getattr(self, f).to_dict()
                else:
                    attr = attr.id

            # Convert field that can not be jsonify
            elif isinstance(attr, EmbeddedDocumentList):
                attr = [a.to_dict() for a in attr]

            # In case of ListField(ReferenceField)
            # TODO: Handle fields, excludes for this case
            elif isinstance(attr, BaseList) and len(attr) > 0 and isinstance(attr[0], Model):
                attr = [a.to_dict() for a in attr]

            elif isinstance(attr, ObjectId):
                attr = str(attr)

            elif isinstance(attr, ImageGridFsProxy):
                attr = str(attr.grid_id)

            elif isinstance(attr, Model):
                if prefetch and f in prefetch:
                    attr = attr.to_dict(
                        fields=deep_fields.get(f),
                        excluded=deep_excluded.get(f)
                    )
                else:
                    attr = str(attr.id)

            d[f] = attr

        return d


class Model(Document, ValidatorMixin, DictMixin):
    meta = {
        'abstract': True
    }

    @classmethod
    def get_or_404(cls, **kwargs):
        try:
            obj = cls.objects.get(**kwargs)
            return obj
        except cls.DoesNotExist:
            abort(404, '{} not found'.format(cls.__name__))


class TimestampedModel(Model):
    meta = {
        'abstract': True
    }

    updated_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)


class EmbeddedModel(EmbeddedDocument, ValidatorMixin, DictMixin):
    meta = {
        'abstract': True
    }

from typing import Dict, Any, Optional

from anji_orm import (
    ensure_element, StringField, BooleanField, DatetimeField, EnumField,
    IntField, FloatField, SelectionField, JsonField, DictField, ListField,
    QueryTable, QueryAst, Model
)
from sanic.request import Request
from sanic.response import json
from sanic_openapi import doc

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.3.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['DataTableMixin', 'OpenAPIDescriptionMixin']


SEARCH_TARGET_FIELD_MARK = 'search_target'


class DataTableMixin(Model):

    async def convert_to_web_info(self) -> Dict[str, Any]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and getattr(self, field_name) is not None:
                fields[field_item.name] = await field_item.async_format(getattr(self, field_name))
        return fields

    async def convert_to_json_data(self) -> Dict[str, Any]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and getattr(self, field_name) is not None:
                fields[field_item.name] = await ensure_element(getattr(self, field_name))
        fields['id'] = self.id
        return fields

    @classmethod
    def process_before_filter(cls, db_request: QueryAst, _request: Request) -> QueryAst:
        return db_request

    @classmethod
    def process_after_filter(cls, db_request: QueryAst, _request: Request) -> QueryAst:
        return db_request

    @classmethod
    def process_filter(cls, db_request: QueryAst, primary_key: Optional[str], request: Request) -> QueryAst:
        if 'filter' in request.args and primary_key is not None:
            if isinstance(db_request, QueryTable):
                return getattr(cls, primary_key).match(request.args.get('filter'))
            return db_request & getattr(cls, primary_key).match(request.args.get('filter'))
        return db_request

    @classmethod
    def process_sort(cls, db_request: QueryAst, request: Request) -> QueryAst:
        column_link = getattr(cls, request.args.get('sortColumn')).amount
        if request.args.get('sortDirection') == 'desc':
            column_link = column_link.desc
        return db_request.order_by(column_link)

    @classmethod
    def process_pager(cls, db_request: QueryAst, request: Request) -> QueryAst:
        page_index = int(request.args.get('pageIndex'))
        page_size = int(request.args.get('pageSize'))
        return db_request.skip(page_index * page_size).limit(page_size)

    @classmethod
    async def process_web_request(
            cls, request: Request,
            primary_key: str = None, prettify_response: bool = True) -> Dict[str, Any]:
        if not primary_key:
            primary_key = next(iter(cls._primary_keys), primary_key)
        db_request: QueryTable = cls.all()
        db_request = cls.process_before_filter(db_request, request)
        db_request = cls.process_filter(db_request, primary_key, request)
        db_request = cls.process_after_filter(db_request, request)
        total_count = await db_request.count().async_run()
        if 'sortColumn' in request.args:
            db_request = cls.process_sort(db_request, request)
        if 'pageIndex' in request.args and 'pageSize' in request.args:
            db_request = cls.process_pager(db_request, request)
        records = await db_request.async_run()
        if prettify_response:
            return json(
                {
                    'data': [await record.convert_to_web_info() for record in records],
                    'total': total_count
                }
            )
        return json(
            {
                'data': [await record.convert_to_json_data() for record in records],
                'total': total_count
            }
        )


class OpenAPIDescriptionMixin(Model):

    _doc_field_mapping = {
        StringField: doc.String,
        EnumField: doc.String,
        DatetimeField: doc.DateTime,
        BooleanField: doc.Boolean,
        IntField: doc.Integer,
        FloatField: doc.Float,
        SelectionField: doc.String,
        JsonField: doc.Dictionary,
        DictField: doc.Dictionary,
        ListField: doc.List,
    }
    _doc_additonal_arguments = {
        EnumField: lambda field: dict(choices=[x.value for x in field.variants]),
        SelectionField: lambda field: dict(choices=field.variants)
    }

    @classmethod
    def map_field(cls, field):
        if field.__class__ in cls._doc_field_mapping:
            doc_class = cls._doc_field_mapping[field.__class__]
            additional_arguments = {}
            if field.__class__ in cls._doc_additonal_arguments:
                additional_arguments = cls._doc_additonal_arguments[field.__class__](field)
            return doc_class(description=field.description, **additional_arguments)
        return doc.String(field.description)

    @classmethod
    def get_full_description(cls):
        if not hasattr(cls, '__openapi_full_description__'):
            cls.__openapi_full_description__ = type(cls.__name__, (), {
                field_name: OpenAPIDescriptionMixin.map_field(field)
                for field_name, field in cls._fields.items()
                if field.displayed
            })
        return cls.__openapi_full_description__

    @classmethod
    def get_description(cls):
        if not hasattr(cls, '__openapi_create_description__'):
            cls.__openapi_create_description__ = type(cls.__name__ + 'Data', (), {
                field_name: OpenAPIDescriptionMixin.map_field(field)
                for field_name, field in cls._fields.items()
                if field.displayed and (not field.default and not field.optional)
            })
        return cls.__openapi_create_description__

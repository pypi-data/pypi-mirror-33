import itertools
from functools import partial

import pgpy
import json
import re

from collections import Iterable, OrderedDict
from sanic.log import logger
from longitude.utils import is_list_or_tuple, allow_sync
from longitude import config
from longitude.exceptions import NotFound


class SQLFetchable:
    def fetch(self, *args, **kwargs):
        raise RuntimeError('not implemented')

    def get_conn(self):
        raise RuntimeError('not implemented')


class NotColumn:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return self.val


class SQLCRUDModel:

    table_name = None
    encoded_columns = tuple()
    select_columns = ('*',)
    simple_filters = tuple()
    simple_joins = {}
    group_by = tuple()

    formats = {
        'geojson': ('format_geojson_featurecollection', 'format_geojson_feature')
    }

    db_model = None
    db_conn = None

    def __init__(self, db_model: SQLFetchable, conn=None):
        self.db_model = db_model
        self.db_conn = conn

    @allow_sync
    async def list(self, joins=None, group_by=None, order_by=None, format=None, **filters):
        select_sql = self.select_sql(
            joins=joins,
            group_by=group_by,
            order_by=order_by,
            **filters
        )
        sql, params = self.placeholder_to_ordinal(*select_sql)

        ret = await self._fetch(sql, *params)

        return self.transform_objects(ret, format=format)

    @allow_sync
    async def count(self, **filters):
        return (await self.get(columns=(NotColumn('count(*)'),), **filters))['count']

    @allow_sync
    async def exists(self, **filters):
        return (await self.count(**filters)) > 0

    @allow_sync
    async def get(self, *args, joins=None, group_by=None, order_by=None, format=None, **filters):

        if len(args) == 1:
            filters['oid'] = args[0]
        elif len(args) > 1:
            raise TypeError('get() expected at most 1 arguments, got ' + len(args))

        select_sql = self.select_sql(
            joins=joins,
            group_by=group_by,
            order_by=order_by,
            **filters
        )
        sql, params = self.placeholder_to_ordinal(*select_sql)

        ret = await self._fetch(sql, *params)

        if len(ret) == 0:
            raise NotFound('Object not found')
        elif len(ret) > 1:
            raise AssertionError(
                'SQLCRUDModel.get can only return 0 or 1 '
                'elements.'
            )

        return self.transform_object(ret[0], format=format)

    @allow_sync
    async def upsert(self, values, pk=('id',), returning_columns=None):

        params = {}

        values = self.patch_insert_columns_encoded(values)
        values = self.patch_insert_columns(values)

        if returning_columns is None:
            returning_columns = self.select_columns

        insert_columns_snippet = []
        conflict_snippet = []
        values_snippet = []

        for key, val in values.items():

            if is_list_or_tuple(val, length=2):
                val, right_side_tpl = val
            else:
                right_side_tpl = '${}'

            param_name = self.add_param_name(key, val, params)
            insert_columns_snippet.append(key)
            conflict_snippet.append(('{}=' + right_side_tpl).format(key, param_name))
            values_snippet.append(right_side_tpl.format(param_name))

        sql = '''
            INSERT INTO {schema}{table} (
              {columns}
            ) VALUES (
              {values}
            )
            ON CONFLICT ({keys}) DO UPDATE SET
              {conflict}
            RETURNING {returning_columns}
        '''.format(
            schema=self.schema,
            table=self.table_name,
            columns=','.join(insert_columns_snippet),
            values=','.join(values_snippet),
            keys=','.join(pk),
            conflict=','.join(conflict_snippet),
            returning_columns=','.join(returning_columns)
        )

        sql, params = self.placeholder_to_ordinal(sql, params)

        ret = await self._fetch(sql, *params)

        return ret[0]

    @allow_sync
    async def delete(self, oid=None, **filters):

        if oid is not None:
            filters['oid'] = oid

        sql, params = self.placeholder_to_ordinal(*self.delete_sql(**filters))

        ret = await self._fetch(sql, *params)

        if len(ret) == 0:
            raise NotFound('Object not found')

        return {
            'results': ret
        }

    def select_sql(self, params=None, columns=None, joins=None, group_by=None, order_by=None, **filters):

        if columns is None:
            columns = self.select_columns

        if params is None:
            params = {}

        where_clause, params = self.where_sql(params, **filters)
        columns = [
            '_t.' + x if isinstance(x, str) and '.' not in x
            else x
            for x
            in columns
        ]

        all_joins = dict(self.simple_joins.items())
        all_joins.update(joins or {})

        if group_by is None:
            group_by = self.group_by

        if group_by is not None and group_by:
            group_by = 'GROUP BY ' + ','.join(group_by)
        else:
            group_by = ''

        if order_by is not None:
            order_by = 'ORDER BY ' + ','.join(order_by)
        else:
            order_by = ''

        return (
            '''
                SELECT 
                    {columns}
                FROM {schema}{table} _t
                {joins}
                WHERE {where_clause}
                {group_by}
                {order_by}
            '''.format(
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause,
                columns=','.join(str(x) for x in columns),
                joins='\n'.join(all_joins.values()),
                group_by=group_by,
                order_by=order_by
            ),
            params
        )

    def delete_sql(self, params=None, **filters):

        if params is None:
            params = {}

        where_clause, params = self.where_sql(params, **filters)

        return (
            '''
                DELETE FROM {schema}{table} _t
                WHERE {where_clause}
                RETURNING id
            '''.format(
                schema=self.schema,
                table=self.table_name,
                where_clause=where_clause
            ),
            params
        )

    def where_sql(self, params, **filters):

        simple_filters = []

        declared_filters = set(
            x[0] if isinstance(x, tuple)
                else x
            for x
            in self.simple_filters
        )

        if 'oid' not in declared_filters:
            simple_filters.append(('oid', '=%', '_t.id'))

        if 'oid__in' not in declared_filters:
            simple_filters.append(('oid__in', '= any(%::int[])', '_t.id'))

        simple_filters.extend(self.simple_filters)

        snippet = []

        for opts in simple_filters:
            if isinstance(opts, str):
                opts = (opts,)

            opts = list(opts)

            if len(opts) == 1:
                opts.append('=%')

            if len(opts) == 2:
                opts.append(opts[0])

            filter_name,\
            operator,\
            column_name = opts

            if filter_name in filters:
                filter_value = filters[filter_name]
                param_name = self.add_param_name(filter_name, filter_value, params)

                right_side = operator.replace('%', '${}'.format(param_name))

                snippet.append('{column_name}{right_side}'.format(
                    column_name=column_name if '.' in column_name else '_t.' + column_name,
                    right_side=right_side
                ))

        if not snippet:
            snippet = 'TRUE'
        else:
            snippet = ' AND '.join(snippet)

        return snippet, params

    async def query(self, sql, params={}):
        if isinstance(params, dict):
            sql, params = self.placeholder_to_ordinal(sql, params)

        return await self._fetch(sql, *params)

    async def _fetch(self, *args, **kwargs):
        ret = await self.db_model.fetch(*args, conn=self.db_conn, **kwargs)
        ret = self.decode_objects(ret)
        return ret

    def transform_objects(self, data, format=None):
        is_single = isinstance(data, dict)

        if is_single:
            data = [data]

        transformed_objects = []
        for obj in data:
            transformed_objects.append(self.transform_object(obj, format=format))

        if is_single:
            transformed_objects = transformed_objects[0]

        if format and format !='json' and format not in self.formats:
            raise RuntimeError('Format existing, allowed values: ' + ','.join(self.formats.keys()))
        elif format and format != 'json'  and isinstance(self.formats[format], tuple):
            transformed_objects = getattr(self, self.formats[format][0])(transformed_objects)
        else:
            transformed_objects = {
                'results': transformed_objects
            }

        return transformed_objects

    def transform_object(self, data, format=None):

        if format and format != 'json' and format not in self.formats:
            raise RuntimeError('Format existing, allowed values: ' + ','.join(self.formats.keys()))
        elif format and format != 'json' and isinstance(self.formats[format], tuple) and len(self.formats[format])>1:
            data = getattr(self, self.formats[format][1])(data)

        return data

    def format_geojson_featurecollection(self, data):
        return {
            'type': 'FeatureCollection',
            'features': data,
            'properties': {}
        }

    def format_geojson_feature(self, data):
        return {
            'type': 'Feature',
            'geometry': data.get('geom', None),
            'properties': OrderedDict(
                (k, v)
                for k, v
                in data.items()
                if k != 'geom'
            )
        }

    @property
    def schema(self):
        return config.DB_SCHEMA + '.' if config.DB_SCHEMA \
            else ''

    @classmethod
    def add_param_name(cls, name, value, params):

        if name in params:
            for i in itertools.count(1):
                name = name + str(i)
                if name not in params:
                    break

        params[name] = cls.prepare_value(value)

        return name

    @staticmethod
    def prepare_value(val):
        if isinstance(val, dict):
            val = json.dumps(val)

        return val

    def to_python(self, obj:dict):
        return obj

    @staticmethod
    def placeholder_to_ordinal(sql, params):
        ordinal_params = []

        named_params = list(sorted(params.keys(), key=lambda x: -len(x)))

        for named_param in named_params:
            if ('$' + named_param) in sql:
                sql = sql.replace('$' + named_param, '$' + str(len(ordinal_params) + 1))
                ordinal_params.append(params[named_param])

        return sql, ordinal_params

    def patch_insert_columns_encoded(self, data):
        for attr_name in self.encoded_columns:
            if attr_name in data and not is_list_or_tuple(data[attr_name], length=2):
                data[attr_name] = (data[attr_name], 'pgp_pub_encrypt(${}, dearmor(get_pgp_pubkey()))')

        return data

    def patch_insert_columns(self, values):

        values.pop('created_at', None)

        if any(re.match(r'^(_t\.)?updated_at$', x) for x in self.select_columns):
            values['updated_at'] = ('', 'CURRENT_TIMESTAMP')

        return values

    def decode_objects(self, data):

        if not config.PGP_PRIVATE_KEY:
            return data

        is_single = isinstance(data, dict)

        if is_single:
            data = [data]

        for obj in data:
            for encoded_attr in set(self.encoded_columns).intersection(obj.keys()):
                if obj[encoded_attr] is not None:
                    try:
                        db_crypted_attr = pgpy.PGPMessage.from_blob(obj[encoded_attr])
                        obj[encoded_attr] = config.PGP_PRIVATE_KEY[0].decrypt(db_crypted_attr).message
                    except ValueError as e:
                        obj[encoded_attr] = None
                        logger.warning(
                            "Couldn't decode attribute attribute %s of object with %s.%s: %s",
                            encoded_attr,
                            self.__class__.__name__,
                            str(obj.get('id', 'UNKNOWN')),
                            str(e)
                        )

        if is_single:
            data = data[0]

        return data

    @staticmethod
    def alias_conf(conf, alias=None):
        newconf = []
        for conf_elem in conf:
            if not alias:
                newconf.append(alias)
            elif isinstance(conf_elem, str):
                if '.' not in conf_elem:
                    newconf.append('{}.{}'.format(alias,conf_elem))
                elif '_t.' in conf_elem:
                    newconf.append(conf_elem.replace('_t.', '{}.'.format(alias)))
                else:
                    newconf.append(conf_elem)
            elif isinstance(conf_elem, Iterable):
                if  '.' not in conf_elem[2]:
                    newconf.append((conf_elem[0], conf_elem[1], '{}.{}'.format(alias,conf_elem[2])))
                elif '_t.' in conf_elem[2]:
                    newconf.append((conf_elem[0], conf_elem[1], conf_elem[2].replace('_t.', '{}.'.format(alias))))
                else:
                    newconf.append(conf_elem)
            else:
                raise ValueError('Unknown filter or select type: {}'.format(conf_elem))

        return newconf

# -*- coding: utf8 -*-
import datetime
import logging
from uuid import uuid4
import six
from .base_metadata_db import BaseMetadataDB, MetadataTypeNotSupported, MetadataFieldNotFound, MetadataOperationError
from ..bigquery_mixin import BigQueryMixin, BqJob
import re


# noinspection SqlNoDataSourceInspection
class BigQueryMetadataDB(BaseMetadataDB, BigQueryMixin):
    STAGING_TABLE_NAME = 'staging'
    STAGING_COMMIT = 'staging'
    METADATA_TABLE_NAME = 'metadata'
    INDEX_TABLE_NAME = 'index'
    STAGING_INDEX_TABLE_NAME = 'staging_index'
    TEMP_TABLE_TTL = 10 * 60

    def __init__(self, connection, version=None, version_ts_lookup=None, delete_temp_on_commit=True, isolated=False):
        self.__version = version
        self.__staging_table = None
        self.__metadata_table = None
        self.__prev_table_info = None
        self.__delete_temp_on_commit = delete_temp_on_commit
        self.__isolated = isolated
        super(BigQueryMetadataDB, self).__init__(connection, version_ts_lookup)

    def __get_staging_table_name(self, version=None):
        version = version or self.__version or 0
        return '%s_%s' % (self.STAGING_TABLE_NAME, version)

    def __get_staging_index_table_name(self):
        version = self.__version or 0
        return '%s_%s' % (self.STAGING_INDEX_TABLE_NAME, version)

    @classmethod
    def _default_table_schema(cls):
        from google.cloud import bigquery

        schema = (
            bigquery.SchemaField('_sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('_commit_sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('_ts', 'TIMESTAMP', 'REQUIRED'),
            bigquery.SchemaField('_hash', 'STRING', 'REQUIRED'),
        )

        return schema

    def _create_table(self):
        schema = self._default_table_schema()

        self.__metadata_table = self._create_specific_table(self.METADATA_TABLE_NAME, schema)
        self.__staging_table = self._create_specific_table(self.__get_staging_table_name(), self.__metadata_table.schema)

    def __get_staging_table(self):
        self.__staging_table = self._get_specific_table(self.__get_staging_table_name())
        return self.__staging_table

    def __using_staging_table(self):
        if self.__staging_table is None:
            self.__get_staging_table()

    def __get_metadata_table(self):
        self.__metadata_table = self._get_specific_table(self.METADATA_TABLE_NAME)
        return self.__metadata_table

    def __using_metadata_table(self):
        if self.__metadata_table is None:
            self.__get_metadata_table()

    @classmethod
    def __value_to_sql_type(cls, column_value):
        if isinstance(column_value, six.string_types):
            return 'STRING'

        if isinstance(column_value, six.integer_types):
            return 'INTEGER'

        if isinstance(column_value, float):
            return 'FLOAT'

        raise MetadataTypeNotSupported('UNKNOWN TYPE %s' % type(column_value))

    def _patch_table_with_new_schema(self, table, schema):
        bq_client = self._connection

        table.schema = schema
        bq_client.update_table(table, ['schema'])

    @classmethod
    def __validate_new_columns(cls, table, new_columns):
        schema = table.schema[:]
        existing_fields = {field.name: field for field in schema}
        actual_new_columns = []
        for new_column in new_columns:
            if new_column.name in existing_fields:
                existing_field = existing_fields[new_column.name]
                if new_column.field_type.lower() != existing_field.field_type.lower():
                    raise MetadataOperationError('field %s changed type from %s to %s' % (
                        new_column.name, new_column.field_type, existing_field.field_type))

                continue

            actual_new_columns.append(new_column)

        return actual_new_columns

    def __add_columns(self, table, new_columns, refresh_table_method):
        from google.api_core.exceptions import PreconditionFailed

        logging.info('add columns %s', new_columns)

        if len(new_columns) == 0:
            return

        retry = 3

        while retry > 0:
            actual_new_columns = self.__validate_new_columns(table, new_columns)

            if len(actual_new_columns) == 0:
                return

            schema = table.schema[:]
            actual_new_columns = sorted(actual_new_columns, key=lambda field: field.name)
            schema.extend(actual_new_columns)
            try:
                self._patch_table_with_new_schema(table, schema)
                break
            except PreconditionFailed:
                logging.info('table %s precondition failed, retrying', self.__staging_table.table_id)
                table = refresh_table_method()
                retry -= 1
                continue

    def __columns_from_data_object(self, data_object):
        from google.cloud import bigquery

        columns = []
        for column_name, column_value in data_object.items():
            column_name = self.common_name_to_bq_field_name(column_name)
            columns.append(bigquery.SchemaField(column_name, self.__value_to_sql_type(column_value)))

        return columns

    def _add_missing_columns(self, data_object):
        self.__using_staging_table()

        columns = self.__columns_from_data_object(data_object)
        self.__add_columns(self.__staging_table, columns, self.__get_staging_table)

    @classmethod
    def _fields_for_select(cls, fields):
        return ','.join(['`%s`' % field for field in fields])

    @classmethod
    def _schema_fields(cls, schema):
        return [field.name for field in schema]

    def _merge_rows(self, src_table, schema=None):
        from google.api_core.exceptions import BadRequest

        self.__using_staging_table()
        self.__using_metadata_table()

        built_in_fields = set(self._schema_fields(self._default_table_schema()))

        fields_new = set(self._schema_fields(schema or src_table.schema))
        staging_fields = set(self._schema_fields(self.__staging_table.schema)) - built_in_fields
        metadata_fields = set(self._schema_fields(self.__metadata_table.schema)) - built_in_fields

        only_in_staging_fields = staging_fields - fields_new
        only_in_metadata_fields = metadata_fields - only_in_staging_fields - fields_new

        all_meta_fields = []
        all_meta_fields.extend(fields_new)
        all_meta_fields.extend(staging_fields)
        all_meta_fields.extend(metadata_fields)

        all_meta_fields = sorted(set(all_meta_fields))

        select_fields = []
        for field in all_meta_fields:
            select_field = 'TO_JSON_STRING(`{field}`)'.format(field=field)
            select_fields.append(select_field)

        hash_select = 'TO_HEX(SHA1(CONCAT({fields}))) as _hash'.format(fields=','.join(select_fields))

        with self._connection.get_cursor() as bq_dataset:
            src_query = """
                #standardSQL
                #_merge_rows
                SELECT *, {hash_select}, CURRENT_TIMESTAMP() as _ts, 'staging' as _commit_sha
                FROM (
                    SELECT *  
                    FROM `{dataset_name}.{src_table}`
                """

            if len(only_in_staging_fields) > 0:
                src_query += """
                    LEFT JOIN (
                        SELECT `_sha`, {only_in_staging_fields}
                        FROM `{dataset_name}.{metadata_staging_index_table_name}`
                    )
                    USING (_sha)
                """

            if len(only_in_metadata_fields) > 0:
                src_query += """
                    LEFT JOIN (
                        SELECT `_sha`, {only_in_metadata_fields}
                        FROM `{dataset_name}.{metadata_table_name}`
                    )
                    USING (_sha)                    
                """

            src_query += ')'

            src_query = src_query.format(
                hash_select=hash_select,
                dataset_name=bq_dataset.dataset_id,
                src_table_columns=self._fields_for_select(fields_new),
                only_in_staging_fields=self._fields_for_select(only_in_staging_fields),
                only_in_metadata_fields=self._fields_for_select(only_in_metadata_fields),
                src_table=src_table.table_id,
                **self.__get_table_names()
            )

            new_staging_fields = fields_new - staging_fields - built_in_fields
            new_staging_fields = list(self._get_fields_schema(new_staging_fields, src_table))
            self.__add_columns(self.__staging_table, new_staging_fields, self.__get_staging_table)

            job = self._async_copy_table_data(src_query, (), self._get_table_ref(self.__get_staging_table_name()))

            try:
                BqJob(job).wait()
            except BadRequest as ex:
                logging.info(str(ex))
                message = ex.errors[0]['message'] if len(ex.errors) > 0 else 'Unknown error'
                raise MetadataOperationError(message)

    @classmethod
    def _delete_temp_table(cls, project, table_ref):
        from controllers.legit import BigQueryConnection
        from google.cloud import bigquery

        bq_client = bigquery.Client(project=project)

        BigQueryConnection.delete_table_using_connection(bq_client, table_ref)

    def _get_temp_table(self, prefix):
        prefix = 'tmp_' + prefix
        from deferred import do_defer

        temp_table_ref = self._get_table_ref(uuid4().hex, prefix=prefix)

        do_defer(
            self._delete_temp_table, temp_table_ref.project, temp_table_ref,
            _countdown=self.TEMP_TABLE_TTL, _tag=temp_table_ref.project)

        return temp_table_ref

    def add_data_using_url(self, metadata_url, dry_mode=False):
        temp_table_ref = self._get_temp_table(prefix='add_data')

        job = self._async_load_job(metadata_url, table_ref=temp_table_ref)

        result = BqJob(job).wait()

        logging.info('result %s', result)

        if not dry_mode:
            bq_client = self._connection
            dest_table = bq_client.get_table(result.destination)
            self._merge_rows(dest_table)

    def _add_data(self, flatten_data_list):
        rows = []

        now = datetime.datetime.utcnow()

        for flatten_data_list in flatten_data_list:
            row = []
            for field in self.__staging_table.schema:
                common_field_name = self.bq_field_name_to_common_name(field.name)
                if common_field_name == '_ts':
                    row.append(now)
                else:
                    row.append(flatten_data_list.get(common_field_name))

            rows.append(row)

        bq_client = self._connection
        bq_client.create_rows(self.__staging_table, rows)

    def __truncate_staging(self):
        import google.cloud.exceptions

        if not self.__delete_temp_on_commit:
            logging.debug('meta: delete_temp_on_commit')
            return

        logging.info('truncate metadata staging')
        bq_client = self._connection
        # noinspection PyUnresolvedReferences
        try:
            bq_client.delete_table(self._get_table_ref(self.__get_staging_table_name()))
        except google.cloud.exceptions.NotFound:
            logging.info('table %s not found', self.__get_staging_table_name())
            pass

    def end_commit(self):
        logging.debug('bq end commit meta')

        if not self.__isolated:
            self.__truncate_staging()

    def begin_commit(self, commit_sha, tree_id, ts):
        logging.debug('bq begin commit meta %s %s (%s, %s)', commit_sha, tree_id, self.__isolated, self.__version)

        from google.cloud import bigquery

        self.__using_staging_table()
        self.__using_metadata_table()

        if self.__staging_table.schema != self.__metadata_table.schema:
            self.__add_columns(self.__metadata_table, self.__staging_table.schema, self.__get_metadata_table)

        with self._connection.get_cursor() as bq_dataset:
            if not self.__isolated:
                # create the table for the next staging
                self._create_specific_table(self.__get_staging_table_name(version=self.__version + 1), self.__staging_table.schema)

            src_query = """
                #standardSQL
                #begin_commit
                SELECT @commit_sha as _commit_sha, @ts as _ts, TableA.*
                # Find the latest metadata given in the staging meta
                FROM (
                  SELECT * EXCEPT(row_number)
                  FROM (
                    # Find the latest metadata given in the staging meta
                    SELECT * EXCEPT(_commit_sha, _ts) , ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                    FROM {dataset_name}.{metadata_staging_index_table_name}
                  )
                  WHERE row_number = 1
                ) TableA
                LEFT OUTER JOIN (
                  SELECT * EXCEPT(row_number)
                  FROM (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                    FROM {dataset_name}.{metadata_table_name}
                  )
                  WHERE row_number = 1
                ) TableB
                USING (_sha, _hash)
                WHERE TableB._sha IS NULL OR TableB._hash IS NULL
            """.format(
                dataset_name=bq_dataset.dataset_id,
                **self.__get_table_names())

            src_query_parameters = (
                bigquery.ScalarQueryParameter('commit_sha', 'STRING', commit_sha),
                bigquery.ScalarQueryParameter('ts', 'TIMESTAMP', ts),
            )

            metadata_table = self._get_table_ref(self.METADATA_TABLE_NAME)
            job = self._async_copy_table_data(src_query, src_query_parameters, metadata_table)

            return BqJob(job)

    def _query_head_data(self, sha_list):
        from google.cloud import bigquery
        from google.cloud.bigquery import QueryJobConfig

        bq_client = self._connection

        metadata_fields, staging_metadata_fields = self.__get_metadata_fields_for_union()

        with bq_client.get_cursor() as bq_dataset:
            query = """
            #standardSQL
            #_query_head_data
            SELECT * EXCEPT(_max_sha, _max_ts, _ts)
            FROM (
              SELECT {staging_metadata_fields}
              FROM `{dataset_name}.{metadata_staging_index_table_name}`
              WHERE _sha IN UNNEST(@sha_list)
              UNION ALL
              SELECT {metadata_fields}
              FROM `{dataset_name}.{metadata_table_name}`
              WHERE _sha IN UNNEST(@sha_list)) AS metadata_staging_combine
              INNER JOIN (
                  SELECT  _sha AS _max_sha, MAX(_ts) AS _max_ts
                  FROM `{dataset_name}.{metadata_staging_index_table_name}`
                  WHERE _sha IN UNNEST(@sha_list)
                  GROUP BY _sha
                  UNION ALL
                  SELECT  _sha AS _max_sha, MAX(_ts) AS _max_ts
                  FROM `{dataset_name}.{metadata_table_name}`
                  WHERE _sha IN UNNEST(@sha_list)
                  GROUP BY _sha
              ) _max_metadata
              ON metadata_staging_combine._sha = _max_sha
              WHERE metadata_staging_combine._ts = _max_ts;
            """.format(
                dataset_name=bq_dataset.dataset_id,
                staging_metadata_fields=staging_metadata_fields,
                metadata_fields=metadata_fields,
                **self.__get_table_names())

            query_parameters = (
                bigquery.ArrayQueryParameter('sha_list', 'STRING', sha_list),
            )

            job_config = QueryJobConfig()
            job_config.query_parameters = query_parameters

            items_iter, _ = self._query_sync(query, job_config, process_row=self.build_dict)

            return items_iter

    @classmethod
    def __table_fields(cls, table_ref):
        for field in table_ref:
            yield field.name

    @classmethod
    def __union_fields(cls, fields_a, fields_b):
        def field_value(field_name, missing_fields=None):
            if field_name in (missing_fields or []):
                return 'NULL as `%s`' % field_name

            return '`%s`' % field_name

        new_fields = list(set(fields_a) - set(fields_b))

        fields_a_select = ','.join([field_value(field) for field in fields_a])
        fields_b_select = ','.join([field_value(field, new_fields) for field in fields_a])

        return fields_b_select, fields_a_select

    def __get_metadata_fields_for_union(self, except_fields=None):
        self.__using_staging_table()
        self.__using_metadata_table()

        staging_metadata_fields = set(list(self.__table_fields(self.__staging_table.schema))) - set(except_fields or [])
        metadata_fields = set(list(self.__table_fields(self.__metadata_table.schema))) - set(except_fields or [])

        return self.__union_fields(staging_metadata_fields, metadata_fields)

    def _query(self, sql_vars, select_fields, where, result_url=None):
        import google.cloud.exceptions
        from google.cloud import bigquery
        from google.cloud.bigquery import QueryJobConfig

        bq_client = self._connection
        sql_vars['random_function'] = '_phr'

        user_limit = sql_vars.get('limit')
        user_limit = 'LIMIT %s' % user_limit if user_limit is not None else ''

        system_limit = '' if user_limit else 'LIMIT 1000' if result_url is None else ''

        offset = sql_vars.get('offset')
        offset = 'OFFSET %s' % offset if offset is not None else ''

        if sql_vars.get('split_field') is None:
            query_phase = """
                    CASE
                      WHEN _phr >= $sample_percentile + $phase_train_start * $sample AND _phr < $sample_percentile + $phase_train_end * $sample THEN 'train'
                      WHEN _phr >= $sample_percentile + $phase_test_start * $sample AND _phr < $sample_percentile + $phase_test_end * $sample THEN 'test'
                      WHEN _phr >= $sample_percentile + $phase_validation_start * $sample AND _phr < $sample_percentile + $phase_validation_end * $sample THEN 'validation'
                      ELSE NULL
                    END as _phase            
            """
        else:
            query_phase = '%s as _phase' % sql_vars.get('split_field')

        def query_size_staging_without_where():
            return """
                #standardSQL
                #query_size_staging_without_where
                SELECT SUM(_size) AS `size`, COUNT(_size) AS `count`
                FROM (
                    SELECT *
                    FROM (
                        SELECT size as _size, name as _sha, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number                                  
                        FROM {dataset_name}.{index_staging_index_table_name}
                    )
                    WHERE row_number = 1
                    {user_limit}
                )
             """

        def query_size_without_staging_without_where():
            return """
                #standardSQL
                #query_size_without_staging_without_where
                SELECT SUM(_size) AS `size`, COUNT(_size) AS `count`
                FROM (
                    SELECT *
                    FROM (
                        SELECT size as _size, name as _sha, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number                                  
                        FROM {dataset_name}.{index_table_name}
                        WHERE ts <= @version_ts
                    )
                    WHERE row_number = 1
                    {user_limit}
                )
             """

        def query_size_staging():
            if where is None:
                return query_size_staging_without_where()

            metadata_fields, staging_metadata_fields = self.__get_metadata_fields_for_union({'_hash', 'url'})

            return """
                #standardSQL
                #query_size_staging
                SELECT SUM(_size) as `size`, COUNT(_size) as `count`
                FROM (
                    SELECT  _sha, _size
                    FROM ( # Bring all the items from staging index 
                      SELECT *
                      FROM (
                        SELECT name as _sha, _size 
                        FROM (
                          SELECT name, size as _size, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number
                          FROM {dataset_name}.{index_staging_index_table_name}
                         )
                        WHERE row_number = 1
                      ) staging_index
                      LEFT JOIN (
                        SELECT _sha
                        FROM (
                          SELECT _sha, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                          FROM {dataset_name}.{metadata_staging_index_table_name}
                        )
                        WHERE row_number = 1
                      ) staging_meta
                      USING(_sha) # _sha is actual a name here
                    ) AS staging_items
                    LEFT JOIN (
                      # join this with latest (_ts) metadata
                      SELECT * EXCEPT(_commit_sha, row_number)
                      FROM (
                        SELECT *, ((FARM_FINGERPRINT({phase_seed}) + POW(2, 63)) / POW(2, 64)) as _phr
                          FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                            FROM  (
                              SELECT {staging_metadata_fields}
                              FROM {dataset_name}.{metadata_staging_index_table_name}
                              UNION ALL
                              SELECT {metadata_fields}
                              FROM {dataset_name}.{metadata_table_name}
                            )
                          )
                          WHERE row_number = 1
                      )
                    ) AS meta
                    USING(_sha)
                    WHERE({where})
                    {user_limit}                    
                )
             """.replace('{staging_metadata_fields}', staging_metadata_fields).replace('{metadata_fields}', metadata_fields)

        def query_staging():
            metadata_fields, staging_metadata_fields = self.__get_metadata_fields_for_union({'_hash', 'url'})

            return """
                #standardSQL
                # query_staging
                SELECT * EXCEPT(_ts, _phr), {query_phase}
                FROM (
                    SELECT  *
                    FROM ( # Bring all the items from staging index 
                      SELECT *
                      FROM (
                        SELECT name as _sha, _size 
                        FROM (
                          SELECT name, size as _size, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number
                          FROM {dataset_name}.{index_staging_index_table_name}
                         )
                        WHERE row_number = 1
                      ) staging_index
                      LEFT JOIN (
                        SELECT _sha
                        FROM (
                          SELECT _sha, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                          FROM {dataset_name}.{metadata_staging_index_table_name}
                        )
                        WHERE row_number = 1
                      ) staging_meta
                      USING(_sha) # _sha is actual a name here
                    ) AS staging_items
                    LEFT JOIN (
                      # join this with latest (_ts) metadata
                      SELECT * EXCEPT(_commit_sha, row_number)
                      FROM (
                        SELECT *
                          FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                            FROM  (
                              SELECT {staging_metadata_fields}
                              FROM {dataset_name}.{metadata_staging_index_table_name}
                              UNION ALL
                              SELECT {metadata_fields}
                              FROM {dataset_name}.{metadata_table_name}
                            )
                          )
                          WHERE row_number = 1
                      )
                      RIGHT JOIN (
                        # This join will give us the latest URL (_url) and hash (_hash) of the data (by name)
                        SELECT ((FARM_FINGERPRINT({phase_seed}) + POW(2, 63)) / POW(2, 64)) as _phr, *
                        FROM (
                          SELECT name as _sha, sha as _hash, _url
                          FROM ( # This will remove any duplicates we might have
                            SELECT * EXCEPT(row_number)
                            FROM (
                              SELECT *, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number
                              FROM (
                                SELECT name, ts, url as _url, sha
                                FROM {dataset_name}.{index_staging_index_table_name}
                                UNION ALL
                                SELECT name, ts, url as _url, sha
                                FROM {dataset_name}.{index_table_name}
                                UNION ALL
                                SELECT _sha as name, NULL as ts, NULL as  _url, NULL as sha
                                FROM {dataset_name}.{metadata_staging_index_table_name}            
                              )
                            )
                            WHERE row_number = 1                                                        
                          )
                        )
                      ) index_with_hash
                      USING(_sha)
                    ) AS meta
                    USING(_sha)
                )
                WHERE({where})
                ORDER BY _ts DESC, _sha
                {user_limit_or_system_limit}
                {offset}
             """.replace('{staging_metadata_fields}', staging_metadata_fields).replace('{metadata_fields}', metadata_fields)

        def query_size_without_staging():
            if where is None:
                return query_size_without_staging_without_where()

            return """
                #standardSQL
                #query_size_without_staging
                SELECT SUM(_size) AS `size`, COUNT(_size) AS `count`
                FROM (
                    SELECT *
                    FROM (
                        SELECT *, {query_phase}
                        FROM (
                            SELECT *, ((FARM_FINGERPRINT({phase_seed}) + POW(2, 63)) / POW(2, 64)) as _phr                    
                            FROM (
                                SELECT *, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                                FROM (
                                  SELECT * EXCEPT(row_number, _hash)
                                  FROM (
                                      SELECT *, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) as row_number
                                      FROM {dataset_name}.{metadata_table_name}
                                      WHERE _ts <= @version_ts
                                    )
                                    WHERE row_number = 1
                                )
                                RIGHT JOIN (
                                    SELECT * EXCEPT(row_number)
                                    FROM (
                                        SELECT size as _size, name as _sha, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number                                  
                                        FROM {dataset_name}.{index_table_name}
                                        WHERE ts <= @version_ts
                                    )
                                    WHERE row_number = 1
                                )
                                USING(_sha)
                            )
                        )
                    )
                    WHERE row_number = 1 AND ({where})
                    {user_limit}
                )
             """

        def query_all_meta_data_without_staging():
            return """
                #standardSQL
                #query_all_meta_data_without_staging
                SELECT * EXCEPT(_ts, _phr, _commit_sha, commit_sha), commit_sha AS _commit_sha
                FROM (
                    SELECT {query_phase}, *                    
                    FROM (
                        SELECT *, ((FARM_FINGERPRINT({phase_seed}) + POW(2, 63)) / POW(2, 64)) as _phr
                        FROM (
                            # This join will give us the latest URL (url) and hash (_hash) of the data (by name)
                            # This will remove any duplicates we might have
                            SELECT * EXCEPT(row_number)
                            FROM (
                                SELECT size as _size, commit_sha, name as _sha, sha as _hash, url as _url, 
                                       ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number                                  
                                FROM {dataset_name}.{index_table_name}
                                WHERE ts <= @version_ts
                            )
                            WHERE row_number = 1
                        )
                        LEFT JOIN (
                          SELECT * EXCEPT(row_number, _hash)
                          FROM (
                            SELECT *, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) as row_number
                            FROM {dataset_name}.{metadata_table_name}
                            WHERE _ts <= @version_ts
                          )
                          WHERE row_number = 1                        
                        )
                        USING(_sha)                        
                    )
                    WHERE _phr is not NULL
                )
                WHERE ({where})
                {user_limit_or_system_limit}
                {offset}
             """

        def get_phase_seed():
            fields = []
            for key in [group_key, datapoint_key]:
                if not key:
                    continue

                fields.append('CAST(`{group}` AS STRING)'.format(group=key))

            if not fields:
                fields.append('`_sha`')

            fields.append('"$seed"')

            return "CONCAT({fields})".format(fields=','.join(fields))

        def append_ver_if_needed(name, var_type, src_query_parameters):
            if '@' + name in query_sql:
                version_ts = sql_vars[name]
                src_query_parameters.append(bigquery.ScalarQueryParameter(name, var_type, version_ts))

            return src_query_parameters

        def handle_bad_query_request(bad_request):
            field = self._field_not_found(bad_request.message)

            if field is not None:
                raise MetadataFieldNotFound(field)

        def format_query(query):
            return query.format(
                dataset_name=bq_dataset.dataset_id,
                phase_seed=phase_seed,
                where=where or 'True',
                select=','.join(select_fields),
                user_limit_or_system_limit=user_limit or system_limit,
                system_limit=system_limit,
                user_limit=user_limit,
                offset=offset,
                query_phase=query_phase,
                **self.__get_table_names())

        def return_iter(query_query_job):
            data_iter, _ = self._query_sync_by_job(query_query_job, process_row=self.build_dict)

            return data_iter

        def get_size_result_job(job_config):
            def process_size_result(results):
                for result in results:
                    return result['size'], result['count']

            return BqJob(
                self._query_async(size_query, job_config), process_size_result)

        def create_job_config(current_result_url=None):
            src_query_parameters = append_ver_if_needed('version_ts', 'TIMESTAMP', [])

            job_config = QueryJobConfig()
            job_config.query_parameters = src_query_parameters
            job_config.use_query_cache = True

            if current_result_url is not None:
                job_config.allow_large_results = True
                job_config.destination = self._get_temp_table(prefix='query_data')

            return job_config

        with bq_client.get_cursor() as bq_dataset:
            version_var = sql_vars.get('version')

            group_key = sql_vars.get('group')
            datapoint_key = sql_vars.get('datapoint')

            phase_seed = get_phase_seed()

            if version_var is not None and version_var.lower() == 'staging':
                query_sql, size_query = query_staging(), query_size_staging()
            else:
                query_sql, size_query = query_all_meta_data_without_staging(), query_size_without_staging()

            query_sql = self.fill_in_vars(format_query(query_sql), sql_vars)
            size_query = self.fill_in_vars(format_query(size_query), sql_vars)

            def do_query():
                query_job_config = create_job_config(result_url)
                full_result_query_job = self._query_async(query_sql, query_job_config)

                query_job = get_size_result_job(job_config=create_job_config())

                if result_url is None:
                    total_size, total_count = query_job.wait()

                    return return_iter(full_result_query_job), total_count, total_size

                full_result_query_job.result()

                extract_job = self._extract_table(query_job_config.destination, result_url)

                BqJob(extract_job).wait()
                total_size, total_count = query_job.wait()

                return None, total_count, total_size

            # noinspection PyUnresolvedReferences
            try:
                return do_query()
            except google.cloud.exceptions.BadRequest as ex:
                handle_bad_query_request(ex)
                logging.exception('bad query')
                raise MetadataOperationError()

    @classmethod
    def _field_not_found(cls, message):
        field_not_found_re = r'Unrecognized name:\ (?P<field>.*) at \[\d+:\d+\]'

        m = re.match(field_not_found_re, message)

        return None if m is None else m.group("field")

    def get_all_data(self, sha):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        pass

    def delete_all(self):
        metadata_table = self._get_table_name(self._connection.table_prefix, self.METADATA_TABLE_NAME)
        staging_metadata_table_prefix = self._get_table_name(self._connection.table_prefix, self.STAGING_TABLE_NAME)
        self._connection.delete_tables([metadata_table, staging_metadata_table_prefix])

    def get_commit_statistics(self, commit_sha, most_frequent_values_limit=100):
        from google.cloud.bigquery import QueryJobConfig
        import google.cloud.exceptions

        def get_metadata_fields():
            metadata_table_ref = self._get_table_ref(self.METADATA_TABLE_NAME)
            # noinspection PyUnresolvedReferences
            try:
                metadata_table = bq_client.get_table(metadata_table_ref)
            except google.cloud.exceptions.NotFound:
                logging.info('table %s not found', self.METADATA_TABLE_NAME)
                return None

            default_schema = self._default_table_schema()
            return [field.name for field in metadata_table.schema if field not in default_schema]

        def query_top_values(current_metadata_field):
            query = """
                #standardSQL
                #query_top_values
                SELECT `{field}`, COUNT(*) as frequency
                FROM (
                  SELECT {field}, ROW_NUMBER() OVER (PARTITION by _sha ORDER BY _ts DESC) row_number
                  FROM `{dataset_name}.{metadata_table_name}`
                  WHERE  _ts <= (
                    SELECT MAX(_ts)
                    FROM `{dataset_name}.{metadata_table_name}`
                    WHERE `_commit_sha` = '{commit_sha}')
                )
                WHERE row_number = 1
                GROUP BY `{field}`
                ORDER BY frequency DESC
                LIMIT {limit}
            """.format(
                dataset_name=bq_dataset.dataset_id,
                field=current_metadata_field,
                commit_sha=commit_sha,
                limit=most_frequent_values_limit,
                **self.__get_table_names())
            return self._query_async(query, QueryJobConfig())

        bq_client = self._connection
        with bq_client.get_cursor() as bq_dataset:
            metadata_fields = get_metadata_fields()

            if metadata_fields is None:
                return {}

            query_jobs = {field: query_top_values(field) for field in metadata_fields}

            metadata_statistics = {}
            for metadata_field, query_job in query_jobs.items():
                top_values = [tuple(row) for row in query_job.result()]
                metadata_statistics[metadata_field] = top_values

        return metadata_statistics

    def __get_table_names(self):
        bq_client = self._connection

        metadata_table_name = self._get_table_name(bq_client.table_prefix, self.METADATA_TABLE_NAME)
        metadata_staging_index_table_name = self._get_table_name(bq_client.table_prefix, self.__get_staging_table_name())
        index_staging_index_table_name = self._get_table_name(bq_client.table_prefix, self.__get_staging_index_table_name())
        index_table_name = self._get_table_name(bq_client.table_prefix, self.INDEX_TABLE_NAME)

        return {
            'metadata_table_name': metadata_table_name,
            'metadata_staging_index_table_name': metadata_staging_index_table_name,
            'index_staging_index_table_name': index_staging_index_table_name,
            'index_table_name': index_table_name,
        }

    def rpc_total_count_items(self):
        bq_client = self._connection

        with bq_client.get_cursor() as bq_dataset:
            query = """
                #standardSQL
                #rpc_total_count_items
                SELECT *
                FROM (
                    SELECT 'item' as _id, COUNT(DISTINCT name) as total_data_points
                    FROM (
                      SELECT DISTINCT name FROM `{dataset_name}.{index_table_name}` 
                      UNION ALL
                      SELECT DISTINCT name FROM `{dataset_name}.{index_staging_index_table_name}`
                    )
                )
                LEFT JOIN (
                  SELECT 'item' as _id, COUNT(DISTINCT name) as version_total_data_points
                  FROM `{dataset_name}.{index_staging_index_table_name}`                
                )
                USING (_id)
                LEFT JOIN (
                    SELECT 'item' as _id, COUNT(DISTINCT _sha) as total_meta_data
                    FROM (
                      SELECT DISTINCT _sha FROM `{dataset_name}.{metadata_table_name}`
                      UNION ALL
                      SELECT DISTINCT _sha FROM `{dataset_name}.{metadata_staging_index_table_name}`
                    )                
                )
                USING (_id)
                LEFT JOIN (
                  SELECT 'item' as _id, COUNT(DISTINCT _sha) as version_total_meta_data
                  FROM `{dataset_name}.{metadata_staging_index_table_name}`                
                )
                USING (_id)                                               
                """.format(dataset_name=bq_dataset.dataset_id, **self.__get_table_names())

            return self._return_async_dict(
                query,
                'total_data_points', 'version_total_data_points',
                'total_meta_data', 'version_total_meta_data')

    def rpc_get_commit_id(self):
        bq_client = self._connection

        with bq_client.get_cursor() as bq_dataset:
            src_query = """ 
                #standardSQL
                #rpc_get_commit_id
                SELECT *
                FROM (
                    SELECT 'item' as _id, TO_HEX(SHA1(STRING_AGG(_hash ORDER BY _sha))) AS meta_sha
                    FROM (
                        SELECT * EXCEPT(row_number)
                        FROM (
                            SELECT _hash, _sha, ROW_NUMBER() OVER (PARTITION BY _sha ORDER BY _ts DESC) row_number
                            FROM (
                              SELECT _hash, _ts, _sha FROM `{dataset_name}.{metadata_staging_index_table_name}`
                              UNION ALL
                              SELECT _hash, _ts, _sha FROM `{dataset_name}.{metadata_table_name}`
                          )
                        )
                        WHERE row_number=1
                    )
                )
                LEFT JOIN ( 
                    SELECT 'item' as _id, TO_HEX(SHA1(STRING_AGG(sha ORDER BY name))) AS index_sha
                    FROM (
                      SELECT * EXCEPT(row_number)
                      FROM (
                        SELECT sha, name, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number
                        FROM (
                          SELECT sha, ts, name FROM `{dataset_name}.{index_staging_index_table_name}`
                          UNION ALL
                          SELECT sha, ts, name FROM `{dataset_name}.{index_table_name}`
                        )
                      )
                      WHERE row_number=1
                    )       
                )
                USING (_id)
              """.format(dataset_name=bq_dataset.dataset_id, **self.__get_table_names())

        return self._return_async_dict(src_query, 'index_sha', 'meta_sha')

    def delete_version(self, version_id):
        from google.cloud import bigquery

        query_parameters = (
            bigquery.ScalarQueryParameter('version_id', 'STRING', version_id),
        )

        metadata_table_ref = self._get_table_ref(self.METADATA_TABLE_NAME)

        with self._connection.get_cursor() as bq_dataset:
            query = '''
                #standardSQL
                #delete_version
                SELECT * 
                FROM `{dataset_name}.{metadata_table_name}`
                WHERE `_commit_sha` <> @version_id 
            '''.format(
                dataset_name=bq_dataset.dataset_id,
                metadata_table_name=metadata_table_ref.table_id,
            )

            return self.override_table(query, query_parameters, metadata_table_ref)

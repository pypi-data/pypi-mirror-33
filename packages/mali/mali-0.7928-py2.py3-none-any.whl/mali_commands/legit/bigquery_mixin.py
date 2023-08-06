# -*- coding: utf8 -*-
import logging
import os
from uuid import uuid4

from .job import Job
from .connection_mixin import ConnectionMixin


class BqJob(Job):
    def __init__(self, job, result_callback=None):
        self.__job = job
        self.__result_callback = result_callback

    def wait(self):
        result = self.__job.result()

        logging.info('bq job result %s', result)

        return self.__result_callback(result) if self.__result_callback else result


class BigQueryMixin(ConnectionMixin):
    @classmethod
    def __return_results_from_iter(cls, results_iter, process_row, schema):
        for result in results_iter:
            if process_row is not None:
                yield process_row(result, schema)
                continue

            yield result

    def _query_async(self, query, job_config=None):
        from google.cloud.bigquery import QueryJobConfig

        job_config = job_config or QueryJobConfig()
        debug_params = [param.to_api_repr() for param in job_config.query_parameters]
        logging.info('query async: %s, params: %s, legacy_sql: %s', query, debug_params, job_config.use_legacy_sql)

        if job_config.use_query_cache is None:
            job_config.use_query_cache = True

        bq_client = self._connection

        return bq_client.query(query, job_config)

    def _query_sync_by_job(self, query_job, process_row=None):
        results_iter = query_job.result()

        query_results = query_job.query_results()

        # noinspection PyProtectedMember
        logging.debug('query results %s', query_results._properties)

        data_enum = self.__return_results_from_iter(results_iter, process_row, query_results.schema)

        return data_enum, query_results.total_rows

    def _query_sync(self, query, job_config, process_row=None):
        query_job = self._query_async(query, job_config)

        return self._query_sync_by_job(query_job, process_row)

    @classmethod
    def valid_table_name_random_token(cls, size=8):
        from base58 import b58encode

        return b58encode(os.urandom(size))

    @classmethod
    def _get_table_name(cls, prefix, name):
        table_full_name = '{prefix}_{name}'.format(prefix=prefix, name=name)

        return table_full_name

    def _get_table_ref(self, name, prefix=None):
        prefix = prefix or self._connection.table_prefix
        table_full_name = self._get_table_name(prefix, name)

        with self._connection.get_cursor() as bq_dataset:
            return bq_dataset.table(table_full_name)

    def _create_specific_table(self, name, schema):
        logging.info('create_specific_table %s with schema %s', name, schema)

        import google.cloud.exceptions
        from google.cloud.bigquery import Table

        table_ref = self._get_table_ref(name)

        table = Table(table_ref, schema=schema)

        bq_client = self._connection

        try:
            bq_client.create_table(table)
        except google.cloud.exceptions.Conflict:
            table = self._get_specific_table(name)

        return table

    def _get_specific_table(self, name):
        table_ref = self._get_table_ref(name)

        bq_client = self._connection

        return bq_client.get_table(table_ref)

    def _copy_table_data(self, src_query, src_query_params, dest_table_ref, write_disposition=None):
        return self._async_copy_table_data(src_query, src_query_params, dest_table_ref, write_disposition).result()

    def _async_copy_table_data(self, src_query, src_query_params, dest_table_ref, write_disposition=None):
        from google.cloud.bigquery.job import WriteDisposition
        from google.cloud.bigquery import QueryJobConfig

        write_disposition = write_disposition or WriteDisposition.WRITE_APPEND

        logging.info(
            'copy_table_data to %s filter query: %s params: %s (%s)',
            dest_table_ref.table_id if dest_table_ref else '(random table)', src_query, src_query_params, write_disposition)

        job_config = QueryJobConfig()
        job_config.query_parameters = src_query_params
        job_config.destination = dest_table_ref
        job_config.write_disposition = write_disposition

        return self._query_async(src_query, job_config)

    def _extract_table(self, table_ref, url):
        from google.cloud.bigquery.job import DestinationFormat
        from google.cloud.bigquery import ExtractJobConfig

        logging.info('extract_table %s to %s', table_ref.table_id, url)

        job_config = ExtractJobConfig()
        if url.endswith('.json'):
            job_config.destination_format = DestinationFormat.NEWLINE_DELIMITED_JSON

        bq_client = self._connection

        return bq_client.extract_table(table_ref, url, job_config=job_config)

    def _async_load_job(self, url, schema=None, table_ref=None):
        from google.cloud.bigquery import LoadJobConfig
        from google.cloud.bigquery.job import DestinationFormat

        job_config = LoadJobConfig()
        if url.endswith('.json'):
            job_config.source_format = DestinationFormat.NEWLINE_DELIMITED_JSON

        job_config.autodetect = schema is None
        if schema is not None:
            job_config.schema = schema

        bq_client = self._connection

        dest_table_ref = table_ref or self._get_table_ref(uuid4().hex)

        return bq_client.load_table_from_uri(url, dest_table_ref, job_config=job_config)

    @classmethod
    def bq_field_name_to_common_name(cls, name):
        return '@' + name[1:] if name in ['_commit_sha', '_size', '_sha', '_hash', '_url', '_phase'] else name

    @classmethod
    def common_name_to_bq_field_name(cls, name):
        return '_' + name[1:] if name.startswith('@') else name

    @classmethod
    def build_dict(cls, row, schema):
        return {
            cls.bq_field_name_to_common_name(field.name): val for field, val in zip(schema, row) if val is not None
        }

    def _return_async_dict(self, query, *names):
        def process_result(results):
            for result in results:
                return {name: result[name] for name in names}

        return self._return_async(query, process_result)

    def _return_async(self, query, callback):
        from google.cloud.bigquery import QueryJobConfig

        job_config = QueryJobConfig()

        job = self._query_async(query, job_config)

        return BqJob(job, callback)

    @classmethod
    def _get_fields_schema(cls, new_staging_fields, table):
        for field in table.schema:
            if field.name in new_staging_fields:
                yield field

    def override_table(self, query, query_parameters, dest_table, dry_run=False):
        from google.cloud.bigquery import QueryJobConfig
        from google.cloud.bigquery.job import WriteDisposition

        job_config = QueryJobConfig()
        job_config.query_parameters = query_parameters
        job_config.write_disposition = WriteDisposition.WRITE_TRUNCATE
        job_config.destination = dest_table
        job_config.dry_run = dry_run

        job = self._query_async(query, job_config)

        return BqJob(job)

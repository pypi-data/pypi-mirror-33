# -*- coding: utf8 -*-
import datetime
import logging
from ..bigquery_mixin import BigQueryMixin, BqJob
from .base_db_index import BaseMLIndex


# noinspection SqlNoDataSourceInspection,SqlResolve
class BigQueryMLIndex(BaseMLIndex, BigQueryMixin):
    STAGING_INDEX_TABLE_NAME = 'staging_index'
    INDEX_TABLE_NAME = 'index'

    def __init__(self, connection, version=None, delete_temp_on_commit=True, isolated=False):
        self.__version = version or 0

        super(BigQueryMLIndex, self).__init__(connection)
        self.__delete_temp_on_commit = delete_temp_on_commit
        self.__isolated = isolated

    def __get_index_table_ref(self):
        return self._get_table_ref(self.INDEX_TABLE_NAME)

    def __get_staging_index_table_ref(self, version=None):
        staging_table_name = '%s_%s' % (self.STAGING_INDEX_TABLE_NAME, version or self.__version or 0)
        return self._get_table_ref(staging_table_name)

    @classmethod
    def __table_schema(cls):
        from google.cloud import bigquery

        schema = (
            bigquery.SchemaField('name', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('ctime', 'FLOAT', 'REQUIRED'),
            bigquery.SchemaField('mtime', 'FLOAT', 'REQUIRED'),
            bigquery.SchemaField('mode', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('size', 'INTEGER', 'REQUIRED'),
            bigquery.SchemaField('url', 'STRING'),
            bigquery.SchemaField('commit_sha', 'STRING', 'REQUIRED'),
            bigquery.SchemaField('ts', 'TIMESTAMP', 'REQUIRED'),  # this has to be the last column
        )

        return schema

    def __create_table_by_ref_if_needed(self, table_ref):
        logging.info('create table if needed %s', table_ref.table_id)

        import google.cloud.exceptions
        from google.cloud.bigquery.table import Table

        bq_client = self._connection

        table = Table(table_ref)
        table.schema = self.__table_schema()

        try:
            bq_client.create_table(table)
        except google.cloud.exceptions.Conflict:
            pass

        return table

    def _create_table_if_needed(self):
        self.__create_table_by_ref_if_needed(self.__get_index_table_ref())
        self.__create_table_by_ref_if_needed(self.__get_staging_index_table_ref())

    def set_entries(self, entries, dry_mode=False):
        if not entries:
            return

        now = datetime.datetime.utcnow()

        def decode_row_without_gid_uid(entries):
            for name, sha, ctime, mtime, mode, _, _, size, url in self._decode_entries(entries):
                yield name, sha, ctime, mtime, mode, size, url, 'staging', now

        rows = [row for row in decode_row_without_gid_uid(entries)]

        logging.debug('inserting %s rows into bq', len(rows))

        staging_index_table_ref = self.__get_staging_index_table_ref()

        bq_client = self._connection

        if not dry_mode:
            bq_client.create_rows(staging_index_table_ref, rows, selected_fields=self.__table_schema())

        logging.debug('inserted %s rows into bq', len(rows))

    def __truncate_staging_index(self):
        if not self.__delete_temp_on_commit:
            logging.debug('index: delete_temp_on_commit: False')
            return

        logging.info('truncate index staging')

        staging_table_ref = self.__get_staging_index_table_ref()
        bq_client = self._connection
        bq_client.delete_table(staging_table_ref)

    def __query_into_index_table(self, from_table_ref, to_table_ref, commit_sha, ts, remove_duplicates=True):
        from google.cloud import bigquery

        bq_client = self._connection

        with bq_client.get_cursor() as bq_dataset:
            if remove_duplicates:
                src_query = """
                    #standardSQL
                    #__query_into_index_table
                    SELECT interim_index_table.*, @commit_sha as commit_sha, @ts as ts 
                    FROM (
                        SELECT * EXCEPT(row_number, ts, commit_sha)
                        FROM (
                          SELECT *, ROW_NUMBER() OVER (PARTITION BY name ORDER BY ts DESC) row_number
                          FROM `{dataset_name}.{from_table_ref}`
                        )
                        WHERE row_number = 1
                    ) interim_index_table
                  """.format(
                    dataset_name=bq_dataset.dataset_id,
                    from_table_ref=from_table_ref.table_id,
                )
            else:
                src_query = """
                    #standardSQL
                    #__query_into_index_table
                    SELECT interim_index_table.*, @commit_sha as commit_sha, @ts as ts 
                    FROM `{dataset_name}.{from_table_ref}` interim_index_table
                  """.format(
                    dataset_name=bq_dataset.dataset_id,
                    from_table_ref=from_table_ref.table_id,
                )

            src_query_parameters = (
                bigquery.ScalarQueryParameter('commit_sha', 'STRING', commit_sha),
                bigquery.ScalarQueryParameter('ts', 'TIMESTAMP', ts),
            )

            job = self._async_copy_table_data(
                src_query, src_query_parameters, to_table_ref)

            return BqJob(job)

    def begin_commit(self, commit_sha, tree_id, ts):
        staging_index_table_ref = self.__get_staging_index_table_ref()

        if not self.__isolated:
            self.__create_table_by_ref_if_needed(self.__get_staging_index_table_ref(version=self.__version + 1))

        return self.__query_into_index_table(staging_index_table_ref, self.__get_index_table_ref(), commit_sha, ts)

    def end_commit(self):
        if not self.__isolated:
            self.__truncate_staging_index()

    def delete_all(self):
        index_table = self._get_table_name(self._connection.table_prefix, self.INDEX_TABLE_NAME)
        staging_index_table_prefix = self._get_table_name(self._connection.table_prefix, self.STAGING_INDEX_TABLE_NAME)
        self._connection.delete_tables([index_table, staging_index_table_prefix])

    def _query_changeset(self, new_index_table):
        staging_index_table_ref = self.__get_staging_index_table_ref()
        index_table_ref = self.__get_index_table_ref()

        with self._connection.get_cursor() as bq_dataset:
            query = """
                #standardSQL
                #_query_changeset
                SELECT name, op
                FROM (
                    SELECT TableA.name as name, 'c' as op
                    FROM `{dataset_name}.{new_index_table}` AS TableA
                    LEFT JOIN (
                      SELECT sha, name
                      FROM `{dataset_name}.{staging_index_table}`
                      UNION ALL
                      SELECT sha, name
                      FROM `{dataset_name}.{index_table}`
                    ) AS TableB
                    ON TableA.name = TableB.name 
                    WHERE TableA.sha != TableB.sha
                    UNION ALL
                    SELECT TableA.name as name, 'i' as op
                    FROM `{dataset_name}.{new_index_table}` AS TableA
                    LEFT JOIN (
                      SELECT sha, name
                      FROM `{dataset_name}.{staging_index_table}`
                      UNION ALL
                      SELECT sha, name
                      FROM `{dataset_name}.{index_table}`
                    ) AS TableB
                    ON TableA.name = TableB.name AND TableA.sha = TableB.sha
                    WHERE TableB.sha IS NULL
                    UNION ALL
                    SELECT TableA.name as name, 'd' as op
                    FROM `{dataset_name}.{new_index_table}` AS TableA
                    RIGHT OUTER JOIN (
                      SELECT sha, name
                      FROM `{dataset_name}.{staging_index_table}`
                      UNION ALL
                      SELECT sha, name
                      FROM `{dataset_name}.{index_table}`
                    ) AS TableB
                    ON TableA.name = TableB.name
                    WHERE TableA.name is NULL
                )        
            """.format(
                dataset_name=bq_dataset.dataset_id,
                new_index_table=new_index_table.table_id,
                staging_index_table=staging_index_table_ref.table_id,
                index_table=index_table_ref.table_id,
            )

        return self._query_async(query)

    def _load_table_from_url(self, table_url, table_ref=None):
        job = self._async_load_job(table_url, table_ref=table_ref)

        result = BqJob(job).wait()

        bq_client = self._connection

        return bq_client.get_table(result.destination)

    def add_data_using_url(self, index_url, changeset_result_url):
        data_interim_table = self._load_table_from_url(index_url)

        bq_client = self._connection

        if changeset_result_url is not None:
            query_job = self._query_changeset(data_interim_table)

            BqJob(query_job).wait()

            changeset_table = bq_client.get_table(query_job.destination)

            extract_job = self._extract_table(changeset_table, changeset_result_url)

            BqJob(extract_job).wait()
        else:
            now = datetime.datetime.utcnow()
            staging_index_table_ref = self.__get_staging_index_table_ref()
            self.__query_into_index_table(data_interim_table, staging_index_table_ref, 'staging', now, remove_duplicates=False).wait()

        bq_client.delete_table(data_interim_table)

    def delete_version(self, version_id):
        from google.cloud import bigquery

        query_parameters = (
            bigquery.ScalarQueryParameter('version_id', 'STRING', version_id),
        )

        index_table_ref = self.__get_index_table_ref()
        with self._connection.get_cursor() as bq_dataset:
            query = '''
                #standardSQL
                #delete_version
                SELECT * 
                FROM `{dataset_name}.{index_table_name}`
                WHERE `commit_sha` <> @version_id 
            '''.format(
                dataset_name=bq_dataset.dataset_id,
                index_table_name=index_table_ref.table_id,
            )

            return self.override_table(query, query_parameters, index_table_ref)

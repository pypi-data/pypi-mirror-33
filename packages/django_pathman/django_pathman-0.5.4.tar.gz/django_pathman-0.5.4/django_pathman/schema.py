# coding: utf-8
import logging

from django.db.backends.postgresql.schema import DatabaseSchemaEditor
from django.db import connection

assert isinstance(connection.schema_editor(), DatabaseSchemaEditor), u'Pathman is available for PostgreSQL only'


logger = logging.getLogger('django.db.backends.schema')

DatabaseSchemaEditor.sql_create_range_partitions = "SET TIME ZONE '%s'; " \
                                                   "SELECT create_range_partitions('%s', '%s', %s, %s, %s);"
DatabaseSchemaEditor.sql_disable_pathman_for = "SELECT drop_range_partition(partition, false) FROM " \
                                               "pathman_partition_list WHERE parent = '%s'::regclass;" \
                                               "SELECT disable_pathman_for('%s');"

DatabaseSchemaEditor.alter_child_index = "SELECT alter_child_index(replace('%(table)s', '\"', ''));"


def _data_exists(self, model):
    return model.objects.exists()


def _disable_partitions(self, model):
    sql_disable_pathman_for = self.sql_disable_pathman_for
    return sql_disable_pathman_for % {
        "table": model._meta.db_table,
    }


def range_partitions(self, model, old_partition_rule, new_partition_rule):
    from django.conf import settings
    execute_sql = None
    old_column, old_begin, old_interval = old_partition_rule
    new_column, new_begin, new_interval = new_partition_rule
    if not old_column and new_column:
        data_exists = self._data_exists(model)
        count = 'NULL' if data_exists else 1
        execute_sql = self.sql_create_range_partitions % (settings.TIME_ZONE, model._meta.db_table, new_column, new_begin, new_interval, count)
    elif not new_column and old_column:
        execute_sql = self.sql_disable_pathman_for % (model._meta.db_table, model._meta.db_table)
    elif not old_column and old_column != new_column:
        assert u'Change partition rule column is not allowed'
    else:
        raise RuntimeError(u'Unreachable statement')
    assert execute_sql, u'execute_sql is None'
    logger.debug(u'Partition sql: %s' % execute_sql)
    print execute_sql
    self.execute(execute_sql)


def _create_index_sql(self, model, fields, suffix="", sql=None):
    index_sql = self._create_index_sql_orig(model, fields, suffix=suffix, sql=sql)
    alter_child_index_sql = self.alter_child_index % model._meta.db_table
    result_sql = ';'.join([index_sql.rstrip(';'), alter_child_index_sql])
    return result_sql


def sql_create_index(self):
    return self.sql_create_index_orig + '; ' + self.alter_child_index


def sql_create_varchar_index(self):
    return self.sql_create_varchar_index_orig + '; ' + self.alter_child_index


def sql_create_text_index(self):
    return self.sql_create_text_index_orig + '; ' + self.alter_child_index


DatabaseSchemaEditor._data_exists = _data_exists
DatabaseSchemaEditor._disable_partitions = _disable_partitions
DatabaseSchemaEditor.range_partitions = range_partitions
DatabaseSchemaEditor.sql_create_index_orig = DatabaseSchemaEditor.sql_create_index
DatabaseSchemaEditor.sql_create_varchar_index_orig = DatabaseSchemaEditor.sql_create_varchar_index
DatabaseSchemaEditor.sql_create_text_index_orig = DatabaseSchemaEditor.sql_create_text_index
DatabaseSchemaEditor.sql_create_index = property(sql_create_index)
DatabaseSchemaEditor.sql_create_varchar_index = property(sql_create_varchar_index)
DatabaseSchemaEditor.sql_create_text_index = property(sql_create_text_index)
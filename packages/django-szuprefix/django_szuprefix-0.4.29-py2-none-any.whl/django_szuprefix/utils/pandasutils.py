# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, division
import pandas as pd
from .dbutils import db_sqlalchemy_str, get_table_fields, getDB
from pandas.io.sql import pandasSQL_builder
import math


def get_select_sql(sql):
    sql = sql.strip()
    return ' ' in sql.lower() and sql or (u'select * from %s' % sql)


def get_dataframe_from_table(table_name_or_sql, connection="default", coerce_float=True):
    sql = get_select_sql(table_name_or_sql).replace("%", "%%")
    con = connection.startswith("hive://") and connection or db_sqlalchemy_str(connection)
    return pd.read_sql(sql, con, coerce_float=coerce_float)


def write_dataframe_to_table(df, **kwargs):
    kwargs['con'] = db_sqlalchemy_str(kwargs['con'])
    return df.to_sql(**kwargs)


def smart_write_dataframe_to_table(df, **kwargs):
    con = db_sqlalchemy_str(kwargs['con'])


def split_dataframe_into_chunks(df, chunksize=10000):
    for i in range(int(math.ceil(len(df) / chunksize))):
        b = i * chunksize
        e = b + chunksize - 1
        yield df.loc[b:e]


def dtype(dt):
    return dt.startswith('int') and 'int' \
           or dt.startswith('float') and 'float' \
           or dt.startswith('datetime') and 'datetime' \
           or 'string'


def ftype(ft):
    return ft == "string" and "varchar(255)" or ft == "datetime" and "TIMESTAMP" or ft


def format_timestamp(df):
    for c, dt in df.dtypes.iteritems():
        if str(dt).startswith("datetime"):
            df[c] = df[c].apply(lambda x: x.isoformat())
    return df


def clear_dict_nan_value(d):
    for k, v in d.items():
        if pd.isnull(v) or v == 'NaT':
            d[k] = None
    return d


def dataframe_to_table(df, is_preview=False):
    count = len(df)
    if is_preview and count > 20:
        data = df[:10].merge(df[-10:], how='outer')
    else:
        data = df
    data = [clear_dict_nan_value(d) for d in data.to_dict("records")]
    from pandas.io.json.table_schema import build_table_schema
    schema = build_table_schema(df, index=False)
    return dict(data=data, count=count, fields=schema.get('fields'), is_preview=is_preview)


class AutoGrowTable(object):
    def __init__(self, db_name, table_name, primary_key):
        self.db_name = db_name
        self.table_name = table_name
        self.primary_key = primary_key
        self.fields = {}
        self.connection = getDB(self.db_name)
        self.pd_sql = pandasSQL_builder(db_sqlalchemy_str(self.db_name))
        self.detect_fields()

    def detect_fields(self):
        try:
            self.fields = [f.lower() for f in get_table_fields(getDB(self.db_name), self.table_name)]
        except:
            pass

    def get_field_definition(self, fields):
        return ",".join(["%s %s" % (f, ftype(f)) for f in fields])

    def create_table(self, df):
        exists = self.pd_sql.has_table(self.table_name)
        dtypes = dict([(c, dtype(str(dt))) for c, dt in df.dtypes.iteritems()])
        se = self.connection.schema_editor
        new_fields = ["%s %s" % (f, ftype(dt)) for f, dt in dtypes.iteritems() if f not in self.fields]
        # print new_fields
        with self.connection.cursor() as cursor:
            if not exists:
                sql = "create table %s(%s)" % (self.table_name, ",".join(new_fields))
                # print sql
                cursor.execute(sql)
                sql = "alter table %s add primary key(%s)" % (self.table_name, self.primary_key)
                # print sql
                cursor.execute(sql)
                self.detect_fields()
            else:
                if new_fields:
                    cursor.execute("alter table %s add column %s" % (self.table_name, ", add column ".join(new_fields)))

    def run(self, data_frame):
        df = data_frame
        self.create_table(df)
        errors = self.insert(df)
        return errors

    def gen_sql_table(self, df):
        from pandas.io.sql import SQLTable
        self.table = SQLTable(self.table_name, self.pd_sql, df).table.tometadata(self.pd_sql.meta)

    def split_insert_and_update(self, df):
        # self.table.select(  df[self.primary_key]
        pass

    def insert(self, df):
        self.gen_sql_table(df)
        errors = []
        df = format_timestamp(df)
        with self.connection.cursor() as cursor:
            sql_template = "select 1 from %s where %%s" % self.table_name
            for r in xrange(len(df)):
                s = df.iloc[r]
                d = clear_dict_nan_value(s.to_dict())
                where = "%s='%s'" % (self.primary_key, d[self.primary_key])
                sql = sql_template % where
                cursor.execute(sql)
                try:
                    if cursor.fetchone():
                        self.table.update().where(where).values(d).execute()
                    else:
                        self.table.insert(d).execute()
                except Exception, e:
                    print e
                    errors.append(d[(self.primary_key, str(e))])
        return errors

    def update(self, df):
        for r in xrange(len(df)):
            self.table.update(df.iloc[r].to_dict()).execute()

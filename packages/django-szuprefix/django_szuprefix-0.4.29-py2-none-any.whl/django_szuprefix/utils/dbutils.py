#!/usr/bin/env python   
# -*- coding:utf8 -*-   
# Author:DenisHuang
# Date:2013/11/7
# Usage:
from django.db import connections

db = connections['default']
cursor = db.cursor()
cursor._defer_warnings = True


#
# all_types = {}
# all_types["integer"] = ["tinyint", "smallint", "mediumint", "int", "bigint"]
# all_types["decimal"] = ["double", "float", "decimal"]
# all_types["time"] = ["time", "date", "datetime", "timestamp", "year"]
# all_types["string"] = ["char", "varchar", "text", "enum"]
#
#
# def genAllFieldTypesTable(cursor, fieldTypes):
#     tmp_table = "tmp_YxbUm87N13F"
#     fs = ",".join(
#         ["f%s %s" % (t, t == "enum" and "enum('a')" or t == "varchar" and "varchar(1)" or t) for t in fieldTypes])
#     cursor.execute("create table if not exists %s (%s)" % (tmp_table, fs))
#     cursor.execute("select * from %s limit 1" % tmp_table)
#     d = dict([(fd[0][1:], fd[1]) for fd in cursor.description])
#     cursor.execute("drop table if exists %s " % tmp_table)
#     return d
#
#
# #
# # print genAllFieldTypesTable(cursor,reduce(lambda x,y:x+y,all_types.values())
# #
# fieldTypeCodes = {'smallint': 2,
#                   'enum': 254,
#                   'varchar': 253,
#                   'timestamp': 7,
#                   'int': 3,
#                   'mediumint': 9,
#                   'decimal': 246,
#                   'float': 4,
#                   'year': 13,
#                   'datetime': 12,
#                   'char': 254,
#                   'tinyint': 1,
#                   'bigint': 8,
#                   'text': 252,
#                   'time': 11,
#                   'double': 5,
#                   'date': 10}
#
# fieldCodeTypes = dict([(v, k) for k, v in fieldTypeCodes.iteritems()])
#
# fieldCategories = {}
# for cat, types in all_types.iteritems():
#     for type in types:
#         fieldCategories[type] = cat
#         fieldCategories[fieldTypeCodes[type]] = cat
#
#
# def cursorDescription2MapList(cursor):
#     global fieldCategories
#     l = []
#     m = {}
#     for fd in cursor.description:
#         d = {'name': fd[0],
#              'verboseName': fd[0],
#              'category': fieldCategories[fd[1]]}
#         l.append(d)
#         m[fd[0]] = d
#     return m, l
#
#
# def cursorDescription2SortedDict(cursor):
#     from collections import OrderedDict
#     # from django.http.request import SortedDict
#     m = OrderedDict()
#     for fd in cursor.description:
#         d = {'name': fd[0],
#              'verboseName': fd[0],
#              'category': fieldCategories[fd[1]]}
#         m[fd[0]] = d
#     return m


def get_table_fields(conn, table_name):
    with conn.cursor() as cursor:
        from collections import OrderedDict
        d = OrderedDict()
        for row in conn.introspection.get_table_description(cursor, table_name):
            name = row[0]
            field_type = conn.introspection.get_field_type(row[1], row)
            d[name] = dict(name=name, type=field_type)

        return d


def execute_sql(sql, db_name='default'):
    cur = connections[db_name].cursor()
    return cur.execute(sql), cur


def getDB(dbName='default'):
    return connections[dbName]


def getDBOptionals():
    return [(k, v["HOST"]) for k, v in connections.databases.iteritems()]


def django_db_setting_2_sqlalchemy(sd):
    emap = {"mysql": "mysql+mysqldb"}
    engine = sd['ENGINE'].split(".")[-1]
    engine = emap.get(engine, engine)
    charset = sd.get("OPTIONS", {}).get("charset")
    params = charset and "?charset=%s" % charset or ""
    return "%s://%s:%s@%s/%s%s" % (engine, sd['USER'], sd['PASSWORD'], sd['HOST'], sd['NAME'], params)


def db_sqlalchemy_str(db):
    return django_db_setting_2_sqlalchemy(connections[db].settings_dict)

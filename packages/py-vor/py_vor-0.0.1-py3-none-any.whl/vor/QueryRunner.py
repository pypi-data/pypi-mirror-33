# -*- coding: utf-8 -*-

"""QueryRunner
Object to run queries from SQL files and return them in a specified format.
Author: ksco92
"""

import pyodbc
import socket

import pandas as pd
import pg8000
import pymysql

from vor.tools.upload_to_s3 import upload_to_s3
from vor.tools.write_to_csv import write_to_csv


##########################################
##########################################
##########################################
##########################################


class QueryRunner:

    def __init__(self, engine, host, port, username, password, schema, sql_file, autocommit=False, returns_rows=False,
                 text_to_replace=None, replace_text_with=None, include_headers=True, return_as='nested_list',
                 results_file=None, aws_access_key_id=None, aws_secret_access_key=None, aws_region_name='us-east-1',
                 aws_bucket_name=None, aws_file_path='', **kwargs):
        self.engine = engine
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.schema = schema
        self.autocommit = autocommit
        self.returns_rows = returns_rows
        self.sql_file = sql_file
        self.text_to_replace = text_to_replace
        self.replace_text_with = replace_text_with
        self.include_headers = include_headers
        self.return_as = return_as
        self.results_file = results_file
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region_name = aws_region_name
        self.aws_bucket_name = aws_bucket_name
        self.aws_file_path = aws_file_path

        for key, value in kwargs.items():
            setattr(self, key, value)

    ##########################################
    ##########################################

    def execute_all(self):

        """Executes the results of all the queries in the specified file and returns the results of the last one in the
        specified format."""

        cur = self.create_cursor()
        statements = self.get_statements()
        results = []

        for statement in statements:
            results = self.execute_statement(cur, statement)

        return self.return_results_as(results)

    ##########################################
    ##########################################

    def create_cursor(self):

        """Creates a cursor based on the engine provided to the runner."""

        if self.engine == 'mysql':
            conn = pymysql.connect(host=self.host, port=self.port, user=self.username, passwd=self.password,
                                   db=self.schema, autocommit=self.autocommit, connect_timeout=36000, local_infile=True,
                                   max_allowed_packet=16 * 1024, charset='utf8')

        elif self.engine in ('redshift', 'postgresql'):

            conn = pg8000.connect(user=self.username, password=self.password, host=self.host, port=self.port,
                                  database=self.schema)
            conn._usock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            if self.autocommit:
                conn.autocommit = True

        elif self.engine == 'sqlserver':

            conn = pyodbc.connect(driver="{SQL Server}", server=self.host + ',' + str(self.port), database=self.schema,
                                  uid=self.username, pwd=self.password, autocommit=self.autocommit)

        else:
            return None

        return conn.cursor()

    ##########################################
    ##########################################

    def execute_statement(self, cur, statement):

        """Executes a SQL statement using the provided cursor."""

        query_results = []
        column_names = []

        cur.execute(statement)

        if self.returns_rows:

            for col in cur.description:
                if self.engine in ('mysql', 'sqlserver'):
                    column_names.append(col[0])
                elif self.engine in ('redshift', 'postgresql'):
                    column_names.append(col[0].decode("utf-8"))

            query_results.append(column_names)

            for row in cur:
                row = [str(n) for n in row]
                query_results.append(list(row))

        else:
            return None

        return query_results

    ##########################################
    ##########################################

    def get_statements(self):

        """Reads the queries in the provided file and replaces the desired text."""

        with open(self.sql_file) as f:
            query = f.read()
            f.close()

        for ttr, rtw in zip(self.text_to_replace, self.replace_text_with):
            query = query.replace(ttr, rtw)

        queries = query.split(';')
        queries = filter(None, queries)

        return queries

    ##########################################
    ##########################################

    def return_results_as(self, results):

        """Returns the results of a statement in the specified format."""

        if self.return_as == 'nested_list':
            if self.include_headers:
                return results
            else:
                return results[1:]

        elif self.return_as == 'pd_dataframe':
            results = pd.DataFrame(results[1:], columns=results[0])
            return results

        elif self.return_as == 'csv_file':
            if self.include_headers:
                write_to_csv(self.results_file, results)
            else:
                write_to_csv(self.results_file, results[1:])
            return None

        elif self.return_as == 'dict':
            keys = results[0]
            values = results[1:]
            output = []

            for row in values:
                output.append(dict(zip(keys, row)))

            output = {'data': output}
            return output

        elif self.return_as == 's3_upload':
            if self.include_headers:
                write_to_csv(self.results_file, results)
            else:
                write_to_csv(self.results_file, results[1:])

            upload_to_s3(self.results_file, self.aws_bucket_name, self.aws_file_path,
                         aws_region_name=self.aws_region_name, aws_access_key_id=self.aws_access_key_id,
                         aws_secret_access_key=self.aws_secret_access_key)

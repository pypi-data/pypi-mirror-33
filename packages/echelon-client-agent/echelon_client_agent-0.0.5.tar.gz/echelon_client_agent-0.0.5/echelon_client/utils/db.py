# -*- coding: utf-8 -*-
import pytz
import logging
import sqlite3
import uuid
import urllib

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from utils.config_loader import ConfigSectionMap
from utils.utils import print_info


class DbCredentials(object):

    def __init__(self):
        self.conn = sqlite3.connect('crendentials.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS credentials('''
            '''id INTEGER PRIMARY KEY AUTOINCREMENT, '''
            '''str_conexion text, server_receptor text, sql_lector text, '''
            '''lapse_seconds text, table_update text, id_name_update text, '''
            '''field_update text)''')

    def insert(self, **values):
        sql = (
            "insert or replace into credentials (str_conexion, "
            "server_receptor, sql_lector, lapse_seconds, table_update, "
            "id_name_update, field_update) values "
            """('%s', '%s', "%s", '%s', '%s', '%s', '%s')""" % (
                values['str_conexion'],
                values['server_receptor'],
                values['sql_lector'],
                values['lapse_seconds'],
                values['table_update'],
                values['id_name_update'],
                values['field_update']
            )
        )
        self.cursor.execute("delete from credentials;")
        self.cursor.execute(sql)
        self.conn.commit()

    def dictfetchall(self, result):
        """
        Return all rows from a cursor as a dict"
        """

        columns = [
            'id',
            'str_conexion',
            'server_receptor',
            'sql_lector',
            'lapse_seconds',
            'table_update',
            'id_name_update',
            'field_update',
        ]

        return dict(zip(columns, result or ('', '', '', '', '', '', '', '')))

    def get(self):
        sql = "select * from credentials;"
        rows = self.cursor.execute(sql)
        rows = rows.fetchone()
        self.conn.commit()

        return self.dictfetchall(rows)

    def check_string_con(self, string):
        string = string.strip()
        try:
            first_split = string.rsplit('@', 1)
            first_part_first_split = first_split[0]
            if first_part_first_split == "":
                return False, None, None, None, None, None, None
            second_part_first_split = first_split[1]
            if second_part_first_split == "":
                return False, None, None, None, None, None, None
        except:
            return False, None, None, None, None, None, None

        try:
            second_split = first_part_first_split.split(':')
            engine = second_split[0]
            if engine == "":
                return False, None, None, None, None, None, None
            user = second_split[1]
            if user == "":
                return False, None, None, None, None, None, None
            if '//' not in user:
                return False, None, None, None, None, None, None
            user = user.split('//')[1]
            password = second_split[2]
        except:
            return False, None, None, None, None, None, None

        try:
            host_port_name_db = second_part_first_split.split('/')
            host_port = host_port_name_db[0]
            if host_port == "":
                return False, None, None, None, None, None, None
            host_ports = host_port.split(':')
            host = host_ports[0]
            if host == "":
                return False, None, None, None, None, None, None
            port = host_ports[1]
            if port == "":
                return False, None, None, None, None, None, None
            name_db = host_port_name_db[1]
            if name_db == "":
                return False, None, None, None, None, None, None
        except:
            return False, None, None, None, None, None, None

        return True, engine, user, password, host, port, name_db

    def check_host_port_receptor(self, string):
        try:
            host_port = string.split(':')
            host = host_port[0]
            if host == "":
                return False, None, None
            port = host_port[1]
            if port == "":
                return False, None, None
        except:
            return False, None, None

        return True, host, port


def change_lat_lng(number):
    """
    Function returns the number in string format and if its negative or
     positive

    :param number: Positive or negative number

    :return: Tuple with number and P or N
    """

    return (
        str(number) if number > 0 else str(number * -1),
        'P' if number > 0 else 'N'
    )


def dictfetchall(result):
    """
    Return all rows from a cursor as a dict"
    """

    columns = [
        'row_id', 'idd', 'timestamp', 'lat', 'lng',
        'speed', 'course', 'altitude', 'satellites'
    ]

    bufferr = [
        dict(zip(columns, row))
        for row in result
    ]

    answer = list()
    for b in bufferr:
        track = {
            'row_id': b['row_id'],
            'idd': b['idd'],
            'date': b['timestamp'].strftime("%d%m%y"),
            'time': b['timestamp'].strftime("%H%M%S"),
            'lat1': change_lat_lng(b['lat'])[0],
            'lat2': change_lat_lng(b['lat'])[1],
            'lng1': change_lat_lng(b['lng'])[0],
            'lng2': change_lat_lng(b['lng'])[1],
            "speed": b['speed'],
            "course": b['course'],
            "altitude": b['altitude'],
            "satellites": b['satellites']
        }
        answer.append(track)

    return answer


def to_utc_str(datetime_with_tz, format='%Y-%m-%d %H:%M:%S'):
    """
    change time zoned date time into utc time.

    :param datetime_with_tz: datetime with time zone
    :param format: string with desired date format

    :return: datime in string format
    """
    datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)

    return datetime_in_utc.strftime(format)


def set_config_db(**data):

    return {
        'db_engine': data['engine'],
        'db_name': data['name'],
        'db_host': data['host'],
        'db_user': data['user'],
        'db_pass': data['pass'],
        'db_port': data['port'],
    }


def get_config_values(config_file):
    """
    Get config values

    :param config_file: config.ini file path

    :return: parsed values found in the config ini file
    """
    database_engine = ConfigSectionMap(config_file, "database")['engine']
    database_name = ConfigSectionMap(config_file, "database")['name']
    database_host = ConfigSectionMap(config_file, "database")['host']
    database_user = ConfigSectionMap(config_file, "database")['user']
    database_pass = ConfigSectionMap(config_file, "database")['pass']
    database_port = ConfigSectionMap(config_file, "database")['port']

    return {
        'db_engine': database_engine,
        'db_name': database_name,
        'db_host': database_host,
        'db_user': database_user,
        'db_pass': database_pass,
        'db_port': database_port,
    }


def get_engine(config_values):
    """
    Takes config values and connects to db engine.

    :param config_values: dictionary containing db connection params and query
    :return: engine, sesssion and WiseTrack object
    """
    Base = automap_base()
    string_con = config_values

    if (('Server' in config_values) or ('Driver' in config_values) or
            ('Database' in config_values) or ('DRIVER' in config_values)):
        quoted = urllib.parse.quote_plus(config_values)
        string_con = 'mssql+pyodbc:///?odbc_connect={quoted}'.format(
            quoted=quoted)
    try:
        engine = create_engine(string_con)
        Base.prepare(engine, reflect=True)
        session = Session(engine)

        return (engine, session)
    except Exception as err:
        print("Some problem with connection to DB: ", err)

    return (None, None)


def required_fields(query):
    forbidden_words = [
        'as date', 'as time',
        'as lat', 'as lng',
        'speed', 'course',
        'altitude', 'satellites'
    ]
    query_words = "".join(
        (char if char.isalpha() else " ") for char in query).split()
    for word in query_words:
        if word.lower() in forbidden_words:
            return word

    return False


def simple_sql_injection_check(query):
    """
    check if query has some kind of sql injection

    :param query: string containg and sql query
    :return: False if is a safe sql select query otherwise invalid word found
    """
    forbidden_words = ['drop', 'insert', 'alter', 'grant', 'truncate', 'alter']
    query_words = "".join(
        (char if char.isalpha() else " ") for char in query).split()
    for word in query_words:
        if word.lower() in forbidden_words:
            return word

    return False


def perform_query(query, engine):
    """
    Perform query in db engine

    :param query: string sql query
    :param engine: sqlanchemy engine object

    :result: list of objects from query execution result
    """

    sql_inject = simple_sql_injection_check(query)
    if sql_inject:
        raise Exception(
            'Forbidden word found in query: {word}'.format(word=sql_inject))
    text_query = text(query)
    conn = engine.connect()
    try:
        result = conn.execute(text_query).fetchall()
    except Exception as e:
        message = 'Error executing query: {error}'.format(error=e)
        logging.error(message)
        print(message)

        return []

    return result


def elements_to_ids(elems):
    vec = [str(e['row_id']) for e in elems]

    return ','.join(vec)


def update_query(table, id_name, state, elements, engine, widget=None):

    result = None
    for e in elements:
        sql = "update %s set %s = '%s' where %s = %s" % (
            table, state, str(e['uuid']), id_name, e['row_id'])

        print_info("sql update: %s" % sql, widget)
        logging.info("sql update: %s" % sql)
        text_query = text(sql)
        conn = engine.connect()
        try:
            result = conn.execute(text_query)
        except Exception as e:
            message = 'Error executing query: {error}'.format(error=e)
            logging.error(message)

            return []

    return result


def set_uuids_dict(data):

    for t in data:
        t['uuid'] = uuid.uuid4()

    return data

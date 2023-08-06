# -*- coding: utf-8 -*-
import os

from utils.constants import (
    STRING_TITLE,
    STRING_CONEXION_DB,
    STRING_HOST_PORT,
    STRING_LAPSE_TIME,
    STRING_CONFIGURATION,
    STRING_CONFIGURATION_SQL,
    STRING_SENT,
    STRING_WRONG_OPTION,
    STRING_MENU_CONF,
    STRING_SQL_SENTENCE,
    STRING_TABLE_UPDATE,
    STRING_ID_NAME_UPDATE,
    STRING_FIELD_UPDATE,
    STRING_LESS_DATA,
)


class EchelonConsole:

    string_title = STRING_TITLE
    string_conexion_db = STRING_CONEXION_DB
    string_host_port = STRING_HOST_PORT
    string_lapse_time = STRING_LAPSE_TIME
    string_configuration = STRING_CONFIGURATION
    string_configuration_sql = STRING_CONFIGURATION_SQL
    string_sent = STRING_SENT
    string_wrong_option = STRING_WRONG_OPTION
    string_menu_conf = STRING_MENU_CONF
    string_sql_sentence = STRING_SQL_SENTENCE
    string_table_update = STRING_TABLE_UPDATE
    string_id_name_update = STRING_ID_NAME_UPDATE
    string_field_update = STRING_FIELD_UPDATE
    string_less_data = STRING_LESS_DATA
    conexion_db = ''
    host_port = ''
    lapse_time = ''
    sentence_sql = ''
    table_update = ''
    id_name_update = ''
    field_update = ''

    def __init__(self, db_object):
        self.db_object = db_object
        data_db = self.db_object.get()
        self.conexion_db = data_db['str_conexion']
        self.host_port = data_db['server_receptor']
        self.lapse_time = data_db['lapse_seconds']
        self.sentence_sql = data_db['sql_lector']
        self.table_update = data_db['table_update']
        self.id_name_update = data_db['id_name_update']
        self.field_update = data_db['field_update']

    def save_total_conf_db(self):
        data_save = {
            'str_conexion': self.conexion_db,
            'server_receptor': self.host_port,
            'lapse_seconds': self.lapse_time,
            'sql_lector': self.sentence_sql,
            'table_update': self.table_update,
            'id_name_update': self.id_name_update,
            'field_update': self.field_update,
        }
        self.db_object.insert(**data_save)

    def save_sql(self):
        pass

    def print_main_menu(self):
        conf_conf = "(1) Configuración" if (
            self.conexion_db == "" or self.host_port == "" or
            self.lapse_time == "") else "(1) Configuración (LISTO)"

        conf_sql = "(2) Ingresar SQL" if (
            self.sentence_sql == "" or self.table_update == "" or
            self.id_name_update == "" or
            self.field_update == "") else "(2) Ingresar SQL (LISTO)"

        print(conf_conf)
        print(conf_sql)
        print("(3) Enviar\n")

    def main_options(self, option):
        while option != "1" and option != "2" and option != "3":
            os.system('clear')
            self.print_main_title()
            self.print_main_menu()
            print("Opción incorrecta")
            option = input("Opción: ")

        return option

    def print_main_title(self):
        print(self.string_title)

    def show_main_menu(self, error=''):
        os.system('clear')
        self.print_main_title()
        self.print_main_menu()
        print(error)
        option = input("Opción: ")
        option = str(option).strip()

        return self.main_options(option)

    def show_sub_menu(self):

        return input(self.string_menu_conf)

    def edit_conf(self):
        os.system('clear')
        self.print_main_title()
        print(self.string_configuration)
        print("\n")
        self.conexion_db = input(self.string_conexion_db)
        self.host_port = input(self.string_host_port)
        self.lapse_time = input(self.string_lapse_time)

    def edit_sql(self):
        os.system('clear')
        self.print_main_title()
        print(self.string_configuration_sql)
        print("\n")
        self.sentence_sql = input(self.string_sql_sentence)
        print("\n ---- Datos para la actualización ---- \n")
        self.table_update = input(self.string_table_update)
        self.id_name_update = input(self.string_id_name_update)
        self.field_update = input(self.string_field_update)

    def show_conf_step(self):
        os.system('clear')
        self.print_main_title()
        print(self.string_configuration)
        print('\n{0}{1}'.format(self.string_conexion_db, self.conexion_db))
        print('{0}{1}'.format(self.string_host_port, self.host_port))
        print('{0}{1}\n'.format(self.string_lapse_time, self.lapse_time))

    def show_sql_step(self):
        os.system('clear')
        self.print_main_title()
        print(self.string_configuration_sql)
        print('\n{0}{1}'.format(self.string_sql_sentence, self.sentence_sql))
        print("\n ---- Datos para la actualización ---- \n")
        print('{0}{1}'.format(self.string_table_update, self.table_update))
        print('{0}{1}'.format(self.string_id_name_update, self.id_name_update))
        print('{0}{1}\n'.format(self.string_field_update, self.field_update))

    def wait_editable_option(self, option):
        while option != "e" and option != "g" and option != "s":
            os.system('clear')
            self.print_main_title()
            print(self.string_configuration)
            self.show_conf_step()
            print(self.string_wrong_option)
            option = input(self.string_menu_conf)

        return option

    def inside_conf(self):
        self.edit_conf()
        self.show_conf_step()

        return self.show_sub_menu()

    def inside_sql(self):
        self.edit_sql()
        self.show_sql_step()

        return self.show_sub_menu()

    def inside_send(self):
        os.system("clear")
        self.print_main_title()
        print(self.string_sent)
        print("Conectando a Base de datos local ... ")

    def check_confs_sqls_data(self):
        if (
            self.conexion_db == "" or self.host_port == "" or
            self.lapse_time == "" or self.sentence_sql == "" or
            self.table_update == "" or self.id_name_update == "" or
                self.field_update == ""):
            return False

        return True

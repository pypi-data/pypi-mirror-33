# -*- coding: utf-8 -*-
import os
import logging
import argparse
import sys

import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import messagebox
from twisted.internet import reactor

from classes.echelon_client_factory import EchelonClientFactory
from utils.db import (
    get_engine,
    DbCredentials,
    set_config_db,
)
from utils.constants import *


class Application(tk.Frame):
    conexion_label = None

    def __init__(self, master=None):
        self.db_cred = DbCredentials()

        data_db = self.db_cred.get()
        self.conexion_db = data_db['str_conexion']
        self.host_port = data_db['server_receptor']
        self.lapse_time = data_db['lapse_seconds']
        self.sentence_sql = data_db['sql_lector']
        self.table_update = data_db['table_update']
        self.id_name_update = data_db['id_name_update']
        self.field_update = data_db['field_update']

        self.master = master
        super().__init__(master)

        self.create_widgets()
        self.fill_fields()
        self.factory = EchelonClientFactory()

    def save_total_conf_db(self):
        data_save = {
            'str_conexion': self.conexion_field.get('1.0', 'end').strip(),
            'server_receptor': self.server_field.get('1.0', 'end').strip(),
            'lapse_seconds': self.lapse_time_field.get('1.0', 'end').strip(),
            'sql_lector': self.sql_lector_field.get('1.0', 'end').strip(),
            'table_update': self.table_update_field.get('1.0', 'end').strip(),
            'id_name_update': self.id_update_field.get('1.0', 'end').strip(),
            'field_update': self.state_update_field.get('1.0', 'end').strip(),
        }
        self.db_cred.insert(**data_save)

    def create_widgets(self):
        self.master.title(TITLE)
        self.master.geometry("1000x860")

        self.query_label = tk.Label(
            self, text=QUERY_LABEL, anchor=tk.W,
            font='Helvetica 18 bold').grid(row=1, column=0, columnspan=2)

        self.conexion_label = tk.Label(
            self, text=STRING_CONEXION_DB, height=3).grid(row=2, column=0)

        self.server_label = tk.Label(
            self, text=STRING_HOST_PORT, height=3).grid(row=2, column=1)

        self.conexion_field = tk.Text(self, width=50, height=1)
        self.conexion_field.grid(row=3, column=0)

        self.server_field = tk.Text(self, width=50, height=1)
        self.server_field.grid(row=3, column=1)

        self.sql_lector_label = tk.Label(
            self, text=STRING_SQL_SENTENCE, height=3).grid(
            row=4, column=0, columnspan=2)
        self.sql_lector_field = tk.Text(self, width=120, height=10)
        self.sql_lector_field.grid(row=5, column=0, columnspan=2)

        self.label_lapse_time = tk.Label(
            self, text=STRING_LAPSE_TIME, height=3).grid(row=6, column=0)
        self.label_table_update = tk.Label(
            self, text=STRING_TABLE_UPDATE, height=3).grid(row=6, column=1)

        self.lapse_time_field = tk.Text(self, width=60, height=1)
        self.lapse_time_field.grid(row=7, column=0)
        self.table_update_field = tk.Text(self, width=60, height=1)
        self.table_update_field.grid(row=7, column=1)

        self.label_id_update = tk.Label(
            self, text=STRING_ID_NAME_UPDATE, height=3).grid(row=8, column=0)
        self.id_update_field = tk.Text(self, width=60, height=1)
        self.id_update_field.grid(row=9, column=0)

        self.label_state_update = tk.Label(
            self, text=STRING_FIELD_UPDATE, height=3).grid(row=8, column=1)
        self.state_update_field = tk.Text(self, width=60, height=1)
        self.state_update_field.grid(row=9, column=1)

        self.send_button = tk.Button(
            self, text=SEND_BUTTON, fg="blue",
            command=self.send_query)
        self.send_button.grid(
            row=11, column=0, columnspan=2, pady=20, ipadx=40, ipady=10)

        self.logger_field = tkst.ScrolledText(
            master=self,
            wrap=tk.WORD,
            width=120,
            height=20,
        )
        self.logger_field.grid(
            row=12, column=0, columnspan=2, pady=20)

        self.pack()

    def fill_fields(self):
        self.conexion_field.insert('1.0', self.conexion_db)
        self.server_field.insert('1.0', self.host_port)
        self.sql_lector_field.insert('1.0', self.sentence_sql)
        self.lapse_time_field.insert('1.0', self.lapse_time)

        self.table_update_field.insert('1.0', self.table_update)
        self.id_update_field.insert('1.0', self.id_name_update)
        self.state_update_field.insert('1.0', self.field_update)

    def check_require_fields(self):
        fields = list()
        fields.append(self.conexion_field.get('1.0', 'end').strip())
        fields.append(self.server_field.get('1.0', 'end').strip())
        fields.append(self.sql_lector_field.get('1.0', 'end').strip())
        fields.append(self.lapse_time_field.get('1.0', 'end').strip())
        fields.append(self.table_update_field.get('1.0', 'end').strip())
        fields.append(self.id_update_field.get('1.0', 'end').strip())
        fields.append(self.state_update_field.get('1.0', 'end').strip())

        for field in fields:
            if field == "":
                return False
        return True

    def check_require_fields_update(self):
        conexion_field = self.conexion_field.get('1.0', 'end').strip()
        server_field = self.server_field.get('1.0', 'end').strip()
        sql_updater_field = self.sql_updater_field.get('1.0', 'end').strip()
        if(conexion_field == "" or server_field == "" or
                sql_updater_field == ""):
            return False

        return True

    def update_query(self):
        if self.check_require_fields_update():
            pass
        else:
            messagebox.showwarning(WARNING_TITLE, WARNING_CONFIG_UPDATE)

    def send_query(self):
        self.save_total_conf_db()
        self.logger_field.insert('1.0', "Enviando...\n")

        def send():
            conexion_field = self.conexion_field.get('1.0', 'end').strip()
            server_field = self.server_field.get('1.0', 'end').strip()
            sql_lector_field = self.sql_lector_field.get('1.0', 'end').strip()
            lapse_time_field = self.lapse_time_field.get('1.0', 'end').strip()

            table = self.table_update_field.get('1.0', 'end').strip()
            id_name = self.id_update_field.get('1.0', 'end').strip()
            field = self.state_update_field.get('1.0', 'end').strip()

            engine, session = get_engine(conexion_field)
            self.logger_field.insert(
                tk.INSERT, "Conectando a Base de Datos local\n")

            is_correct, host, port = self.db_cred.check_host_port_receptor(
                server_field)

            if is_correct:
                self.factory.set_data(
                    sql_lector_field, engine, table, id_name, field,
                    self.logger_field)
                self.factory.set_lapse_time(lapse_time_field)

                reactor.connectTCP(host, int(port), self.factory)
                reactor.run()
            else:
                messagebox.showwarning(
                    WARNING_TITLE, WARNING_HOST_PORT_RECEPTOR)

        if self.check_require_fields():
            self.send_button.config(state="disabled")
            root.after(1000, send)

        else:
            messagebox.showwarning(WARNING_TITLE, WARNING_CONFIG)


if __name__ == '__main__':

    script_path = os.path.abspath(os.path.dirname(sys.argv[0])) + '/'

    if not os.path.exists(script_path + 'logs'):
        try:
            os.makedirs(script_path + 'logs')
        except OSError as exc:
            pass

    if not os.path.exists(script_path + 'conf'):
        try:
            os.makedirs(script_path + 'conf')
        except OSError as exc:
            pass

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        '--author',
        action='version',
        help="show author's info and exit",
        version='Eduardo Chauca Gallegos <eduardo@inka-labs.com>')

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s 0.0.4')

    parser.add_argument(
        '-c',
        '--config_file',
        action="store",
        dest="config_file",
        help="configuration file path",
        default=script_path + 'conf/config.ini')

    parser.add_argument(
        '-l',
        '--log_file',
        action="store",
        dest="log_file",
        help="logging file path",
        default=script_path + "logs/echelon_command.log")

    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        format='%(levelname)s : %(asctime)s :: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

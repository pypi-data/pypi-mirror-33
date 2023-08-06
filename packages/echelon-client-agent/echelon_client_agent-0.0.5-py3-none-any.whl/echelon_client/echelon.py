# -*- coding: utf-8 -*-
import os
import logging
import argparse
import sys

from utils.config_loader import ConfigSectionMap
from classes.echelon_agent import EchelonAgent


def get_config_values(config_file):
    echelon_db = ConfigSectionMap(config_file, "echelon")['db']
    echelon_server_receptor = ConfigSectionMap(
        config_file, "echelon")['server_receptor']
    echelon_sql_lector = ConfigSectionMap(config_file, "echelon")['sql_lector']
    echelon_lapse_seconds = ConfigSectionMap(
        config_file, "echelon")['lapse_seconds']
    echelon_table_update = ConfigSectionMap(
        config_file, "echelon")['table_update']
    echelon_id_field_update = ConfigSectionMap(
        config_file, "echelon")['id_field_update']
    echelon_state_field_update = ConfigSectionMap(
        config_file, "echelon")['state_field_update']

    return {
        'echelon_db': echelon_db,
        'echelon_server_receptor': echelon_server_receptor,
        'echelon_sql_lector': echelon_sql_lector,
        'echelon_lapse_seconds': echelon_lapse_seconds,
        'echelon_table_update': echelon_table_update,
        'echelon_id_field_update': echelon_id_field_update,
        'echelon_state_field_update': echelon_state_field_update,
    }


def echelon_client(script_path, config_file):
    config_values = get_config_values(config_file)
    echelon_agent = EchelonAgent()
    echelon_agent.set_values(**config_values)
    echelon_agent.send_query(
        config_values['echelon_table_update'],
        config_values['echelon_id_field_update'],
        config_values['echelon_state_field_update']
    )


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

    echelon_client(script_path, args.config_file)

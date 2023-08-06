# -*- coding: utf-8 -*-
import configparser


def ConfigSectionMap(config_file, section):
    """
    Handle config section file

    :param config_file: string with file path of config file
    :param section: string, name of the secion inside config file

    :return: dictionary containging params found in config file
    """
    dict1 = {}
    Config = configparser.ConfigParser()
    Config.read(config_file)
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print(("skip: %s" % option))
        except:
            print(("exception on %s!" % option))
            dict1[option] = None

    return dict1

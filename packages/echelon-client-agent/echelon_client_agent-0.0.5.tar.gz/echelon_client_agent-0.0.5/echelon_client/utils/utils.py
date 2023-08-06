# -*- coding: utf-8 -*-
import datetime


def strdate_to_show(strdate):

    return datetime.datetime.strptime(strdate, '%d%m%y').strftime('%d-%m-%Y')


def strtime_to_show(strtime):

    return datetime.datetime.strptime(strtime, '%H%M%S').strftime('%H:%M:%S')


def print_info(msg, widget):
    if widget:
        import tkinter as tk
        widget.insert(tk.INSERT, msg + '\n')
    else:
        print(msg)

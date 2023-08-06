# -*- coding: utf-8 -*-
import uuid
import logging

from twisted.internet.protocol import Protocol
from utils.constants import FAKE_HEADER
from utils.utils import strdate_to_show, strtime_to_show, print_info


class EchelonEncoder(Protocol):

    gpsec = None
    idd = None
    type_package = None
    message = ''
    date = ''
    time = ''
    time = ''
    lat1 = ''
    lat2 = ''
    lng1 = ''
    lng2 = ''
    speed = ''
    course = ''
    altitude = ''
    satellites = ''
    uuid = ''
    data = dict()

    def __init__(self, data, widget=None):
        self.data = data
        self.widget = widget

    def set_header(self, **data):
        self.gpsec = data['gpsec']
        self.type_package = data['type_package']

    def set_message(self, **data):
        self.idd = data['idd']
        self.date = data['date']
        self.time = data['time']
        self.lat1 = data['lat1']
        self.lng1 = data['lng1']
        self.lat2 = data['lat2']
        self.lng2 = data['lng2']
        self.speed = int(data['speed'])
        self.course = int(data['course'])
        self.altitude = int(data['altitude'])
        self.satellites = int(data['satellites'])
        self.uuid = str(data['uuid'])

    def create_uuid(self):
        self.uuid = uuid.uuid4()

    def create_message(self):
        self.message = '{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10}'.format(
            self.date,
            self.time,
            self.lat1,
            self.lat2,
            self.lng1,
            self.lng2,
            self.speed,
            self.course,
            self.altitude,
            self.satellites,
            self.uuid,
        )

    def create(self):
        self.create_message()

        return '{0}#{1}#{2}#{3}\r\n'.format(
            self.gpsec,
            self.idd,
            self.type_package,
            self.message
        )

    def print_header_fields(self):
        return '{0:10}{1:15}{2:15}{3:15}{4:15}{5:5}\n{6:-^80s}'.format(
            'Placa',
            'Fecha',
            'Hora',
            'Latitud',
            'Longitud',
            'Velocidad',
            '-',
        )

    def show_message(self):

        return '{0:10}{1:15}{2:15}{3:15}{4:15}{5:5} km'.format(
            self.idd,
            strdate_to_show(self.date),
            strtime_to_show(self.time),
            self.lat1,
            self.lng1,
            self.speed,
        )

    def send_message(self):
        header = {
            "gpsec": FAKE_HEADER["gpsec"] or self.gpsec,
            "type_package": FAKE_HEADER["type_package"] or self.type_package
        }

        messages = list()
        for element in self.data:
            self.set_header(**header)
            self.set_message(**element)
            messages.append((self.show_message(), self.create().encode()))

        return messages

    def connectionMade(self):
        print_info(self.print_header_fields(), self.widget)
        for msg, enconded_msg in self.send_message():
            print_info(msg, self.widget)
            logging.info(msg)
            self.transport.write(enconded_msg)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print_info("Enviando ...", self.widget)

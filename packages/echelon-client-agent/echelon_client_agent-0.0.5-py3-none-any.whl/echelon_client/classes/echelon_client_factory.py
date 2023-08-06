# -*- coding: utf-8 -*-
import time

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory

from .echelon_encoder import EchelonEncoder
from utils.db import (
    perform_query,
    dictfetchall,
    update_query,
    set_uuids_dict,
)

from utils.utils import print_info


class EchelonClientFactory(ClientFactory):

    num_package = 0

    def set_data(
            self, sql_lector_field, engine, table, id_name, field,
            widget=None):
        self.widget = widget
        self.sql_lector_field = sql_lector_field
        self.engine = engine
        self.table = table
        self.id_name = id_name
        self.field = field
        result = perform_query(self.sql_lector_field, self.engine)
        self.data = dictfetchall(result)
        self.data = set_uuids_dict(self.data)
        update_query(
            table, id_name, field, self.data, self.engine, self.widget)
        self.num_package = self.num_package + 1

    def set_lapse_time(self, lapse_time):
        self.lapse_time = int(lapse_time)

    def clientConnectionFailed(self, connector, reason):
        print_info("Connection Failed", self.widget)
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        result = perform_query(self.sql_lector_field, self.engine)
        self.data = dictfetchall(result)
        self.data = set_uuids_dict(self.data)
        update_query(
            self.table, self.id_name, self.field, self.data, self.engine,
            self.widget)
        print_info(
            "Paquete %s Enviado ------------------------------\n\n" % str(
                self.num_package), self.widget)
        self.num_package = self.num_package + 1
        connector.connect()
        time.sleep(self.lapse_time)

    def buildProtocol(self, addr):

        return EchelonEncoder(self.data, self.widget)

# -*- coding: utf-8 -*-
STATUS_OK = '1'
STATUS_CONVERTION_ERROR = '2'
STATUS_WRONG_TOKEN = '3'
STATUS_DUPLICATED = '4'
STATUS_INTERNAL_ERROR = '5'

IDENTIFIER_INDEX = 0
TIMESTAMP_INDEX = 1
LATITUDE_INDEX = 2
LONGITUDE_INDEX = 3
COURSE_INDEX = 4
SPEED_INDEX = 5
TRACK_ID = 6
TITLE = "Agente de Comunicación"
LAPSE_TIME_SECONDS = 3
CONEXION_LABEL_TEXT = "Cadena de conexión (motor://usuario:contraseña@host:puerto/nombre_bd)"
SERVER_LABEL_TEXT = "Servidor destino (host:puerto)"
QUERY_LABEL = "Ingresa datos correctos para conexion y consulta"
QUERY_LABEL_FORM = "Ingresa las credenciales para la base de datos"
SQL_LECTOR_TEXT = "Lector SQL"
SQL_UPDATER_TEXT = "Actualizador SQL"
SEND_BUTTON = "Enviar"
UPDATE_BUTTON = "Actualizar"
SAVE_BUTTON = "Guardar"
WARNING_TEXT_SQL = "Debes insertar una sentecia SQL"
WARNING_TITLE = "Atención"
WARNING_CONFIG = "Todos los campos son requeridos"
WARNING_CONFIG_UPDATE = "Todos los campos son requeridos"
WARNING_CONEX = "Cadena de conexión no cumple el formato"
WARNING_HOST_PORT_RECEPTOR = "No cumple el formato host:puerto destino"
ENGINE = "Motor de Base de Datos"
HOST = "Host"
PORT = "Puerto"
NAME = "Nombre de Base de Datos"
USER = "Usuario"
PASSWORD = "Contraseña"
TAB_1 = "Emisor"
TAB_2 = "Configuración Base de Datos"

FAKE_HEADER = {
    "gpsec": "GPSEC",
    "type_package": "DP"
}

FAKE_DATA = [
    {
        "idd": "V9B-939",
        "date": "030518",
        "time": "1000",
        "lat1": "13.424",
        "lat2": "P",
        "lng1": "15.2313",
        "lng2": "N",
        "speed": "40",
        "course": "287",
        "altitude": "3000",
        "satellites": "6"
    },
    {
        "idd": "V9B-939",
        "date": "030518",
        "time": "1000",
        "lat1": "13.424",
        "lat2": "P",
        "lng1": "15.2313",
        "lng2": "N",
        "speed": "40",
        "course": "287",
        "altitude": "3001",
        "satellites": "4"
    },
    {
        "idd": "V9B-939",
        "date": "030518",
        "time": "1001",
        "lat1": "13.424",
        "lat2": "P",
        "lng1": "15.2313",
        "lng2": "N",
        "speed": "40",
        "course": "287",
        "altitude": "3201",
        "satellites": "4"
    }
]

STRING_TITLE = "########### AGENTE DE COMUNICACIONES #############\n\n"
STRING_CONEXION_DB = 'CADENA DE CONEXIÓN (MOTOR://USUARIO:CONTRASEÑA@HOST:PUERTO/NOMBRE_BD): '
STRING_HOST_PORT = 'SERVIDOR DE DESTINO (HOST:PUERTO): '
STRING_LAPSE_TIME = 'LAPSO DE TIEMPO DE ENVIO (SEGUNDOS): '
STRING_CONFIGURATION = '####### Configuración #######'
STRING_CONFIGURATION_SQL = '####### Configuración SQL #######'
STRING_SENT = '####### ENVIO #######'
STRING_WRONG_OPTION = 'Opción incorrecta'
STRING_LESS_DATA = 'Ingrese todos los datos'
STRING_MENU_CONF = '(e)Editar - (g)Guardar - (s)Salir: '
STRING_SQL_SENTENCE = 'SENTENCIA SQL: '
STRING_TABLE_UPDATE = 'TABLA DONDE SE ACTUALIZARÁ EL ESTADO: '
STRING_ID_NAME_UPDATE = 'NOMBRE DEL CAMPO IDENTIFICADOR UNICO EN LA TABLA: '
STRING_FIELD_UPDATE = 'NOMBRE DEL CAMPO DE ESTADO EN LA TABLA: '

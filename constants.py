# Bases de datos
MDB_SERVER_ADDR = '192.168.4.220'
MDB_SERVER_PORT = 3306
MDB_USER = 'stt'
MDB_USER_PASSWORD = '122122'
MDB_DB_NAME = 'dbstorm'

SDB_SERVER_ADDR = '192.168.4.220'
SDB_SERVER_PORT = 3306
SDB_USER = 'stt'
SDB_USER_PASSWORD = '122122'
SDB_DB_NAME = 'datos_sitrad'

# Mapeo Model Number -> Table Name
INSTRUMENT_MODEL_NUMBER = {
    73:'mt512elog',
    44:'mt543ri',
    16:'mt512Ri',
    26:'ti33ri',
    53:'mt530super'
    }

# Comandos
COMMANDS = {
    1:'QUERY',
    0:'FIN'
}

# Logging level
# Use CRITICAL for production
# Use DEBUG for debugging
logLevel = 'DEBUG'

# Dash debug server mode
dashDebugMode = True
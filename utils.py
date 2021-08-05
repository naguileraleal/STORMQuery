import constants as const
import mariadb

def nuevaConexionMDB():
    """
    Crea una nueva conexion a la base de datos MDB
    Devuelve el conector
    """
    try:
        conn = mariadb.connect(
            user=const.MDB_USER,
            password=const.MDB_USER_PASSWORD,
            host=const.MDB_SERVER_ADDR,
            port=const.MDB_SERVER_PORT,
            database=const.MDB_DB_NAME,
            autocommit=True
        )
        return conn
    except mariadb.Error as e:
        print(e)

def nuevaConexionSDB():
    """
    Crea una nueva conexion a la base de datos SDB
    Devuelve el conector
    """
    try:
        conn = mariadb.connect(
            user=const.SDB_USER,
            password=const.SDB_USER_PASSWORD,
            host=const.SDB_SERVER_ADDR,
            port=const.SDB_SERVER_PORT,
            database=const.SDB_DB_NAME,
            autocommit=True
        )
        return conn
    except mariadb.Error as e:
        print(e)

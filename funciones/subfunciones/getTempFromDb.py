import logging
import mariadb
import utils
from math import trunc
import pandas as pd
import constants as const


def get_temp_from_db(dbName,instrumentAddress,dateRange,probe=None):
    '''
    Busca en las bases de datos de Sitrad  los datos en la columna 'temperatura' entre las fechas dadas, del instrumento dado
    Si tiene muchas columnas de temperatura, busca en la columna 'temperatura'+str(probe)

    Parametros
    ----------
    dbName : str
        El nombre de la base de datos de sitrad en la que se quiere buscar
    
    instrumentAddress : int
        La direccion del instrumento en la red de Sitrad

    dateRange : tuple(datetime.datetime, datetime.datetime)
        Rango de fechas de la consulta
    
    probe : int
        La probe del instrumento de la que se quere obtener la temperatura. Para equipos con una sola probe vale None.

    Devuelve
    --------
    dataPeriods : list(pandas.DataFrame)
        Lista de dataframes. Cada uno contiene datos (timestamp, temp) del instrumento en el periodo dateRange.

    '''

    # dateRange es una tupla con dos objetos de la clase datetime


    # 1. ins = get all from instrumentos where endereco = instrumentAddress
    # 2. for instrumento in ins
    # 3.a. temps = get all from INSTRUMENT_MODEL_NUMBER[instrumento.endereco] where id = instrumento.id and date in range
    # 3.b. append(temps,result)
    
    try:
        # Asumo que la base de datos de sitrad es unica
        # TODO: Usar dbName para poder buscar en mas de una base de datos
        db = utils.nuevaConexionSDB()
        c = db.cursor()

        logging.debug('probe is None: {}'.format(probe is None))
        logging.debug('probe: {}'.format(probe))
       
        # Obtener todos los instrumentos con la direccion de red que busco
        # La mayoria de los instrumentos tienen una sola probe de temperatura
        # Otros como el ti33ri tienen tres. La columna 'probe' de la tabla 'gabinetes' indica que probe es la que corresponde al gabinete.

        c.execute(
            "SELECT id, modelo, endereco FROM instrumentos WHERE endereco=?",(instrumentAddress,)
            )
        
        result = c.fetchall()
        instruments = pd.DataFrame([*result],columns=['id','modelo','direccion'])

        logging.debug('sample instruments: ')
        logging.debug(instruments)

        # Cuando se cambia un termostato Full Gauge por otro en el mismo instrumento, la endereco queda igual para ambos, ya no se cumple que tengo una endereco por instrumento.
        dataPeriods = list()
        data = pd.DataFrame()

        for i in range(0,instruments.shape[0]):
            # BETWEEN selecciona datos incluyendo los valores limites

            tableName = const.INSTRUMENT_MODEL_NUMBER[instruments['modelo'].iloc[i]]

            if probe:
                query = (
                    "SELECT data, TRUNCATE(temperatura{0}/10,1) FROM {1} WHERE id={2} AND data BETWEEN '{3}' AND '{4}'"
                        ).format(
                            probe,
                            tableName,
                            str(instruments.id.values[i]).strip('[]'),
                            dateRange[0].strftime('%Y-%m-%d %H:%M:%S'),
                            dateRange[1].strftime('%Y-%m-%d %H:%M:%S')
                            )
            else:
                query = (
                    "SELECT data, TRUNCATE(temperatura/10, 1) FROM {0} WHERE id={1} AND data BETWEEN '{2}' AND '{3}'"
                         ).format(
                             tableName,
                             str(instruments.id.values[i]).strip('[]'),
                             dateRange[0].strftime('%Y-%m-%d %H:%M:%S'),dateRange[1].strftime('%Y-%m-%d %H:%M:%S')
                         )
           
            logging.debug('query: {}'.format(query))

            c.execute(query)
            result = c.fetchall()

            if result:
                data = pd.DataFrame([*result],columns=['time','temp'])
                dataPeriods.append(data)
                logging.debug('data:')
                logging.debug(data.to_string())

        db.close()

        return dataPeriods

    except mariadb.Error as e:
        print(e)
        db.close()
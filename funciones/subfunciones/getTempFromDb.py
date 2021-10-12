import logging
import mariadb
import utils
from math import trunc
import pandas as pd
import constants as const


def get_temp_from_db(dbName,instrumentAddress,dateRange):
    # Esta funcion busca en las bases de datos de Sitrad
    # los datos en la columna 'temperatura' entre las
    # fechas dadas, del instrumento dado.

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

        logging.debug('dateRange: {} {}'.format(dateRange[0],dateRange[1]))

        real_instrumentAddress = float(instrumentAddress)
        int_instrumentAddress = int(trunc(real_instrumentAddress))
       
        # Obtener todos los instrumentos con la direccion de red que busco
        # Para un ti33, instrumentAddress tiene formato 'address.probe'
        # Para el resto de los instrumentos, tiene formato 'address'
        c.execute(
            "SELECT id, modelo, endereco FROM instrumentos WHERE endereco=?",(int_instrumentAddress,)
            )
        
        result = c.fetchall()
        instruments = pd.DataFrame([*result],columns=['id','modelo','direccion'])

        probe = trunc((real_instrumentAddress - int_instrumentAddress)*10)
        probe = str(probe)
        instrumentAddress = str(int_instrumentAddress)

        # Cuando se cambia un termostato Full Gauge por otro en el mismo instrumento, la endereco queda igual para
        # ambos, ya no se cumple que tengo una endereco por instrumento.
        dataPeriods = list()
        data = pd.DataFrame()

        for i in range(0,instruments.shape[0]):
            # BETWEEN selecciona datos incluyendo los valores limites
            if probe == '0':
                query = (
                    "SELECT data, TRUNCATE(temperatura/10, 1) FROM {0} WHERE id LIKE {1} AND data BETWEEN '{2}' AND '{3}'"
                         ).format(
                             const.INSTRUMENT_MODEL_NUMBER[instruments['modelo'].iloc[i]],
                             str(instruments.id.values[i]).strip('[]'),
                             dateRange[0].strftime('%Y-%m-%d %H:%M:%S'),dateRange[1].strftime('%Y-%m-%d %H:%M:%S')
                         )

            else:
                query = (
                        "SELECT data, TRUNCATE(temperatura{0}/10,1) FROM {1} WHERE id LIKE {2} AND data BETWEEN '{3}' AND '{4}'"
                         ).format(
                             probe,
                             str(instruments.nombre.values[i]).strip('[]'),
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
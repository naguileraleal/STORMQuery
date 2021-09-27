# ARCHIVO imports.py
# En este archivo pongo todos los imports de todas las funciones y subfunciones de la libreria



import sqlite3

import time

import traceback

from datetime import datetime
from datetime import timedelta

from os import listdir
from os.path import isfile, join
from os import system
import sys

import serial

from plotly.offline import offline
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np

import logging
from math import trunc
import constants as const
import mariadb
import utils
import pandas as pd


# ARCHIVO getTempFromDb.py
import logging


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

            data = data.append(
                pd.DataFrame([*result],columns=['time','temp']), ignore_index=True
                )

            logging.debug('data:')
            logging.debug(data.to_string())

        db.close()

        return data

    except mariadb.Error as e:
        print(e)
        db.close()


# ARCHIVO waitForBarcode.py
# "p" es un puerto serial ya abierto
# Esta funcion devuelve una string
def wait_for_barcode(p):
    done = False
    rcv = ''

    try:
        while not done:
            if p.in_waiting > 0:
                c = p.read()
                rcv += str(c.decode('utf-8','strict'))
                
                if p.in_waiting == 0:
                    done = True
        p.flush()
        rcv = rcv.strip('\r\n')
        return rcv
    
    except serial.SerialException:
        print("wait_for_barcode: ERROR")
        return False




# ARCHIVO isSample.py
import logging


def is_sample(idMuestra,c):

    res = False

    # idMuestra es de la forma ['codigoMuestra','codigoSubMuestra']

    query = "select id from muestras where muestra like '{0}' and submuestra like '{1}'".format(
        idMuestra[0],
        idMuestra[1]
        )

    logging.debug(query)
    c.execute(query)
    c.fetchall()
    logging.debug('rowcount: {}'.format(c.rowcount))
    if (c.rowcount > 0):
        res = True

    return res



# ARCHIVO getDbNames.py
# FUNCTION THAT GETS NAME OF ALL DBs
# IN 'mypath' DIRECTORY

def get_db_names(mypath):

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles = list(filter(lambda n: n.endswith('.db'),onlyfiles))
    
    # newer db's go first
    # newer db's have higher number in their names
    # all db's are named like 'datosNUMBER.db'
    onlyfiles.sort(key = nameskey, reverse=True)

    return onlyfiles


# AUX FUNCTION FOR SORTING LIST OF NAMES
def nameskey(name):
    # Get number from name
    name = name[5: name.find('.')]
    if name == '':
        return 0
    else:
        return int(name)



# ARCHIVO isInstrument.py
def is_instrument(instrument,c):
    # La variable c es el cursor de base de datos
    try: # placeholder ':nombre', paso un dictionary a execute()
         # con los argumentos de la query, {'nombre':variable}
        query = "SELECT codigo FROM instrumentos WHERE codigo=:inst"
        res = c.execute(query,{"inst":instrument}).fetchall()
        if res:
            return True
        else:
            return False
    except:
        print("is_instrument: ERROR")
        traceback.print_exc()
        return False



# ARCHIVO getTemp.py
# FUNCTION THAT GETS TEMP AND TIME DATA FROM
# ALL DB's
def get_temp(dbnames, path, instrumentAddress, dateRange):
    # dbnames is a list with all available db's
    # dbnames is ordered from newest to oldest db
    # instrumentAddress is a string
    # dateRange es una tupla con dos objetos tipo datetime

    # First, check if current db has initDate
    # Current db's name is 'datos.db'
    dateFormat = '%Y-%m-%d %H:%M:%S'

    # Check most current db
    data = get_temp_from_db('datos.db',instrumentAddress,dateRange)
    i=1
    
    if not data.empty:
        # Time data is ordered by date, earlier timestamps come first
        oldest = datetime.strptime(data.time[0],dateFormat)
        # If all the data I'm looking for is in here, there's nothing left to do
        if oldest <= dateRange[0]:
            # it's done
            return data
    
    if data.empty or (datetime.strptime(data.time[0],dateFormat) > dateRange[0] ):
        while (data.empty or (oldest > dateRange[0] ) ) and (i < (len(dbnames)-1)) :
            newData = get_temp_from_db(dbnames[i],path,instrumentAddress,dateRange)
            # New data is older, so must go first
            if not newData.empty:
                data = newData.append(data)
                oldest = datetime.strptime(newData['time'][0],dateFormat)
            i+=1
    return data



# ARCHIVO getSampleInstruments.py
import logging


def get_sample_instruments(idMuestra, c):

    # idMuestra es de la forma ['codigoMuestra','codigoSubMuestra']

   # Esta funcion devuelve de todos los instrumentos en los que estuvo la muestra:
   # endereco, ingreso y egreso de la muestra


    ############################################################################

    '''
    La query larga hace:

    1. Q2 = SELECT<muestras.muestra = sampleId[0] AND muestras.submuestra =  sampleId[1] and muestras.deleted = 0>(muestras)
    2. Q1 = PROJECT<id,nombre,endereco>(gabinetes)
    3. J1 = Q1 JOIN<Q1.id = Q2.idInstrumento> Q2
    4. RES = PROJECT<nombre,ingreso,salida,endereco>(J1)
    '''

    RES = "select nombre,ingreso,salida,endereco from (\
        ((select id,nombre,endereco from gabinetes where deleted=0) as q1)\
        join ((select idInstrumento,ingreso,salida from muestras where \
        deleted=0 and muestra=? and submuestra=?) as q2)\
        on q1.id = q2.idinstrumento)"

    c.execute(
        RES,
        (idMuestra[0],
        idMuestra[1])
        )
    
    res = c.fetchall()

    data = pd.DataFrame(
        [*res],columns=['nombre','ingreso','salida','endereco']
    )


    return data


# ARCHIVO isCommand.py
# Funcion que evalua si el string recibido es un codigo de orden
# "codigo" es un string que corresponde a un codigo de barra

def is_command(barcode):
    
    if const.COMMANDS.get(int(barcode),'NULL') != 'NULL':
        return barcode
    else:
        return False


# ARCHIVO codigosError.py
from enum import Enum

class CodigosError(Enum):
    NO_EXISTE_MUESTRA = -1
    FECHA_INVALIDA = -2
    NO_HAY_DATOS = -3


# ARCHIVO init.py
def init():
    # Mensaje de bienvenida
    f = open(const.MESSAGE_PATH,mode='r')
    print(f.read())
    f.close()

    retrycount = 0

    portOpen = False
    foundDB = False
    while not portOpen and not foundDB: #POSIBLE ERROR EN PRECEDENCIA DE OPERADORES
        try:
            p = serial.Serial('COM4',
                      9600,
                      bytesize=8,
                      parity='N',
                      stopbits=1,
                      xonxoff=0,
                      timeout=0,
                      rtscts=0)
            portOpen = p.is_open
            print(portOpen)

            print("Buscando bases de datos de STORM")
            onlyfiles = [f for f in listdir(const.MDB_FOLDER) if isfile(join(const.MDB_FOLDER, f))]
            onlyfiles = list(f for f in onlyfiles if f.startswith('muestras.db'))
            print(" Archivos encontrados:",onlyfiles)

            # Cuando una lista esta vacia, vale False
            if not onlyfiles:
                # Crear DB 'muestras.db'
                print("Base de datos muestras.db no encontrada")
                print(" Creando una nueva")
                mdb = utils.nuevaConexionMDB()
                mdbc = mdb.cursor()
                mdbc.execute('CREATE TABLE "instrumentos" (\
                    "codigo"	TEXT NOT NULL UNIQUE,\
                    "endereco"	REAL NOT NULL UNIQUE,\
                    "tabla" TEXT NOT NULL UNIQUE)')
                mdb.commit()
                mdb.close()

            foundDB = True

        except serial.SerialException:
            print("ERROR: COM4 no pudo ser abierto/configurado correctamente")
            print(" Intento de nuevo en 5 segundos")
            time.sleep(5)
            retrycount += 1
            if retrycount > 3:
                print("  No fue posible abrir COM4")
                return False
            
        except sqlite3.DatabaseError:
            traceback.print_exc()
            print("ERROR: Hubo problemas creando la base de datos \"muestras.db\"")
            return False
    return p

# Termina init()



# ARCHIVO query_sin_lector.py
from datetime import date
from funciones.codigosError import CodigosError
import logging

def query_sin_lector(muestra, subMuestra, fechaInicio, fechaFin, plot):
    '''
    Parametros
    ----------
    muestra : str
        Codigo de muestra de la muestra

    subMuestra : str
        Codigo de sub-muestra de la muestra

    fechaInicio : str
        Limite inferior del rango de fechas de la consulta (Formato ISO)
    
    fechaFin : str
        Limite superior del rango de fechas de la consulta (Formato ISO)
    
    Devuelve
    --------
    Si se genera un grafico (no vacio) para la muestra, devuelve un plot de tipo plotly.go.Figure
    
    Si la consulta retorna vacia, devuelve CodigosError.NO_HAY_DATOS

    Si no existe una muestra con los identificadores dados en la entrada, devuelve CodigosError.NO_EXISTE_MUESTRA
    '''

    logging.debug('fechaInicio: {} fechaFin: {}'.format(fechaInicio,fechaFin))

    res = None

    mdb = utils.nuevaConexionMDB()
    c = mdb.cursor()

    if is_sample([muestra,subMuestra], c):

        sample_ins = get_sample_instruments([muestra,subMuestra], c)
        # sample_ins tiene para cada instrumento de la muestra
        # ingreso, egreso y endereco
        logging.debug('muestra: {} submuestra: {}'.format(muestra,subMuestra))
        logging.debug('sample_ins:')
        logging.debug(sample_ins)

        data = pd.DataFrame()

        # A get_temp le paso type(dateRange) = (datetime, datetime)
        for index, row in sample_ins.iterrows():
            #%H:%M:%S
            ingreso = datetime.strptime(str(row['ingreso']),'%Y-%m-%d %H:%M:%S').date()
            egreso = datetime.strptime(str(row['salida']),'%Y-%m-%d %H:%M:%S').date()

            if fechaInicio == None:
                fechaInicio = date(1970,1,1)
            else:
                fechaInicio = date.fromisoformat(fechaInicio)
            
            if fechaFin == None:
                fechaFin = datetime.now().date()
            else:
                fechaFin = date.fromisoformat(fechaFin)
            

            # Si la muestra salio del instrumento antes del comienzo de mi busqueda (egreso < fechaInicio)
            # no tiene sentido buscar datos en este instrumento

            # Si la muestra entro al instrumento despues de finalizada mi busqueda (ingreso > fechaFin)
            # tampoco tiene sentido buscar datos en este instrumento

            if egreso > fechaInicio and ingreso < fechaFin:

                if ingreso >= fechaInicio:
                    idate = ingreso
                else:
                    idate = fechaInicio

                if egreso <= fechaFin:
                    edate = egreso
                else:
                    edate = fechaFin

                logging.debug('idate: {} edate: {}'.format(idate,edate))

                data = get_temp_from_db('',
                    row['endereco'],
                    ( idate, edate )
                    )
                if not data.empty:
                    plot.add_trace(
                        go.Scatter(
                            x=data.iloc[:,0],
                            y=data.iloc[:,1],
                            name=row['nombre']
                        )
                    )

        if data.empty:
            res = CodigosError.NO_HAY_DATOS
            logging.debug(
                'no hay datos para muestra: {} submuestra: {}'.format(muestra, subMuestra)
                )
        else:

            plot.update_layout(
                title='Muestra: {} Submuestra: {}'.format(muestra,subMuestra),
                xaxis_title='Fecha',
                yaxis_title='Temperatura ºC',
                legend_title='Gabinete',
                showlegend=True
            )


            logging.debug('se encontraron {} datos para muestra: {} submuestra: {}'.format(data.shape[0],muestra,subMuestra))

        mdb.close()

        return res

    else:
        return CodigosError.NO_EXISTE_MUESTRA





from datetime import datetime

import pandas as pd

import logging

import utils
from funciones.codigosError import CodigosError
from funciones.subfunciones.isSample import is_sample
from funciones.subfunciones.getTempFromDb import get_temp_from_db
from funciones.subfunciones.getSampleInstruments import get_sample_instruments

import plotly.graph_objects as go


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

    data = list()

    if is_sample([muestra,subMuestra], c):

        sample_ins = get_sample_instruments([muestra,subMuestra], c)
        # sample_ins tiene para cada instrumento de la muestra
        # ingreso, egreso y endereco
        logging.debug('muestra: {} submuestra: {}'.format(muestra,subMuestra))
        logging.debug('sample_ins:')
        logging.debug(sample_ins)

        if not fechaInicio:
            fechaInicio = datetime(1970,1,1,0,0,0)
        else:
            fechaInicio = datetime.fromisoformat(fechaInicio)
            
        if not fechaFin:
            fechaFin = datetime.now()
        else:
            fechaFin = datetime.fromisoformat(fechaFin)
        
        logging.debug('fechaInicio: {} fechaFin: {}'.format(fechaInicio,fechaFin))

        # A get_temp le paso type(dateRange) = (datetime, datetime)
        for index, row in sample_ins.iterrows():
            #%H:%M:%S
            ingreso = datetime.strptime(str(row['ingreso']),'%Y-%m-%d %H:%M:%S')
            if pd.isnull(row['salida']):
                egreso = datetime.now()
            else:
                egreso = datetime.strptime(str(row['salida']),'%Y-%m-%d %H:%M:%S')

            logging.debug('ingreso: {} egreso: {}'.format(ingreso,egreso))

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
                    ( idate, edate ),
                    probe=row['probe']
                    )
                
                logging.debug("get_temp_from_db result:")
                logging.debug(data)

                if data:
                    for dataPeriod in data:
                        plot.add_trace(
                            go.Scatter(
                                x=dataPeriod.iloc[:,0],
                                y=dataPeriod.iloc[:,1],
                                name=row['nombre'],
                                mode='lines+markers',
                                connectgaps=False
                            )
                        )

        if not data:
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


            #logging.debug('se encontraron {} datos para muestra: {} submuestra: {}'.format(data.shape[0],muestra,subMuestra))

        mdb.close()

        return res

    else:
        return CodigosError.NO_EXISTE_MUESTRA


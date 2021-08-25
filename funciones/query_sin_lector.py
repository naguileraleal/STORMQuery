from datetime import date
from funciones.codigosError import CodigosError
import logging

def query_sin_lector(muestra, subMuestra, fechaInicio, fechaFin, plot):
    # TODO: De que tipo es fechaInicio fechaFin??

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


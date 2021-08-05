import logging


def query_sin_lector():
    mdb = utils.nuevaConexionMDB()
    c = mdb.cursor()

    while True:
        print('Ingrese codigos de muestra y submuestra')
        sample = input('Muestra: ')
        subSample = input('Sub Muestra: ')

        # Una variable para continuar con el programa una vez que el usuario entre correctamente las fechas
        goAhead=False

        if is_sample([sample,subSample], c):

            print('Entre fechas en formato YYYY,MM,DD')
            print('Separe año mes y dia usando comas')
            print('Luego presione ENTER')

            while not goAhead:
                try:
                    initDate = input('Fecha de inicio:')
                    # Si la fecha de inicio es vacia, que busque desde el principio de la base de datos
                    if (len(initDate) == 0):
                        initDate = datetime(1970,1,1)
                        print("Desde el primer dato")
                    else:
                        initDate = initDate.split(sep=',')
                        initDate = datetime(int(initDate[0]), int(initDate[1]), int(initDate[2]))

                    finDate = input('Fecha de fin:')
                    # Si la fecha de fin es vacia, que busque hasta el ultimo dato que tenga
                    if (len(finDate) == 0):
                        finDate = datetime.now() + timedelta(days=1) # Mañana
                        print("Hasta el ultimo dato")
                    else:
                        finDate = finDate.split(sep=',')
                        finDate = datetime(int(finDate[0]), int(finDate[1]), int(finDate[2]))

                    if initDate == datetime(1970,1,1):
                        pass
                    else:
                        print(f'Desde: {initDate}')
                    if finDate > datetime.now():
                        pass
                    else:
                        print(f'Hasta: {finDate.strftime("%Y-%m-%d %H:%M:%S")}')

                    goAhead=True

                except ValueError:
                    print('Lo que escribio no es una fecha valida')
                    print('Por favor, escriba una fecha de acuerdo al formato mencionado')
                    print('\n')

            sample_ins = get_sample_instruments([sample,subSample], c)
            # sample_ins tiene para cada instrumento de la muestra
            # ingreso, egreso y endereco
            logging.debug('muestra: {} submuestra: {}'.format(sample,subSample))
            logging.debug('sample_ins:')
            logging.debug(sample_ins)

            data = pd.DataFrame()

            print('Buscando datos')

            # A get_temp le paso type(dateRange) = (datetime, datetime)
            for index, row in sample_ins.iterrows():
                ingreso = datetime.strptime(str(row['ingreso']),'%Y-%m-%d %H:%M:%S')
                egreso = datetime.strptime(str(row['salida']),'%Y-%m-%d %H:%M:%S')

                # Si la muestra salio del instrumento antes del comienzo de mi busqueda (egreso < initDate)
                # no tiene sentido buscar datos en este instrumento

                # Si la muestra entro al instrumento despues de finalizada mi busqueda (ingreso > finDate)
                # tampoco tiene sentido buscar datos en este instrumento

                if egreso > initDate and ingreso < finDate:

                    if ingreso >= initDate:
                        idate = ingreso
                    else:
                        idate = initDate

                    if egreso <= finDate:
                        edate = egreso
                    else:
                        edate = finDate

                    prevlen = len(data.index)

                    data = data.append(
                        get_temp_from_db('',
                        row['endereco'],
                        ( idate, edate )
                        )
                        )
                    newlen = len(data.index)
                    if prevlen !=  newlen:
                        sys.stdout.flush()
                        sys.stdout.write('\r')
                        print('{} datos encontrados'.format(len(data.index)))


            if data.empty:
                print(
                    'No hay datos para la muestra {} entre {} y {}'.format(sample,initDate,finDate))
            else:
                plot = px.line(data_frame=data, x='time', y='temp')
                offline.plot(
                    plot,
                    filename=f"{sample}_{initDate.strftime('%Y-%m-%d')}\
                        _{finDate.strftime('%Y-%m-%d')}.html",
                    auto_open=True)

            mdb.close()

            return

        elif is_command(sample) == 'FIN':
            print("Comando FIN leido, saliendo de QUERY")
            return

        else:
            print('Ese codigo no corresponde a una muestra')

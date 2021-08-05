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

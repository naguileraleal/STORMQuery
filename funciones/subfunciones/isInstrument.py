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

import logging


def is_sample(idMuestra,c):

    res = False

    # idMuestra es de la forma ['codigoMuestra','codigoSubMuestra']

    query = "select id from muestras where muestra={0} and submuestra={1}".format(
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

'''
    l = c.execute("SELECT tabla FROM instrumentos").fetchall()
    allInstrumentTables = list()
    for i in l:
        allInstrumentTables.append(i[0])

    for table in allInstrumentTables:
        query = "SELECT * FROM {0} WHERE muestra LIKE '{1}'".format(table,barcode)
        if c.execute(query).fetchall():
            return True
    return False
'''
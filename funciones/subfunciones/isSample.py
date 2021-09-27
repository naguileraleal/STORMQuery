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

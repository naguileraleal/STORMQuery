def get_sample_instruments(idMuestra, c):

    # idMuestra es de la forma ['codigoMuestra','codigoSubMuestra']

   # Esta funcion devuelve de todos los instrumentos en los que estuvo la muestra:
   # endereco, ingreso y egreso de la muestra


    ############################################################################

    '''
    La query larga hace:

    1. Q2 = SELECT<muestras.muestra = sampleId[0] AND muestras.submuestra =  sampleId[1] and muestras.deleted = 0>(muestras)
    2. Q1 = PROJECT<id,endereco>(gabinetes)
    3. J1 = Q1 JOIN<Q1.id = Q2.idInstrumento> Q2
    4. RES = PROJECT<ingreso,salida,endereco>(J1)
    '''

    RES = "select ingreso,salida,endereco from (\
        ((select id,endereco from gabinetes where deleted=0) as q1)\
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
        [*res],columns=['ingreso','salida','endereco']
    )

    return data
# Funcion que evalua si el string recibido es un codigo de orden
# "codigo" es un string que corresponde a un codigo de barra

def is_command(barcode):
    
    if const.COMMANDS.get(int(barcode),'NULL') != 'NULL':
        return barcode
    else:
        return False
import sys
from funciones.stormLib import *
import logging


def main():

    logging.basicConfig(
        filename='./log/query-{}.log'.format(
            datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
            ),
        level=logging.DEBUG,
        encoding='utf-8',
        format='%(levelname)s: %(filename)s - %(module)s - %(funcName)s - \
            %(lineno)d - %(message)s'
        )

    p = init()

    while True:

        print('Por favor, escanee un comando')
        code = wait_for_barcode(p)
        comm = is_command(code)
        
        if type(comm) is not bool:
            if comm == const.COMM_FIN:
                print('Comando FIN escaneado')
                c = input('Seguro que quiere salir del programa? Y/N:')
                if c == 'Y' or c == 'y':
                    p.close()
                    print('Hasta luego')
                    sys.exit()

            if comm == const.COMM_QUERY:
                print('Comando QUERY escaneado')
                query(p)

        else:
            print('El codigo escaneado no corresponde a un comando')
            print('Por favor, escanee un comando')

if __name__ == '__main__':
    main()
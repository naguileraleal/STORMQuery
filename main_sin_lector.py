import sys
from funciones.stormLib import *
import logging


def main():

    logging.basicConfig(
        filename='./log/harcoded-query-{}.log'.format(
            datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
            ),
        level=logging.DEBUG,
        encoding='utf-8',
        format='%(levelname)s: %(filename)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
        )

    while True:

        print('Por favor, escriba un comando')
        code = input('Comando: ')
        comm = const.COMMANDS[int(code)]
        
        if type(comm) is not bool:
            if comm == 'FIN':
                print('Comando FIN escaneado')
                c = input('Seguro que quiere salir del programa? Y/N:')
                if c == 'Y' or c == 'y':
                    print('Hasta luego')
                    sys.exit()

            if comm == 'QUERY':
                print('Comando QUERY escaneado')
                query_sin_lector()

        else:
            print('El codigo escaneado no corresponde a un comando')
            print('Por favor, escanee un comando')

if __name__ == '__main__':
    main()
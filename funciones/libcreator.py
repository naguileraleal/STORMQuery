# La gracia de generar este archivo es juntar todas las funciones en un solo archivo
# para importarlo a la hora de usar las funciones en el main o en los tests en vez
# de tener que importar todos los archivos uno por uno


# list all files in funciones
import os
from os import listdir
from os.path import join, isfile
import sys

os.chdir('./funciones')

mypath = "./subfunciones"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

newf = open("stormLib.py" ,"w+")


# Primero escribo todos los imports
newf.write('# ARCHIVO {}'.format('imports.py'))
newf.write('\n')
f = open('imports.py', 'r')
newf.write(f.read())
f.close()
newf.write('\n\n\n')

nogo = ['__init__.py','main.py','test.py','libcreator.py'
        ,'stormLib.py','constants.py','imports.py']

for file in onlyfiles:
    if file not in nogo:
        newf.write('# ARCHIVO {}'.format(file))
        newf.write('\n')
        f = open('./subfunciones/'+file,'r')
        newf.write(f.read())
        f.close()
        newf.write('\n\n\n')

mypath = "./"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for file in onlyfiles:
    if file not in nogo:
        newf.write('# ARCHIVO {}'.format(file))
        newf.write('\n')
        f = open(file,'r')
        newf.write(f.read())
        f.close()
        newf.write('\n\n\n')

newf.close()

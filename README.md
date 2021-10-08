# STORMQuery
# Instrucciones de instalacion
## Requerimientos previos
- Python 3.8.10
- pip
- Mariadb Connector/C

## Linux
1. Descargar el repositorio y descomprimirlo en una nueva carpeta llamada "STORMQuery"
2. Abrir una terminal en el directorio del proyecto
3. Ejecutar `python -m venv env`
4. Ejecutar `source env/bin/activate` para activar el entorno virtual creado
5. Ejecutar `pip install wheel`
6. Ejecutar `pip install -r requirements.txt` para instalar dependencias
7. En `STORMQuery/constants.py` configurar la ip y credenciales del servidor de bases de datos
    + Las constantes con prefijo "MDB_" corresponden a la base de datos de muestras
    + Las constantes con prefijo "SDB_" corresponden a la base de datos de sitrad

## Windows
1. Descargar el repositorio y descomprimirlo en una nueva carpeta llamada "STORMQuery"
2. Abrir una terminal en el directorio del proyecto
3. Ejecutar `python -m venv env`
4. Ejecutar `env\Scripts\activate` para activar el entorno virtual creado
5. Ejecutar `pip install wheel`
6. Ejecutar `pip install -r requirements.txt` para instalar dependencias
7. En `STORMQuery/constants.py` configurar la ip y credenciales del servidor de bases de datos
    + Las constantes con prefijo "MDB_" corresponden a la base de datos de muestras
    + Las constantes con prefijo "SDB_" corresponden a la base de datos de sitrad
---
# Instrucciones de Ejecucion
## Linux
1. Abrir una terminal en el directorio `STORMQuery`
2. Ejecutar `source env/bin/activate`
3. Ejecutar `python main_dash.py`
4. Abrir en un navegador la url `localhost:1111`

## Windows
1. Abrir una terminal en el directorio `STORMQuery`
2. Ejecutar `env\Scripts\activate`
3. Ejecutar `python main_dash.py`
4. Abrir en un navegador la url `localhost:1111`

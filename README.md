# STORMQuery
# Instrucciones de instalacion
## Requerimientos previos
- Python 3.8.x o superior
- pip

## Linux
1. Descargar el repositorio y descomprimirlo en una nueva carpeta llamada "STORMQuery"
2. Abrir una terminal en el directorio del proyecto
3. Ejecutar `python -m venv env`
4. Ejecutar `source env/bin/activate` para activar el entorno virtual creado
5. Ejecutar `pip install -r requirements.txt --no-cached-dir` para instalar dependencias
6. En `STORMQuery/constants.py` configurar la ip y credenciales del servidor de bases de datos
    + Las constantes con prefijo "MDB_" corresponden a la base de datos de muestras
    + Las constantes con prefijo "SDB_" corresponden a la base de datos de sitrad
---
# Instrucciones de Ejecucion
1. Abrir una terminal en el directorio `STORMQuery`
2. Ejecutar `source env/bin/activate`
3. Ejecutar `python main_dash.py`
4. Abrir en un navegador la url `localhost:1111`

# FUNCTION THAT GETS NAME OF ALL DBs
# IN 'mypath' DIRECTORY

def get_db_names(mypath):

    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    onlyfiles = list(filter(lambda n: n.endswith('.db'),onlyfiles))
    
    # newer db's go first
    # newer db's have higher number in their names
    # all db's are named like 'datosNUMBER.db'
    onlyfiles.sort(key = nameskey, reverse=True)

    return onlyfiles


# AUX FUNCTION FOR SORTING LIST OF NAMES
def nameskey(name):
    # Get number from name
    name = name[5: name.find('.')]
    if name == '':
        return 0
    else:
        return int(name)

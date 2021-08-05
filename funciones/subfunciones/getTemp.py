# FUNCTION THAT GETS TEMP AND TIME DATA FROM
# ALL DB's
def get_temp(dbnames, path, instrumentAddress, dateRange):
    # dbnames is a list with all available db's
    # dbnames is ordered from newest to oldest db
    # instrumentAddress is a string
    # dateRange es una tupla con dos objetos tipo datetime

    # First, check if current db has initDate
    # Current db's name is 'datos.db'
    dateFormat = '%Y-%m-%d %H:%M:%S'

    # Check most current db
    data = get_temp_from_db('datos.db',instrumentAddress,dateRange)
    i=1
    
    if not data.empty:
        # Time data is ordered by date, earlier timestamps come first
        oldest = datetime.strptime(data.time[0],dateFormat)
        # If all the data I'm looking for is in here, there's nothing left to do
        if oldest <= dateRange[0]:
            # it's done
            return data
    
    if data.empty or (datetime.strptime(data.time[0],dateFormat) > dateRange[0] ):
        while (data.empty or (oldest > dateRange[0] ) ) and (i < (len(dbnames)-1)) :
            newData = get_temp_from_db(dbnames[i],path,instrumentAddress,dateRange)
            # New data is older, so must go first
            if not newData.empty:
                data = newData.append(data)
                oldest = datetime.strptime(newData['time'][0],dateFormat)
            i+=1
    return data

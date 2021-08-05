# "p" es un puerto serial ya abierto
# Esta funcion devuelve una string
def wait_for_barcode(p):
    done = False
    rcv = ''

    try:
        while not done:
            if p.in_waiting > 0:
                c = p.read()
                rcv += str(c.decode('utf-8','strict'))
                
                if p.in_waiting == 0:
                    done = True
        p.flush()
        rcv = rcv.strip('\r\n')
        return rcv
    
    except serial.SerialException:
        print("wait_for_barcode: ERROR")
        return False


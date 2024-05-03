import mysql.connector

def connectDb():
    # Establece los detalles de la conexión
    configuracion = {
        'user': 'matiasrodr',
        'password': 'fisuMARswi966',
        'host': 'localhost',
        'database': 'tdf_automatic',
    }
    # Crea una conexión a la base de datos
    conexion = mysql.connector.connect(**configuracion)
    #Crea un cursor para ejecutar consultas SQL
    #cursor = conexion.cursor()
    return conexion

def saldosAll():
    conexion = connectDb()
    cursor = conexion.cursor()
    cursor.execute("select atms.Sucursal, atms.ATM, tdf.REM1, tdf.REM2, tdf.REM3, tdf.REM4, tdf.REMANENTE from tdf join atms on tdf.ATM = atms.ATM order by atms.Sucursal")
    saldos = cursor.fetchall()
    conexion.close()
    return saldos

def saldosBySucursal(sucursal):
    conexion = connectDb()
    cursor = conexion.cursor()
    cursor.execute("select atms.Sucursal, atms.ATM, tdf.REM1, tdf.REM2, tdf.REM3, tdf.REM4, tdf.REMANENTE from tdf join atms on tdf.ATM = atms.ATM where atms.Atencion=%s order by atms.Sucursal", sucursal)
    saldos = cursor.fetchall()
    conexion.close()
    return saldos

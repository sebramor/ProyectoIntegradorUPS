
#realizar las consultas e implementacion 
import pymysql

####Metodos para etiquetas 
#obtener lista de etiquetas
#pasando valores de 1 columna a 1 lista
def valoresColumna(data,numeroColumna):
  #obtiene valor de data.iloc[fila,columna]
  lista=[]
  for i in range(0,len(data.iloc[:,0])):
    #print(data.iloc[i,numeroColumna])
    lista.append(data.iloc[i,numeroColumna])
  
  return lista

def insertarProductoTipoProducto(nombre,descripcion,etiqueta):
    sql = ""




HOST = 'localhost'
PORT = 3306
USER = 'root'
PASSWD = ''
DB = 'db_solicitudfarmacia4'
CHARSET = 'utf8'


############### CONFIGURAR ESTO ###################
# Open database connection
def conectar():
    connection = pymysql.connect(host=HOST,
                             port=PORT,
                             user=USER,
                             passwd=PASSWD,
                             db=DB,
                             charset=CHARSET)
    return connection
##################################################

def ingresarSQL(sql):
    # prepare a cursor object using cursor() method
    db = conectar()
    cursor = db.cursor()

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()


    # desconectar del servidor
    db.close()

def obtenerUltimoID():
    # prepare a cursor object using cursor() method
    db = conectar()
    cursor = db.cursor()
    sql = "SELECT MAX(producto.COD_PRODUCTO) FROM producto"
    id=""
    try:
        # Execute the SQL command
        cursor.execute(sql)
        id = cursor.fetchone()[0]
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()


    # desconectar del servidor
    db.close()
    return id

def obtenerConsultaUnitaria(sql):
    # prepare a cursor object using cursor() method
    db = conectar()
    cursor = db.cursor()
    id=""
    try:
        # Execute the SQL command
        cursor.execute(sql)
        id = cursor.fetchone()
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        id=[None]
        db.rollback()


    # desconectar del servidor
    db.close()
    return id


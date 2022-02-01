import pandas as pd
#realizar las consultas e implementacion 
import pymysql
import metodos

df = pd.read_csv("medicamentosEtiquetados.csv")

nombres = metodos.valoresColumna(df,3)
descripcion = metodos.valoresColumna(df,4)
stock = metodos.valoresColumna(df,5)

def ingresarProductos(nombres,descripcion,stock):
    n = len(nombres)
    for i in range(n):
        sql = "INSERT INTO producto(producto.NOMBRE_PRODUCTO,producto.DESCRIPCION,producto.STOCK) "
        sql+= "VALUES ('"+str(nombres[i])+"','"+str(descripcion[i])+"',"+str(stock[i])+");"
        metodos.ingresarSQL(sql)
        

#id = metodos.obtenerUltimoID()
#print(id)
#sql="INSERT INTO producto(producto.NOMBRE_PRODUCTO,producto.DESCRIPCION,producto.STOCK) VALUES ('ejemplo2','descripcion',10);"
#metodos.ingresarSQL(sql)

ingresarProductos(nombres,descripcion,stock)
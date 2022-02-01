import pandas as pd
#realizar las consultas e implementacion 
import pymysql
import metodos

df = pd.read_csv("medicamentosEtiquetados.csv")

#print(df)

nombres = metodos.valoresColumna(df,3)
etiquetas = metodos.valoresColumna(df,6)

def subirEtiquetas(nombres,etiquetas):
    n = len(nombres)
    for i in range(n):
        sql = "SELECT producto.COD_PRODUCTO FROM producto WHERE producto.NOMBRE_PRODUCTO='"+str(nombres[i])+"';"
        id = metodos.obtenerConsultaUnitaria(sql)[0]
        #print(nombres[i],id)
        if(id!=None):
            sql = "INSERT INTO tipo_producto(tipo_producto.COD_PRODUCTO, tipo_producto.ID_TIPO_PRODUCTO) "
            sql+= "VALUES('"+str(id)+"','"+str(etiquetas[i])+"');"
            metodos.ingresarSQL(sql)

subirEtiquetas(nombres,etiquetas)








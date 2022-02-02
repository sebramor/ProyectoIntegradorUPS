#Se importan las librerias
from os import curdir
from tkinter import Menu
from turtle import setposition
from flask import Flask, make_response 
from flask import render_template, request, redirect, url_for, flash, session, escape
#para que se dejen ver las imagenes
from flask import send_from_directory
from flaskext.mysql import MySQL
from datetime import datetime
#importar para encriptar
import bcrypt
#para seleccionar fotografia
#modulo que permite entrar en la carpeta
import os

#from numpy import can_cast 

import metodos

#Crear el objeto Flask
app=Flask(__name__)

#Se establece llave secreta
#Para mensajes flash
app.secret_key="JairClave"

#Semilla para encriptamiento
semilla = bcrypt.gensalt()

#configuracion conexion BD
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='db_solicitudfarmacia4'
mysql.init_app(app)





@app.route('/')
def home():
    return render_template('home.html')

@app.route('/somos')
def somos():
    return render_template('somos.html')


#Define la ruta ingresar
@app.route('/ingresar')
def principal():
    #nombre uno de los datos de la sesion
    #si nombre esta en la lista de sesiones
    if 'nombre' in session:
        #si esta logiado carga inicio
        tipo=session['tipo']
        menu = metodos.definirMenu(tipo) 
        return render_template('inicio.html',menus=menu)
    else:
        #si no esta logiado carga ingresar
        return render_template('ingresar.html')

@app.route('/registrarPersonal')
def registrarPersonal():
    if 'nombre' in session:
        #si esta logiado carga inicio
        tipo=session['tipo']
        menu = metodos.definirMenu(tipo) 
        return render_template('registrar.html',menus=menu)
    else:
        #si no esta logiado carga ingresar
        return render_template('ingresar.html')

#ruta de inicio
@app.route('/inicio')
def inicio():
    #verificar que hay sesion 
    if 'nombre' in session:
        #Carga template main.html
        tipo=session['tipo']
        menu = metodos.definirMenu(tipo)            
        return render_template('inicio.html',menus=menu)
    else:
        #carga template ingresar
        return render_template('ingresar.html')

#Define la ruta de registro 
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    #Si se envia el metodo registrar por GET
    #Si ya esta logiado mandarle al inicio.html
    if(request.method=="GET"):
        #verificar que hay sesion
        if 'nombre' in session:
            #carga template main
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)
            return render_template('inicio.html',menus=menu)
        else:
            #Acceso no concedido
            return render_template("ingresar.html")
    else:
        #si no realiza con el metodo GET 
        #lo realiza con el metodo POST

        #obtiene los datos 
        nombre=request.form['nmNombreRegistro']
        correo=request.form['nmCorreoRegistro']
        password=request.form['nmPasswordRegistro']
        ciudad=request.form['nmCiudadRegistro']
        cedula=request.form['nmCedulaRegistro']
        tipo=request.form['nmTipoRegistro']
        historial_clinico=request.form['nmHistorialClinico']
        password_encode=password.encode("utf-8")
        password_encriptado=bcrypt.hashpw(password_encode, semilla)
        
        #ver si el usuario ya esta registrado
        sql = "SELECT usuario.CORREO FROM usuario WHERE usuario.CORREO=%s;"
        datos = (correo)
        conn= mysql.connect()
        cursor= conn.cursor()
        #la sentencia con los datos
        cursor.execute(sql,datos)
        #terminar la conexion
        fila=cursor.fetchall()
        conn.commit()    
        conn.close()
        #si fila es mayor a 0 es porque existe el correo
        if len(fila)>0:
            flash('Ya existe el correo registrado',"alert-danger")    
            #Redirige a Ingresar
            return render_template('ingresar.html')
        
        #utilizar para hacer una sentencia sql
        #porciento s, se agregara despues esos datos
        sql = "INSERT INTO usuario(usuario.CORREO,usuario.CEDULA_RUC,usuario.NOMBRE_USUARIO,usuario.CLAVE_USUARIO,usuario.ID_TIPO,usuario.CIUDAD) "
        sql+= "VALUES(%s,%s,%s,%s,%s,%s);"
        #son los datos que se van a ingresar
        datos = (correo,cedula,nombre,password_encriptado,tipo,ciudad)
        #print(sql)
        conn= mysql.connect()
        cursor= conn.cursor()
        #la sentencia con los datos
        cursor.execute(sql,datos)

        #insertar en Tabla historial clinico
        sql = "INSERT INTO HISTORIAL_CLINICO(HISTORIAL_CLINICO.CORREO, HISTORIAL_CLINICO.HISTORIAL_CLINICO) VALUES(%s,%s);"
        datos=(correo,historial_clinico)
        cursor.execute(sql,datos)

        #terminar la conexion
        conn.commit()    
        conn.close()
        flash('Su registro fue exitoso, puede ingresar al sistema',"alert-success")    
        #Redirige a Ingresar
        return render_template('ingresar.html')
        

#Definir ruta para ingresar 
@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    if (request.method=="GET"):
        try:
            if 'nombre' in session:
                #Carga template main.html
                tipo=session['tipo']
                menu = metodos.definirMenu(tipo)
                return render_template('inicio.html',menus=menu)
            else:
                #Acceso no concebido
                return render_template("ingresar.html")
        except Exception as e:
            return render_template("ingresar.html")
    else:
        try:
            #Obtiene los datos
            correo=request.form['nmCorreoLogin']
            password=request.form['nmPasswordLogin']
            #print(correo)
            #print(password)
            password_encode=password.encode("utf-8")

            #preparar el query para inserccion 
            sql = "SELECT correo,clave_usuario,nombre_usuario,id_tipo FROM usuario WHERE correo=%s;"
            
            #crear cursor para ejecucion
            conn= mysql.connect()
            cursor= conn.cursor()
            #ejecuta la sentencia
            cursor.execute(sql,(correo))
            #Obtengo el dato 
            usuario = cursor.fetchone()
            #print(usuario)
            #ejecuta el commit
            conn.commit()
            conn.close()

            #Verificar si la consulta a la BD se obtuvo
            #Ver si usuario es distinto de None
            if (usuario != None):
                #Obtiene el password encriptado encode
                password_encriptado_encode = usuario[1].encode()

                #verifica el password
                if(bcrypt.checkpw(password_encode,password_encriptado_encode)):

                    #registra la sesion
                    session['nombre']=usuario[2]
                    session['correo']=correo
                    tipo = usuario[3]

                    session['tipo']=tipo
                    menu = metodos.definirMenu(tipo)
                    #print(session['nombre'])
                    #print(escape(session['correo']))
                    #Redirige al metodo inicio
                    return render_template('inicio.html',menus=menu)
                else:
                    #Mensaje Flash
                    flash("El password no es correcto","alert-warning")

                    #Redirige a Ingresar
                    return render_template('ingresar.html')
            
            else:
                print('El usuario no existe')
                #Mensaje Flash
                flash("El correo no existe","alert-warning")

                #Redirige a ingresar 
                return render_template('ingresar.html')
        
        except Exception as e:
            return render_template('ingresar.html')

#Definir la ruta salir
#Se utiliza para cerrar sesion
# Se limpia la sesion  
@app.route('/salir')
def salir():
    #limpia un argumento de la sesion 
    #Se pone session.pop('nombreVariable',None)
    #None, es para que si no encuentra el nombreVariable
    #no de error 
    session.pop('nombre',None)
    #limpia la sesion 
    session.clear()

    #Manda a ingresar
    return redirect(url_for('ingresar'))


############GESTION USUARIOS

@app.route('/gestionUsuario')
def index():

    try:
       tipo = session['tipo']
       if tipo==1:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            #al momento de ingresar en esta pagina se ingresa esta sentencia sql
            #utilizar para hacer una sentencia sql
            sql = "SELECT usuario.CORREO, usuario.CEDULA_RUC, usuario.NOMBRE_USUARIO, usuario.CIUDAD, tipo_usuario.NOMBRE_TIPO "
            sql+= "FROM usuario, tipo_usuario WHERE usuario.ID_TIPO=tipo_usuario.ID_TIPO;"
            conn= mysql.connect()
            cursor= conn.cursor()
            cursor.execute(sql)
            
            #recuperar la informacion
            empleados = cursor.fetchall()
            #terminar la conexion
            conn.commit()
            conn.close()
            #se envia informacion de empleados
            return render_template('empleados/index.html', empleados=empleados, menus=menu)
            
       else:
            #Acceso no concebido
            return render_template("ingresar.html")
    except Exception as e:
        print(e)
        return render_template("ingresar.html")


    


@app.route('/buscarEmpleado', methods=['POST'])
def buscarEmpleado():
    empleados=[]
    try:
        tipo = session['tipo']
        if tipo==1:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            #recoger los datos
            _nombre=request.form['txtNombre']
            
            #utilizar para hacer una sentencia sql
            #porciento s, se agregara despues esos datos
            sql = "SELECT usuario.CORREO, usuario.CEDULA_RUC, usuario.NOMBRE_USUARIO, usuario.CIUDAD, tipo_usuario.NOMBRE_TIPO "
            sql+= " FROM usuario, tipo_usuario WHERE "
            sql+= "(usuario.NOMBRE_USUARIO LIKE '"+ str(_nombre) +"' OR "
            sql+= "usuario.NOMBRE_USUARIO LIKE '"+ str(_nombre) +" %' OR "
            sql+= "usuario.NOMBRE_USUARIO LIKE '% "+ str(_nombre) +" %' OR "
            sql+= "usuario.NOMBRE_USUARIO LIKE '% "+ str(_nombre) +"' )"
            sql+= "AND usuario.ID_TIPO=tipo_usuario.ID_TIPO;"
            conn= mysql.connect()
            cursor= conn.cursor()
            #la sentencia con los datos
            cursor.execute(sql)
            empleados=cursor.fetchall()
            print(empleados)
            #terminar la conexion
            conn.commit()   
            conn.close()
            if(len(empleados)>0):
                return render_template('empleados/index.html', empleados=empleados,menus=menu)
            else:
                flash('No se encontraron resultados')
                return redirect(url_for('index'))   
        else:
            #Acceso no concebido
            return render_template("ingresar.html")
         
    except Exception as e:
        flash('Ocurrió un problema al buscar')
        return redirect(url_for('index'))
    

@app.route('/destroy/<correo>')
def destroy(correo):
    try:
        conn = mysql.connect()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE correo=%s",(correo))
        conn.commit()
        conn.close()
        flash('El usuario '+str(correo)+' ha sido eliminado')
    except:
        flash('Error al eliminar usuario')
        return redirect(url_for('index'))
    
    #redireccionar a la url de donde vino 
    return redirect(url_for('index'))

@app.route('/edit/<correo>')
def edit(correo):
    try:
        tipo = session['tipo']
        if tipo==1:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            sql="SELECT * FROM usuario WHERE usuario.CORREO=%s"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql,(correo))
            empleados = cursor.fetchall()
            print(empleados)
            conn.commit()
            conn.close()
            return render_template('empleados/edit.html',empleados=empleados,menus=menu)
        else:
            #Acceso no concebido
            return render_template("ingresar.html")
        
    except Exception as e:
        flash('Se ha producido un error inténtelo de nuevo')
        return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    try:
        #recoger los datos
        _nombre=request.form['txtNombre']
        _correo=request.form['txtCorreo']
        _cedula=request.form['txtCedula']
        _ciudad=request.form['txtCiudad']
        
        #utilizar para hacer una sentencia sql
        #porciento s, se agregara despues esos datos
        sql = "UPDATE usuario SET usuario.NOMBRE_USUARIO=%s,usuario.CEDULA_RUC=%s,usuario.CIUDAD=%s WHERE usuario.CORREO=%s;"
        #son los datos que se van a ingresar
        datos = (_nombre,_cedula,_ciudad,_correo)
        conn= mysql.connect()
        cursor= conn.cursor()
        #la sentencia con los datos
        cursor.execute(sql,datos)
        #terminar la conexion
        conn.commit()   
        conn.close() 
    except Exception as e:
        flash('Ocurrió un problema al actualizar el usuario')
        return redirect(url_for('index'))
    
    flash('El usuario se ha actualizado con éxito')
    return redirect(url_for('index'))

##CREAR EMPLEADO
@app.route('/create')
def create(): 
    try:
       tipo = session['tipo']
       if tipo==1:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            return render_template('empleados/create.html',menus=menu)
       else:
            #Acceso no concebido
            return render_template("ingresar.html")
    except Exception as e:
        print(e)
        return render_template("ingresar.html")

    

@app.route('/store', methods=['POST'])
def storage():
    try:
        _nombre=request.form['txtNombre']
        _correo=request.form['txtCorreo']
        _cedula=request.form['txtCedula']
        _ciudad=request.form['txtCiudad']
        _clave=request.form['txtClave']
        _tipoUsuario=int(request.form['txtTipoUsuario'])
        print(type(_tipoUsuario))
        print(_tipoUsuario)
        global semilla
        password_encode=_clave.encode("utf-8")
        password_encriptado=bcrypt.hashpw(password_encode, semilla)

        #Se REALIZA la validacion 
        if _nombre=='' or _correo=='' or _cedula=='' or _ciudad=='' or _clave=='':
            #enviar mns con flash al template
            flash('Recuerda llenar los datos de los campos')
            #si detecta que se ha dejado vacio nombre,etc
            #redirecciona y envia la informacion
            #EL url_for, se le redirecciona al metodo
            return redirect(url_for('create'))

        #ver si el usuario ya esta registrado
        sql = "SELECT usuario.CORREO FROM usuario WHERE usuario.CORREO=%s;"
        datos = (_correo)
        conn= mysql.connect()
        cursor= conn.cursor()
        #la sentencia con los datos
        cursor.execute(sql,datos)
        #terminar la conexion
        fila=cursor.fetchall()
        conn.commit()    
        conn.close()
        #si fila es mayor a 0 es porque existe el correo
        if len(fila)>0:
            flash('Ya existe el correo registrado')
            return redirect(url_for('create'))

        #utilizar para hacer una sentencia sql
        #porciento s, se agregara despues esos datos
        sql = "INSERT INTO usuario(usuario.CORREO,usuario.CEDULA_RUC,usuario.NOMBRE_USUARIO,usuario.CLAVE_USUARIO,usuario.ID_TIPO,usuario.CIUDAD) "
        sql+= "VALUES(%s,%s,%s,%s,%s,%s);"
        #son los datos que se van a ingresar
        datos = ( _correo,_cedula,_nombre,password_encriptado,_tipoUsuario,_ciudad)
        print(sql)
        conn= mysql.connect()
        cursor= conn.cursor()
        #la sentencia con los datos
        cursor.execute(sql,datos)
        #terminar la conexion
        conn.commit()    
        conn.close()
    
    except Exception as e:
        flash('Ocurrió un error, inténtelo de nuevo.')
        return redirect(url_for('create')) 

    flash('El usuario '+str(_correo)+' ha sido registrado')
    return redirect(url_for('index'))


###############Gestion perfil

##cambio de clave

@app.route('/cambiarClave')
def cambiarClave():
    try:
        if 'correo' in session:
            #Carga template main.html
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)
            return render_template('gestionPerfil/cambioClave.html',menus=menu)
        else:
            #Acceso no concebido
            return render_template("ingresar.html")
    except Exception as e:
        return render_template("ingresar.html")


@app.route('/cambiarClavePost', methods=['POST'])
def cambiarClavePost():
    try:

        if 'correo' in session:
            _correo = session['correo']
            
             #recoger los datos
            _pswAntiguo=request.form['pswAntiguo']
            _psw1=request.form['psw']
            _psw2=request.form['psw2']

            password_encode=_pswAntiguo.encode("utf-8")
            

            #preparar el query para inserccion 
            sql = "SELECT clave_usuario FROM usuario WHERE correo=%s;"
            
            #crear cursor para ejecucion
            conn= mysql.connect()
            cursor= conn.cursor()
            #ejecuta la sentencia
            cursor.execute(sql,(_correo))
            #Obtengo el dato 
            usuario = cursor.fetchone()
            #print(usuario)
            #ejecuta el commit
            conn.commit()
            conn.close()

            #Verificar si la consulta a la BD se obtuvo
            #Ver si usuario es distinto de None
            if (usuario != None):
                #Obtiene el password encriptado encode
                password_encriptado_encode = usuario[0].encode()

                #verifica el password
                if(bcrypt.checkpw(password_encode,password_encriptado_encode)):

                    if _psw1!=_psw2:
                        #Mensaje Flash
                        flash("Password nuevo y confirmación no son iguales","alert-warning")
                        #Redirige a Ingresar
                        return redirect(url_for('cambiarClave'))
                    
                    #preparar el query para inserccion 
                    sql = "UPDATE usuario SET clave_usuario=%s WHERE correo=%s;"
                    global semilla
                    password_encode=_psw1.encode("utf-8")
                    password_encriptado=bcrypt.hashpw(password_encode, semilla)
                    #crear cursor para ejecucion
                    conn= mysql.connect()
                    cursor= conn.cursor()
                    #ejecuta la sentencia
                    cursor.execute(sql,(password_encriptado,_correo))
                    #ejecuta el commit
                    conn.commit()
                    conn.close()


                    flash('La contraseña se ha actualizado con éxito',"alert alert-success")
                    return redirect(url_for('inicio'))
                else:
                    #Mensaje Flash
                    flash("El password antiguo no es correcto","alert-warning")

                    #Redirige a Ingresar
                    return redirect(url_for('cambiarClave'))

        else:
            #Acceso no concebido
            return render_template("ingresar.html")
 
       
    except Exception as e:
        flash('Ocurrió un problema al actualizar la contraseña')
        return redirect(url_for('inicio'))
    

@app.route('/editarPerfil')
def editarPerfil():
    try:
        if 'correo' in session:
            correo = session['correo']
            tipo = session['tipo']
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            sql="SELECT CORREO, CEDULA_RUC, NOMBRE_USUARIO, CIUDAD FROM usuario WHERE usuario.CORREO=%s"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql,(correo))
            empleados = cursor.fetchall()
            #print(empleados)
            #si el tipo usuario es cliente->4, se tiene que tener en cuenta el historial clinico
            if session['tipo']!=4:
                conn.commit()
                conn.close()
                return render_template('gestionPerfil/editarPerfil.html',empleados=empleados,menus=menu)
            else:
                sql="SELECT HISTORIAL_CLINICO.HISTORIAL_CLINICO FROM HISTORIAL_CLINICO WHERE HISTORIAL_CLINICO.CORREO=%s"
                cursor.execute(sql,(correo))
                historial_clinico=cursor.fetchone()
                conn.commit()
                conn.close()
                return render_template('gestionPerfil/editarPerfil.html',empleados=empleados,menus=menu, historial_clinico=historial_clinico)
        else:
            #Acceso no concebido
            return render_template("ingresar.html")
        
    except Exception as e:
        flash('Se ha producido un error inténtelo de nuevo','alert-warning')
        return redirect(url_for('inicio'))

@app.route('/editarPerfilPost', methods=['POST'])
def editarPerfilPost():
    try:

        if 'correo' in session:
            #recoger los datos
            _nombre=request.form['txtNombre']
            _correo=request.form['txtCorreo']
            _cedula=request.form['txtCedula']
            _ciudad=request.form['txtCiudad']
            
            #utilizar para hacer una sentencia sql
            #porciento s, se agregara despues esos datos
            sql = "UPDATE usuario SET usuario.NOMBRE_USUARIO=%s,usuario.CEDULA_RUC=%s,usuario.CIUDAD=%s WHERE usuario.CORREO=%s;"
            #son los datos que se van a ingresar
            datos = (_nombre,_cedula,_ciudad,_correo)
            conn= mysql.connect()
            cursor= conn.cursor()
            #la sentencia con los datos
            cursor.execute(sql,datos)
            #terminar la conexion

            #si la session es de cliente se tiene que cambiar la historia clinica
            if session['tipo']==4:
                _historiaClinica = request.form['txtHistorialClinico']
                sql="UPDATE HISTORIAL_CLINICO SET HISTORIAL_CLINICO.HISTORIAL_CLINICO=%s WHERE HISTORIAL_CLINICO.CORREO=%s;"
                datos=(_historiaClinica,_correo)
                cursor.execute(sql,datos)

            conn.commit()   
            conn.close() 

            #cambiar el nombre en la session
            session['nombre']=_nombre

            flash('Sus datos se han actualizado con éxito','alert alert-success')
            return redirect(url_for('inicio'))
        else:
            #Acceso no concebido
            return render_template("ingresar.html")
    except Exception as e:
        flash('Ocurrió un problema al actualizar sus datos','alert-warning')
        return redirect(url_for('inicio'))
    
    


#################GESTION SOLICITUDES 

##realizar solicitudes
@app.route('/realizarSolicitud')
def realizarSolicitud():
    try:
        tipo = session['tipo']
        if tipo == 2:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT producto.COD_PRODUCTO, producto.NOMBRE_PRODUCTO, producto.STOCK, tipo_producto.ID_TIPO_PRODUCTO FROM producto, tipo_producto WHERE producto.COD_PRODUCTO=tipo_producto.COD_PRODUCTO;"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            medicamentos = cursor.fetchall()
            #print(medicamentos)
            conn.commit()
            conn.close()

            return render_template('gestionSolicitudes/realizarSolicitud.html',menus=menu, medicamentos=medicamentos)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        return redirect(url_for('inicio'))


#buscar por el tipo_producto de medicamento
@app.route('/buscarMedicamento/<tipo_producto>')
def medicamentosPorId(tipo_producto):
    try:
        tipo = session['tipo']
        if tipo == 2:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT producto.COD_PRODUCTO, producto.NOMBRE_PRODUCTO, producto.STOCK, tipo_producto.ID_TIPO_PRODUCTO FROM producto, tipo_producto WHERE producto.COD_PRODUCTO=tipo_producto.COD_PRODUCTO"
            sql+=" AND tipo_producto.ID_TIPO_PRODUCTO="+str(tipo_producto)+";"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            medicamentos = cursor.fetchall()
            #print(medicamentos)
            conn.commit()
            conn.close()
            return render_template('gestionSolicitudes/realizarSolicitud.html',menus=menu, medicamentos=medicamentos)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        return redirect(url_for('inicio'))


@app.route('/buscarMedicamentoNombre', methods=['POST'])
def buscarMedicamentoNombre():
    medicamentos=[]
    try:
        tipo = session['tipo']
        if tipo==2:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            #recoger los datos
            _nombre=request.form['txtNombre']
            
            #utilizar para hacer una sentencia sql
            #porciento s, se agregara despues esos datos
            sql = "SELECT producto.COD_PRODUCTO, producto.NOMBRE_PRODUCTO, producto.STOCK, tipo_producto.ID_TIPO_PRODUCTO "
            sql+= " FROM producto, tipo_producto WHERE "
            sql+= "(producto.NOMBRE_PRODUCTO LIKE '"+ str(_nombre) +"' OR "
            sql+= "producto.NOMBRE_PRODUCTO LIKE '"+ str(_nombre) +" %' OR "
            sql+= "producto.NOMBRE_PRODUCTO LIKE '% "+ str(_nombre) +" %' OR "
            sql+= "producto.NOMBRE_PRODUCTO LIKE '% "+ str(_nombre) +"' )"
            sql+= "AND producto.COD_PRODUCTO=tipo_producto.COD_PRODUCTO;"
            conn= mysql.connect()
            cursor= conn.cursor()
            #la sentencia con los datos
            cursor.execute(sql)
            medicamentos=cursor.fetchall()
            #print(medicamentos)
            #terminar la conexion
            conn.commit()   
            conn.close()
            if(len(medicamentos)>0):
                return render_template('gestionSolicitudes/realizarSolicitud.html',menus=menu, medicamentos=medicamentos)
            else:
                flash('No se encontraron resultados','alert-warning')
                return redirect(url_for('realizarSolicitud'))   
        else:
            #Acceso no concebido
            return render_template("ingresar.html")
         
    except Exception as e:
        flash('Ocurrió un problema al buscar','alert-warning')
        return redirect(url_for('realizarSolicitud'))

@app.route('/addMedicamentoLista', methods=['POST'])
def addMedicamentoLista():
    global session 
    try:
        tipo = session['tipo']
        if tipo==2: 
            _cantidad = int(request.form['txtCantidad'])
            _codigo = request.form['codeMedicamento']

            sql = "SELECT producto.STOCK, producto.NOMBRE_PRODUCTO FROM producto WHERE producto.COD_PRODUCTO='"+str(_codigo)+"';"
            conn= mysql.connect()
            cursor= conn.cursor()
            #la sentencia con los datos
            cursor.execute(sql)
            medicamento=cursor.fetchone()
            stock = medicamento[0]
            #print(medicamentos)
            #terminar la conexion
            conn.commit()   
            conn.close()
            
            #modificar session
            session.modified=True

            if _cantidad<=0:
                flash('Cantidad tiene que ser mayor a 0','alert-danger')
                return redirect(url_for('realizarSolicitud'))
            elif(_cantidad>stock):
                flash('No hay el stock suficiente','alert-danger')
                return redirect(url_for('realizarSolicitud'))
            else:
                #print('LLEGAMOS')
                #se guarda codigo_producto:[nombre, cantidad deseada]
                item_Array = {_codigo:[medicamento[1],_cantidad ]}
                #print('ITEM ARRAY')
                #print(item_Array)
                #print('\n\n')

                if 'listaMedicamentos' in session:
                    lista = session['listaMedicamentos']
                    lista[_codigo]=[medicamento[1],_cantidad ]
                    session['listaMedicamentos']=lista
                    #print(lista)
                else:
                    session['listaMedicamentos'] = item_Array
                    #print(session['listaMedicamentos'])
            flash('Ítem agregado al recetario','alert-success')
            return redirect(url_for('realizarSolicitud'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al agregar el producto','alert-warning')
        return redirect(url_for('realizarSolicitud'))



@app.route('/eliminarMedicamentoLista/<_codigo>')
def eliminarMedicamentoLista(_codigo):
    global session 
    try:
        tipo = session['tipo']
        if tipo==2: 
            #_codigo = request.form['codigo']
            #print(_codigo)
            #modificar session
            session.modified=True

            if 'listaMedicamentos' in session:
                lista = session['listaMedicamentos']
                #print(lista)
                lista.pop(_codigo)
                #print(lista)
                if lista!={}:
                    session['listaMedicamentos']=lista
                else:
                    session.pop('listaMedicamentos',None)
                #print(lista)
            else:
                flash('No hay ítems seleccionados','alert-danger')
                return redirect(url_for('realizarSolicitud'))

            flash('Ítem eliminado de la lista','alert-success')
            return redirect(url_for('realizarSolicitud'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al eliminar item de la lista','alert-warning')
        return redirect(url_for('realizarSolicitud'))



@app.route('/enviarSolicitud', methods=['POST'])
def enviarSolicitud():
    try:
        tipo = session['tipo']
        if tipo==2:
            
            #recoger los datos
            _historialClinico=request.form['txtHistorialClinico']
            _nombreDoctor=request.form['txtNombreDoctor']
            #print(_historialClinico)
            #print(_nombreDoctor)

            session.modified=True

            if 'listaMedicamentos' in session:
                lista = session['listaMedicamentos']               
                if lista!={}:
                    print(lista)

                    #creando conexion con BD
                    conn= mysql.connect()
                    cursor= conn.cursor()

                    #insertando en cabecera solicitud
                    sql="INSERT INTO solicitud(solicitud.HISTORIAL_CLINICO, solicitud.NOMBRE_DOCTOR, solicitud.CORREO, solicitud.ID_ESTADO_SOLICITUD)"
                    sql+=" VALUES(%s,%s,%s,%s);"
                    #estado solicitud 1->Solicitud enviada a farmacia
                    correo=session['correo']
                    valores=(_historialClinico,_nombreDoctor,correo,"1")
                    cursor.execute(sql,valores)

                    #escoger el id agregado
                    sql="SELECT solicitud.ID_SOLICITUD FROM solicitud " 
                    sql+="WHERE solicitud.CORREO=%s AND solicitud.HISTORIAL_CLINICO=%s " 
                    sql+="AND solicitud.NOMBRE_DOCTOR=%s AND solicitud.ID_ESTADO_SOLICITUD=%s "
                    sql+="ORDER BY solicitud.ID_SOLICITUD DESC LIMIT 1;"
                    valores=(correo,_historialClinico,_nombreDoctor,"1")
                    cursor.execute(sql,valores)
                    _idSolicitud=cursor.fetchone()[0]
                    #print(_idSolicitud)

                    #agregar en detalle solicitud los medicamentos del recetario
                    for codigo_med in lista:
                        cantidad = lista[codigo_med][1]
                        sql="INSERT INTO detalle_solicitud(detalle_solicitud.COD_PRODUCTO,detalle_solicitud.CANTIDAD,detalle_solicitud.ID_SOLICITUD) "
                        sql+="VALUES(%s,%s,%s);"
                        valores=(codigo_med,cantidad,_idSolicitud)
                        cursor.execute(sql,valores)
                    
                    #cerrar conexion
                    conn.commit()
                    conn.close()

                    session.pop('listaMedicamentos',None)
                    flash('Se ha enviado con éxito la solicitud','alert-dark')
                    return redirect(url_for('realizarSolicitud'))  
                else:
                    flash('No hay ítems seleccionados','alert-danger')
                    return redirect(url_for('realizarSolicitud'))
                    
                #print(lista)
            else:
                flash('No hay ítems seleccionados','alert-danger')
                return redirect(url_for('realizarSolicitud'))


            
            #sql = "SELECT producto.COD_PRODUCTO, producto.NOMBRE_PRODUCTO, producto.STOCK, tipo_producto.ID_TIPO_PRODUCTO "
            conn= mysql.connect()
            cursor= conn.cursor()
            #la sentencia con los datos
            #cursor.execute(sql)
            #medicamentos=cursor.fetchall()
            #print(medicamentos)
            #terminar la conexion
            conn.commit()   
            conn.close()
             

        else:
            #Acceso no concebido
            return render_template("ingresar.html")
         
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al enviar la solicitud','alert-danger')
        return redirect(url_for('realizarSolicitud'))


#ver lista de solicitudes pendientes
##realizar solicitudes
@app.route('/verListaSolicitudes')
def verListaSolicitudes():
    try:
        tipo = session['tipo']
        if tipo == 2:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT solicitud.ID_SOLICITUD, solicitud.HISTORIAL_CLINICO, solicitud.ID_ESTADO_SOLICITUD FROM solicitud "
            sql+="WHERE (solicitud.ID_ESTADO_SOLICITUD='1' OR solicitud.ID_ESTADO_SOLICITUD='2') AND solicitud.CORREO='"+str(session['correo'])+"' "
            sql+="ORDER by solicitud.ID_ESTADO_SOLICITUD DESC, solicitud.ID_SOLICITUD ASC;"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            peticiones = cursor.fetchall()
            #print(medicamentos)
            conn.commit()
            conn.close()

            return render_template('gestionSolicitudes/listaSolicitudes.html',menus=menu, peticiones=peticiones)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        return redirect(url_for('inicio'))


#ver peticion individual
@app.route('/verPeticion/<id>')
def verPeticion(id):
    try:
        tipo = session['tipo']
        if tipo == 2:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT solicitud.HISTORIAL_CLINICO, solicitud.NOMBRE_DOCTOR "
            sql+="FROM solicitud WHERE solicitud.ID_SOLICITUD='"+id+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            cabecera_solicitud = cursor.fetchone()
            sql="SELECT producto.NOMBRE_PRODUCTO, detalle_solicitud.CANTIDAD FROM detalle_solicitud, producto "
            sql+="WHERE detalle_solicitud.ID_SOLICITUD='"+id+"' AND detalle_solicitud.COD_PRODUCTO=producto.COD_PRODUCTO;"
            cursor.execute(sql)
            detalle_solicitud=cursor.fetchall()
            #cerrar conexion
            conn.commit()
            conn.close()
            

            return render_template('gestionSolicitudes/verPeticionIndividual.html',menus=menu, id=id, cabecera_solicitud=cabecera_solicitud, detalle_solicitud=detalle_solicitud)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al ver solicitud','alert-danger')
        return redirect(url_for('verListaSolicitudes'))


#ver peticion individual
@app.route('/peticionRetirada/<id>')
def peticionRetirada(id):
    try:
        tipo = session['tipo']
        if tipo == 2:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            #se cambia a estado 3->peticion retirada de farmacia
            sql="UPDATE solicitud SET solicitud.ID_ESTADO_SOLICITUD='3' "
            sql+="WHERE solicitud.ID_SOLICITUD='"+id+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            #cerrar conexion
            conn.commit()
            conn.close()
            mns="Solicitud número: "+str(id)+" ha sido retirada de farmacia con éxito"
            flash(mns,'alert-success')
            return redirect(url_for('verListaSolicitudes'))
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al realizar la acción, inténtelo de nuevo','alert-danger')
        return redirect(url_for('verListaSolicitudes'))


#ver producto con su descripcion y productos semejantes
@app.route('/verProductoMedico/<id>')
def verProductoMedico(id):
    try:
        tipo = session['tipo']
        if tipo == 2:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT producto.NOMBRE_PRODUCTO, producto.DESCRIPCION, tipo_producto.ID_TIPO_PRODUCTO FROM producto, tipo_producto "
            sql+=" WHERE producto.COD_PRODUCTO=tipo_producto.COD_PRODUCTO "
            sql+="AND producto.COD_PRODUCTO='"+str(id)+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            productos = cursor.fetchall()
            producto=[None]
            if(productos):
                producto=productos[0]
            #print(productos)
            #print(producto)

                      
            try:
                sql="SELECT producto.COD_PRODUCTO, producto.NOMBRE_PRODUCTO, producto.DESCRIPCION FROM producto, tipo_producto "
                sql+="WHERE producto.COD_PRODUCTO=tipo_producto.COD_PRODUCTO "
                sql+="AND tipo_producto.ID_TIPO_PRODUCTO=(SELECT tipo_producto.ID_TIPO_PRODUCTO FROM tipo_producto "
                sql+="WHERE tipo_producto.COD_PRODUCTO='"+str(id)+"' LIMIT 1) "
                sql+="AND NOT producto.COD_PRODUCTO='"+str(id)+"';"
                #print(sql)
                cursor.execute(sql)
                detalle_solicitud=cursor.fetchall()
            except Exception as e:
                print(e)

            #cerrar conexion
            conn.commit()
            conn.close()
            

            return render_template('gestionSolicitudes/verMedicamento.html',menus=menu, producto=producto, medicamentos=detalle_solicitud)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al ver solicitud','alert-danger')
        return redirect(url_for('realizarSolicitud'))




################Parte farmaceutico
#Ver solicitudes por registrar
@app.route('/peticionesRegistrar')
def peticionesRegistrar():
    try:
        tipo = session['tipo']
        if tipo == 3:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT solicitud.ID_SOLICITUD, solicitud.HISTORIAL_CLINICO, solicitud.ID_ESTADO_SOLICITUD FROM solicitud "
            sql+="WHERE (solicitud.ID_ESTADO_SOLICITUD='1') "
            sql+="ORDER by solicitud.ID_SOLICITUD ASC;"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            peticiones = cursor.fetchall()
            #print(medicamentos)
            conn.commit()
            conn.close()

            return render_template('gestionFarmacia/peticionesPorRegistrar.html',menus=menu, peticiones=peticiones)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        return redirect(url_for('inicio'))



#peticiones para entregar
@app.route('/peticionesEntregar')
def peticionesEntregar():
    try:
        tipo = session['tipo']
        if tipo == 3:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT solicitud.ID_SOLICITUD, solicitud.HISTORIAL_CLINICO, solicitud.ID_ESTADO_SOLICITUD, usuario.NOMBRE_USUARIO FROM solicitud, usuario "
            sql+="WHERE solicitud.ID_ESTADO_SOLICITUD='2' AND solicitud.CORREO=usuario.CORREO "
            sql+="ORDER by solicitud.ID_SOLICITUD ASC;"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            peticiones = cursor.fetchall()
            #print(medicamentos)
            conn.commit()
            conn.close()

            return render_template('gestionFarmacia/peticionesPorEntregar.html',menus=menu, peticiones=peticiones)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        return redirect(url_for('inicio'))


#ver peticion individual en farmacia
@app.route('/verPeticionF/<id>')
def verPeticionF(id):
    try:
        tipo = session['tipo']
        if tipo == 3:
            #tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            #traer datos de los productos existentes
            sql="SELECT solicitud.HISTORIAL_CLINICO, solicitud.NOMBRE_DOCTOR, usuario.NOMBRE_USUARIO, solicitud.ID_ESTADO_SOLICITUD "
            sql+="FROM solicitud, usuario WHERE usuario.CORREO=solicitud.CORREO AND " 
            sql+="solicitud.ID_SOLICITUD='"+id+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            cabecera_solicitud = cursor.fetchone()
            sql="SELECT producto.NOMBRE_PRODUCTO, detalle_solicitud.CANTIDAD, producto.COD_PRODUCTO FROM detalle_solicitud, producto "
            sql+="WHERE detalle_solicitud.ID_SOLICITUD='"+id+"' AND detalle_solicitud.COD_PRODUCTO=producto.COD_PRODUCTO;"
            cursor.execute(sql)
            detalle_solicitud=cursor.fetchall()
            #cerrar conexion
            conn.commit()
            conn.close()
            

            return render_template('gestionFarmacia/verPeticionF.html',menus=menu, id=id, cabecera_solicitud=cabecera_solicitud, detalle_solicitud=detalle_solicitud)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al ver solicitud','alert-danger')
        return redirect(url_for('inicio'))


#cambiar estado solicitud de 1 a 2 
@app.route('/cambiarEstadoSolicitud_2', methods=['POST'])
def cambiarEstadoSolicitud_2():
    medicamentos=[]
    try:
        tipo = session['tipo']
        if tipo==3:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            #recoger los datos
            _idSolicitud=request.form['txtIdSolicitud']
            
            #utilizar para hacer una sentencia sql
            #porciento s, se agregara despues esos datos
            sql="UPDATE solicitud SET solicitud.ID_ESTADO_SOLICITUD='2' "
            sql+="WHERE solicitud.ID_SOLICITUD='"+_idSolicitud+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            #cerrar conexion
            conn.commit()
            conn.close()
            mns="Solicitud número: "+str(_idSolicitud)+" ha sido registrada, lista para retirar"
            flash(mns,'alert-success')
            return redirect(url_for('peticionesRegistrar'))
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al realizar la acción, inténtelo de nuevo','alert-danger')
        return redirect(url_for('peticionesRegistrar'))


###############GESTION CLIENTE

#ver lista de recetas 
#peticiones para entregar
@app.route('/listaRecetas')
def listaRecetas():
    try:
        tipo = session['tipo']
        if tipo == 4:
            tipo=session['tipo']
            menu = metodos.definirMenu(tipo)

            conn = mysql.connect()
            cursor = conn.cursor()

            #encontrar historial clinico
            sql = "SELECT HISTORIAL_CLINICO.HISTORIAL_CLINICO FROM HISTORIAL_CLINICO "
            sql+= "WHERE HISTORIAL_CLINICO.CORREO='"+session['correo']+"';"
            cursor.execute(sql)
            historial_cli = cursor.fetchone()[0]

            #encontrar lista de recetarios medicos
            sql="SELECT solicitud.ID_SOLICITUD, solicitud.NOMBRE_DOCTOR, usuario.NOMBRE_USUARIO " 
            sql+="FROM usuario, HISTORIAL_CLINICO, solicitud "
            sql+="WHERE historial_clinico.HISTORIAL_CLINICO=solicitud.HISTORIAL_CLINICO AND usuario.CORREO=solicitud.CORREO "
            sql+="AND solicitud.ID_ESTADO_SOLICITUD='3' " 
            sql+="AND historial_clinico.HISTORIAL_CLINICO=%s AND HISTORIAL_CLINICO.CORREO=%s "
            sql+="ORDER by solicitud.ID_SOLICITUD ASC;"
            cursor.execute(sql,(historial_cli,session['correo']))
            peticiones = cursor.fetchall()

            conn.commit()
            conn.close()

            return render_template('gestionCliente/listaRecetas.html',menus=menu, peticiones=peticiones)
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        return redirect(url_for('inicio'))



#ver solicitud individual
@app.route('/verRecetaIndividual', methods=['POST'])
def verRecetaIndividual():
    try:
        tipo = session['tipo']
        if tipo==4:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            #recoger los datos
            id=request.form['txtIdSolicitud']
            
            
            #traer datos de los productos existentes
            sql="SELECT solicitud.HISTORIAL_CLINICO, solicitud.NOMBRE_DOCTOR, usuario.NOMBRE_USUARIO, solicitud.ID_ESTADO_SOLICITUD "
            sql+="FROM solicitud, usuario WHERE usuario.CORREO=solicitud.CORREO AND " 
            sql+="solicitud.ID_SOLICITUD='"+id+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            cabecera_solicitud = cursor.fetchone()

            
            sql="SELECT producto.NOMBRE_PRODUCTO, detalle_solicitud.CANTIDAD, producto.COD_PRODUCTO FROM detalle_solicitud, producto "
            sql+="WHERE detalle_solicitud.ID_SOLICITUD='"+id+"' AND detalle_solicitud.COD_PRODUCTO=producto.COD_PRODUCTO;"
            cursor.execute(sql)
            detalle_solicitud=cursor.fetchall()
            #cerrar conexion
            conn.commit()
            conn.close()
            

            return render_template('gestionCliente/recetaIndividual.html',menus=menu, id=id, cabecera_solicitud=cabecera_solicitud, detalle_solicitud=detalle_solicitud)

            
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al realizar la acción, inténtelo de nuevo','alert-danger')
        return redirect(url_for('listaRecetas'))



#############PDF
import pdfkit

@app.route('/pdf1')
def pdf1():
    try:
        tipo = session['tipo']
        if tipo==4:
            #Carga template main.html
            menu = metodos.definirMenu(tipo)
            #recoger los datos
            id=request.form['txtIdSolicitud']
            
            
            #traer datos de los productos existentes
            sql="SELECT solicitud.HISTORIAL_CLINICO, solicitud.NOMBRE_DOCTOR, usuario.NOMBRE_USUARIO, solicitud.ID_ESTADO_SOLICITUD "
            sql+="FROM solicitud, usuario WHERE usuario.CORREO=solicitud.CORREO AND " 
            sql+="solicitud.ID_SOLICITUD='"+id+"';"
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            cabecera_solicitud = cursor.fetchone()

            
            sql="SELECT producto.NOMBRE_PRODUCTO, detalle_solicitud.CANTIDAD, producto.COD_PRODUCTO FROM detalle_solicitud, producto "
            sql+="WHERE detalle_solicitud.ID_SOLICITUD='"+id+"' AND detalle_solicitud.COD_PRODUCTO=producto.COD_PRODUCTO;"
            cursor.execute(sql)
            detalle_solicitud=cursor.fetchall()
            #cerrar conexion
            conn.commit()
            conn.close()
            

            html = render_template('gestionCliente/recetaIndividual.html',menus=menu, id=id, cabecera_solicitud=cabecera_solicitud, detalle_solicitud=detalle_solicitud)
            pdf = pdfkit.from_string(html, False)
            response = make_response(pdf)
            response.headers["Content-Type"] = "application/pd"
            response.headers["Content-Disposition"] = "inline; filename=output.pdf"
            return response
            
        else:
            return redirect(url_for('inicio'))
    except Exception as e:
        print(e)
        flash('Ocurrió un problema al descargar inténtelo de nuevo','alert-danger')
        return redirect(url_for('listaRecetas'))
    

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)





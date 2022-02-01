##TIPOS DE USUARIO 
#1 Administrador
#2 Enfermer@
#3 Farmaceutic@
#4 Cliente

MENUS = {
        'administrador':[['Registrar Personal','Gestion empleados','Editar Perfil'],
        ['/create','/gestionUsuario','/editarPerfil'],
        'Gestión Administración','Administrador',
        './static/img/fonfoadmin.png'],

        'enfermero':[['Realizar solicitud','Ver Solicitudes','Editar Perfil'],['/realizarSolicitud','/verListaSolicitudes','/editarPerfil'],
        'Gestión Enfermería', 'Enfermer@','./static/img/fondoenfer.png'],
        
        'farmaceutico':[ ['Peticiones por registrar','Peticiones para entregar','Editar Perfil'],['/peticionesRegistrar','/peticionesEntregar','/editarPerfil'],
        'Gestión Farmacia','Farmaceutic@','./static/img/fondofar.jpg' ],
        
        'cliente':[ ['Ver recetas médicas', 'Editar Perfil'],['/listaRecetas','/editarPerfil'],
        'Gestión Paciente','Paciente','./static/img/fonfopaci.jpg' ]
        }

#metodo para definir un menu
#entrada tipo de usuario
#salida items del menu de usuario
def definirMenu(tipo):
    global MENUS
    menu=''
    if tipo==1:
        menu=MENUS['administrador']
    elif tipo==2:
        menu=MENUS['enfermero']
    elif tipo==3:
        menu=MENUS['farmaceutico']
    elif tipo==4:
        menu=MENUS['cliente']
    
    return menu 
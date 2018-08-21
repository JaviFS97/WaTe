from appJar import gui
import server
import api
import secure
import client
import threading

# Constantes.
PLAY  = "\u25B6"
PAUSE = "\u23F8"
RWD   = "\u23EA"
FWD   = "\u23E9"
STOP  = "\u23F9"


# Variable global que contiene informacion necesaria para llevar a cabo la conexion.
# Contiene la informacion de los usuarios con los que tienes un chat activo.
# Un maximo de 3 chat activos al mismo tiempo.
# Cada indice contendra un diccionario llamado user_Info, con los campos:  {"IP": ,"Puerto": ,"Socket": ,"Nombre":}
# SOLO CONTIENE INFORMACION DE LOS LLAMADOS CLIENTS.
users_Info = {'0': 'Null',
              '1': 'Null',
              '2': 'Null'}

# Usuario con el que te logeas.
my_user = 'Null'



##################################################  VENTANA PRINCIPAL   ##################################################

def press_Entrar():
    """
    Si se presiona el boton Entrar de la ventana principal.
    :return: None
    """

    # Recuperamos la informacion del login.
    usuario = app.entry("Usuario")
    contrasenia = app.entry("Contrasenia")

    # Eliminamos el contenido de la entrada.
    app.clearEntry("Usuario", callFunction=False)
    app.clearEntry("Contrasenia", callFunction=False)

    # Recuperamos la informacion del usuario de la BD
    try:
        response_Data = api.get_UserLoginInfo(usuario)
        print(response_Data)
    except:
        print("Error al obtener informacion de loggin.")
        response_Data = {'status_code': "ERROR"}

    # Si el login fue correcto,
    if response_Data["status_code"] == "OK":
        if secure.compareHash(contrasenia, response_Data["Salt"], response_Data["PasswordHash"]):

            # Si el estado de dicho user es 1, quiere decir que hay alguien conectado con su user.
            if response_Data["Estado"] == '1':
                app.infoBox("Ya estas conectado", "Ya estas conectado en otra sesion.\nAlguien esta utilizando tu user.")

            # Si su estado es 0, quiere decir que no hay nadie conectado con su user.
            else:
                # Variable global, donde guardar el nombre con el que te has logueado.
                global my_user
                my_user = usuario
                app.setLabel("Msg1", "Hola de nuevo " + my_user)

                # todo implementar cifrado
                clavePublica = "PorImplementar"

                # Crear hilo que se encargue de lanzar el server para la creacion de un socket que quede a la escucha de clientes.
                server_thread_principal = threading.Thread(target=server.lanzar_server,
                                                           args=(usuario,
                                                                 clavePublica,
                                                                 app)) # Pasamos la app, para poder crear subwindow cuando nos llamen
                server_thread_principal.daemon = True
                server_thread_principal.start()

                # Lanzamos una ventana hija, escondiendo la ventana padre.
                app.hide("Ventana Login")
                app.showSubWindow("Ventana Inicio-Identificado")

        # Si el usuario y/o la contrasenia fueron erroneos.
        else:
            app.errorBox("Error login", "Usuario y/o contraseña erroneo", parent=None)

    # Si hubo error con la obtencion de los datos de la BD.
    else:
        app.errorBox("Error api", "Error con la api o la BD", parent=None)


def press_Registrar():
    """
    Si se presiona el boton Registrar de la pagina principal.
    :return: None.
    """

    usuario = app.entry("Usuario")
    hashPassword = secure.hashingPassword(app.entry("Contrasenia"))

    # Creamos el usuario con su nombre, password hasheada y su salt.
    # Cuando realice el login, se actualizaran los datos IP, Puerto, estadoUser,...
    if api.create_User(usuario, hashPassword):
        app.infoBox("Registrado con exito", "Te registraste como: "+usuario)
    else:
        app.errorBox("Error en el registro", "Hubo un error a la hora de registrarse ")


def app_stop():
    respuesta = app.yesNoBox("Confirma que cierras", "Estas seguro de querer abandonar WaTe?")
    if respuesta:
        return True


###############################################################################################################################


##################################################  VENTANA UNA VEZ LOGUEADO ##################################################
def usuarios_conectados():
    """
    Devuelve una lista con los nombres de los usuarios que estan conectados, esto es, su campo 'Estado' sea 1 == True.
    :return: lista de usuarios conectados.
    """

    global my_user
    print("Actualizando clientes conectados.")
    usuarios = api.get_AllUser()
    lista_usarios = []

    for user in usuarios:
        if user['Estado'] == '1':
            # Anadimos todos los users menos el propio.
            if user['Nombre'] != my_user:
                lista_usarios.append(user['Nombre'])

    if len(lista_usarios) == 0:
        lista_usarios = ['- Vacio -']

    return lista_usarios


def actualizar_usuarios_conectados():
    """
    Se encarga de actualizar el wigdet con los nuevos usuarios conectados.
    Se invoca cuando pasas el raton por encima del wigdet.
    :return:
    """
    app.changeOptionBox("Usuarios conectados: ", usuarios_conectados())


def cerrar_sesion():
    """
    Debe poner al usuario con su 'estado' en desconectado.
    A continuacion, eliminar la subwindow y volver a mostrar la ventana de inicio.
    :return:
    """

    cerrar_sesion = True
    # Antes de cerrar sesion, hay que ver si tiene chats abiertos, si es asi, tendra que cerrarlos antes.
    if tienes_chats_client():
        cerrar_sesion = False
        app.infoBox("Tienes chats activos",
                    "Tienes chat/s client activo/s, cierra/los para poder cerrar sesion")

    if tienes_chats_server():
        cerrar_sesion = False
        app.infoBox("Tienes chats activos",
                    "Tienes chat/s server activo/s, cierra/los para poder cerrar sesion")

    # Si no hay ningun chat abierto, se podra cerrar sesion.
    if cerrar_sesion:
        # Actualizamos los campos del usuario en la BD, entre otros, ponemos el estado del usuario en desconectado.
        api.update_userLogoutInfo(my_user)

        # todo,Tambien parar el socket server que esta a la escucha
        server.parar_server()

        # Escondemos todas las subventanas.
        app.hideAllSubWindows()
        # Mostramos la pantalla de inicio.
        app.show()

def press_Usuario():
    """
    Cuando el usuario escoge un usuario al que llamar de la optionBox.
    Hay que abrir un socket contra el otro usario para iniciar la conversacion.
    Por otro lado, hay que dejar un hilo a la escucha que se encargue de recibir las posibles respuestas del usuario con el que hablamos.
    :return:
    """

    # Devuelve el usuario escogido en la lista de usuarios conectados.
    user_llamar = app.getOptionBox("Usuarios conectados: ")

    # Obtener la informacion de lA BD para iniciar la comunicacion con el.
    user_llamar_info = api.get_IPandPort(user_llamar)
    if user_llamar_info["status_code"] == "OK":
        # Si user conectado.
        if user_llamar_info["Estado"] == '1':
            # Lanzar el cliente y obtener su socket
            client_socket = client.lanzar_cliente(user_llamar_info["IP"],
                                                  user_llamar_info["Puerto"],
                                                  my_user)

            # Creamos diccionario con la informacion relevante del usuario al que hay que llamar.
            user_Info = {"IP": user_llamar_info['IP'],
                         "Puerto": user_llamar_info['Puerto'],
                         "Socket": client_socket,
                         "Nombre": user_llamar}

            # Calculamos la longitud de users_Info, pasa saber en que posicion insertar en la misma.
            long = len(users_Info)

            # Insertamos la informacion en la variable global users_Info, en la pos que este vacia.
            num_ventana = -1
            cuenta = 0
            while cuenta < long:
                if users_Info[str(cuenta)] == "Null":
                    users_Info[str(cuenta)] = user_Info
                    num_ventana = cuenta
                    break

                cuenta += 1

            # Si ya tiene 3 chat abiertos.
            else:
                app.infoBox("Maximo numeros de chats activos", "Ya tienes 3 chats activos.\n Si deseas hablar con otra persona, cierra uno de tus chats activos.")

            # Si se le asigna un numero de ventana, creamos un hilo para recibir los posibles mensajes y mostramos la ventana del chat.
            if (num_ventana >= 0) and (num_ventana < 3):
                # Creamos un hilo que quede a la escucha de posibles mensajes de la persona con la que se habla.
                client_thread_principal = threading.Thread(target=client.recibir_mensaje,
                                                           args=(client_socket,
                                                                 app,
                                                                 num_ventana,
                                                                 users_Info))
                client_thread_principal.daemon = True
                client_thread_principal.start()

                # Mostramos una nueva ventana donde poder llevar a cabo el chat 0, 1 o 2.
                app.showSubWindow("Ventana Inicio-Identificado-Client-"+str(num_ventana))

        # Usuario no conectado.
        else:
            app.errorBox("usuario no conectado", "El usuario no se encuentra conectado en estos momentos")

    else:
        app.errorBox("Error al llamar al usuario", "Hubo un error a la hora de llamar al usuario "+user_llamar)


######################################################################################################################################################


################################################################  VENTANA DE CHAT ####################################################################

    #------------------------------------- Cuando siendo cliente envias un mensaje --------------------------------------------------#

def tienes_chats_client():
    """
    Recorre users_Info para comprobar si hay algun chat cliente activo.
    Si lo hay, devolvera True.
    :return:
    """
    for key in users_Info:
        if users_Info[str(key)] != 'Null':
            return True

    return False

                                                        ##### CLIENTE 0 #####
def send_msg_0():
    """
    Callback que se ejectua cuando introduces una cadena en el entry (ChatEntrada) y presionas el boton <Enter>.
    Del chat 0.
    Siendo cliente.
    :return:
    """

    # Obtenemos el mensaje que se introdujo en la 'Entry'
    msg = app.getEntry("ChatEntrada-Client-0")
    # Enviamos dicho mensaje.
    client.enviar_mensaje(users_Info['0']['Socket'], msg, app, 0)


def terminar_client_chat_0():
    """
    Cuando se presiona el boton de terminar chat.
    Del chat 0.
    :return:
    """

    # Mostramos caja de si o no para ver si de verdad quiere terminar o no.
    respuesta = app.yesNoBox("Terminar conversacion",
                             "Deseas terminar el chat con " + users_Info['0']['Nombre'] + " ?")
    if respuesta:
        # Enviamos el mensaje 'CLOSE'.
        client.enviar_mensaje(users_Info['0']['Socket'], 'CLOSE', app, 0)
        # Colocamos la informacion del user a Null puesto que terminamos el chat.
        users_Info['0'] = "Null"
                                                        ####################


                                                        ##### CLIENTE 1 #####
def send_msg_1():
    """
    Callback que se ejectua cuando introduces una cadena en el entry (ChatEntrada) y presionas el boton <Enter>.
    Del chat 1.
    Siendo cliente.
    :return:
    """

    # Obtenemos el mensaje que se introdujo en la 'Entry'
    msg = app.getEntry("ChatEntrada-Client-1")
    # Enviamos dicho mensaje.
    client.enviar_mensaje(users_Info['1']['Socket'], msg, app, 1)


def terminar_client_chat_1():
    """
    Cuando se presiona el boton de terminar chat.
    Del chat 1.
    :return:
    """

    # Mostramos caja de si o no para ver si de verdad quiere terminar o no.
    respuesta = app.yesNoBox("Terminar conversacion",
                             "Deseas terminar el chat con " + users_Info['1']['Nombre'] + " ?")
    if respuesta:
        # Enviamos el mensaje 'CLOSE'.
        client.enviar_mensaje(users_Info['1']['Socket'], 'CLOSE', app, 1)
        # Colocamos la informacion del user a Null puesto que terminamos el chat.
        users_Info['1'] = "Null"
                                                        ####################


                                                        ##### CLIENTE 2 #####
def send_msg_2():
    """
    Callback que se ejectua cuando introduces una cadena en el entry (ChatEntrada) y presionas el boton <Enter>.
    Del chat 2.
    Siendo cliente.
    :return:
    """

    # Obtenemos el mensaje que se introdujo en la 'Entry'
    msg = app.getEntry("ChatEntrada-Client-2")
    # Enviamos dicho mensaje.
    client.enviar_mensaje(users_Info['2']['Socket'], msg, app, 2)


def terminar_client_chat_2():
    """
    Cuando se presiona el boton de terminar chat.
    Del chat 2.
    :return:
    """

    # Mostramos caja de si o no para ver si de verdad quiere terminar o no.
    respuesta = app.yesNoBox("Terminar conversacion",
                             "Deseas terminar el chat con " + users_Info['2']['Nombre'] + " ?")
    if respuesta:
        # Enviamos el mensaje 'CLOSE'.
        client.enviar_mensaje(users_Info['2']['Socket'], 'CLOSE', app, 2)
        # Colocamos la informacion del user a Null puesto que terminamos el chat.
        users_Info['2'] = "Null"
                                                        ####################

#------------------------------------- Cuando siendo server envias un mensaje --------------------------------------------------#
                                                        ##### SERVER 0 #####

def tienes_chats_server():
    """
    Recorre users_Info del modulo server.py para comprobar si hay algun chat server activo.
    Si lo hay, devolvera True.
    :return:
    """

    return server.tienes_chats_server()


def send_msg_server_0():
    """
    Callback que se ejectua cuando introduces una cadena en el entry (ChatEntrada) y presionas el boton <Enter>.
    Del chat 0.
    Siendo server.
    :return:
    """

    # Obtenemos el mensaje que se introdujo en la 'Entry'
    msg = app.getEntry("ChatEntrada-Server-0")
    # Enviamos dicho mensaje.
    server.enviar_mensaje(msg, app, 0)


def terminar_server_chat_0():

    server.enviar_mensaje('CLOSE', app, 0)


                                                        ####################
                                                        ##### SERVER 1 #####


def send_msg_server_1():
    """
    Callback que se ejectua cuando introduces una cadena en el entry (ChatEntrada) y presionas el boton <Enter>.
    Del chat 1.
    Siendo server.
    :return:
    """

    # Obtenemos el mensaje que se introdujo en la 'Entry'
    msg = app.getEntry("ChatEntrada-Server-1")
    # Enviamos dicho mensaje.
    server.enviar_mensaje(msg, app, 1)


def terminar_server_chat_1():

    server.enviar_mensaje('CLOSE', app, 1)


                                                        ####################
                                                        ##### SERVER 2 #####


def send_msg_server_2():
    """
    Callback que se ejectua cuando introduces una cadena en el entry (ChatEntrada) y presionas el boton <Enter>.
    Del chat 2.
    Siendo server.
    :return:
    """

    # Obtenemos el mensaje que se introdujo en la 'Entry'
    msg = app.getEntry("ChatEntrada-Server-2")
    # Enviamos dicho mensaje.
    server.enviar_mensaje(msg, app, 2)


def terminar_server_chat_2():

    server.enviar_mensaje('CLOSE', app, 2)

                                                            ####################

######################################################################################################################################################





##################################################################  ------  GUI  ------  ############################################################

#----------------------------------------------------- VENTANA CUANDO EJECUTAS LA APP ----------------------------------------------------------#
with gui("Ventana Inicio", "800x600", bg='orange', font={'size': 12}) as app:
    app.label("Bienvenido a WaTe", bg='blue', fg='orange')
    app.image("Imagen inicio", "../Images/whatsapptelegram.gif")
    app.entry("Usuario", label=True, focus=True)
    app.entry("Contrasenia", label=True, secret=True)
    app.buttons(["Entrar", "Registrarse", "Salir"], [press_Entrar, press_Registrar,  app.stop])
    app.setStopFunction(app_stop)



    #---------------------------------------------------- VENTANA CUANDO LOGUEADO CON EXITO  -----------------------------------------------------#
    with app.subWindow("Ventana Inicio-Identificado", size="550x600", bg='orange'):
        app.label("Msg0", "Pagina inicio.", fg='blue', bg='orange', font={'size': 15})
        app.label("Msg1", " ", fg='blue', bg='orange', font={'size': 15})
        app.startTabbedFrame("TabbedFrame")
        app.setTabbedFrameTabExpand("TabbedFrame", expand=True)

        # Primer TAB
        app.startTab("Chat texto")
        app.addLabel("Msg2", "Quieres chatear con alguien ?")
        # Buscamos todos los usuarios de la base de datos que esten conectados
        app.addLabelOptionBox("Usuarios conectados: ", usuarios_conectados())
        # Se encarga de actualizar la lista de usuarios conectados cada vez que pasamos el raton por encima del wigdet.
        app.setOptionBoxOverFunction("Usuarios conectados: ", [actualizar_usuarios_conectados, None])
        app.setOptionBoxChangeFunction("Usuarios conectados: ", press_Usuario)
        app.stopTab()

        # Segundo TAB
        app.startTab("Chat video(En desarrollo)")
        # Imagen para el video
        app.image("videochat", "../Images/webcam.gif")
        app.setImageSize("videochat", 400, 400)
        # Botones para contrar del chat
        #app.addButtons([PLAY, PAUSE, STOP], [play_videochat, pause_videochat, stop_videochat])
        app.addButtons([PLAY, PAUSE, STOP], [None, None, None])
        app.addEmptyLabel("Vacio1")
        app.stopTab()

        app.stopTabbedFrame()

        app.buttons(["Cerrar sesion"], [cerrar_sesion])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Cerrar sesion'
        app.setStopFunction(cerrar_sesion)




    #---------------------------------------------------- VENTANA CUANDO DECIDES CON QUIEN CHATEAR (MAX 3) -------------------------------------------------#
    with app.subWindow("Ventana Inicio-Identificado-Client-0",  size="650x450", bg='blue'):
        app.addLabel("llamada-Client-0", "En ventana de llamada")
        app.addListBox("Chat-Client-0", ["Bienvenido al chat de texto, escriba en el input y pulse Enter para enviar"])
        app.setListBoxWidth("Chat-Client-0", 300)
        app.addEntry("ChatEntrada-Client-0")
        app.setEntrySubmitFunction("ChatEntrada-Client-0", send_msg_0)
        app.buttons(["Terminar chat client 0"], [terminar_client_chat_0])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Terminar chat client 0'
        app.setStopFunction(terminar_client_chat_0)

    with app.subWindow("Ventana Inicio-Identificado-Client-1",  size="650x450", bg='blue'):
        app.addLabel("llamada-Client-1", "En ventana de llamada")
        app.addListBox("Chat-Client-1", ["Bienvenido al chat de texto, escriba en el input y pulse Enter para enviar"])
        app.setListBoxWidth("Chat-Client-1", 300)
        app.addEntry("ChatEntrada-Client-1")
        app.setEntrySubmitFunction("ChatEntrada-Client-1", send_msg_1)
        app.buttons(["Terminar chat client 1"], [terminar_client_chat_1])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Terminar chat client 1'
        app.setStopFunction(terminar_client_chat_1)

    with app.subWindow("Ventana Inicio-Identificado-Client-2",  size="650x450", bg='blue'):
        app.addLabel("llamada-Client-2", "En ventana de llamada")
        app.addListBox("Chat-Client-2", ["Bienvenido al chat de texto, escriba en el input y pulse Enter para enviar"])
        app.setListBoxWidth("Chat-Client-2", 300)
        app.addEntry("ChatEntrada-Client-2")
        app.setEntrySubmitFunction("ChatEntrada-Client-2", send_msg_2)
        app.buttons(["Terminar chat client 2"], [terminar_client_chat_2])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Terminar chat client 2'
        app.setStopFunction(terminar_client_chat_2)

    # ---------------------------------------------------- VENTANA CUANDO ALGUIEN QUIERE CHATEAR CONTIGO (MAX 3)  --------------------------------------------#
    with app.subWindow("Ventana Inicio-Identificado-Server-0",  size="650x450", bg='orange'):
        app.addLabel("llamada-Server-0", "En ventana de llamada")
        app.addListBox("Chat-Server-0", ["Bienvenido al chat de texto, escriba en el input y pulse Enter para enviar"])
        app.setListBoxWidth("Chat-Server-0", 300)
        app.addEntry("ChatEntrada-Server-0")
        app.setEntrySubmitFunction("ChatEntrada-Server-0", send_msg_server_0)
        app.buttons(["Terminar chat server 0"], [terminar_server_chat_0])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Terminar chat server 0'
        app.setStopFunction(terminar_server_chat_0)

    with app.subWindow("Ventana Inicio-Identificado-Server-1",  size="650x450", bg='orange'):
        app.addLabel("llamada-Server-1", "En ventana de llamada")
        app.addListBox("Chat-Server-1", ["Bienvenido al chat de texto, escriba en el input y pulse Enter para enviar"])
        app.setListBoxWidth("Chat-Server-1", 300)
        app.addEntry("ChatEntrada-Server-1")
        app.setEntrySubmitFunction("ChatEntrada-Server-1", send_msg_server_1)
        app.buttons(["Terminar chat server 1"], [terminar_server_chat_1])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Terminar chat server 1'
        app.setStopFunction(terminar_server_chat_1)

    with app.subWindow("Ventana Inicio-Identificado-Server-2",  size="650x450", bg='orange'):
        app.addLabel("llamada-Server-2", "En ventana de llamada")
        app.addListBox("Chat-Server-2", ["Bienvenido al chat de texto, escriba en el input y pulse Enter para enviar"])
        app.setListBoxWidth("Chat-Server-2", 300)
        app.addEntry("ChatEntrada-Server-2")
        app.setEntrySubmitFunction("ChatEntrada-Server-2", send_msg_server_2)
        app.buttons(["Terminar chat server 2"], [terminar_server_chat_2])
        # Boton  rojo 'x' para cerrar la ventana, misma funcionalidad que dar a boton 'Terminar chat server 2'
        app.setStopFunction(terminar_server_chat_2)

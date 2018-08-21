import socket


def lanzar_cliente(IP_server, Puerto_server, nombre):
    """
    Crea un socket contra el usuario con el que queremos inicar un chat.
    :param IP_server: ip del usuario al que hay que llamar.
    :param Puerto_server: puerto donde se haya a la escucha el socket del usuario al que hay llamar.
    :param nombre: del usuario que llama.
    :return:
    """
    # Creacion del socket de tipo stream.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(" [Client]: Creado socket.")

    # Conexion contra el servidor alojado en IP_server y con puerto Puerto_server
    client_socket.connect((IP_server, int(Puerto_server)))
    print(" [Client]: Conectado a ( "+IP_server+", "+str(Puerto_server)+" ).")

    client_socket.send(nombre.encode())
    return client_socket


def enviar_mensaje(client_socket, msg, app, num_ventana):
    """
    Se encarga de enviar mensajes contra el socket que se le pasa por parametro.
    A continuacion, muestra ese mensaje en tu propio chat y borra el msg del input.
    Todo ello tras presionar <Enter> (cuando se haya terminado de introducir el msg en el input).
    :param client_socket: socket abierto contra el otro usuario.
    :param msg: mensaje a enviar.
    :param app: objeto app, para poder hacer referencia a las acciones de la GUI.
    :param num_ventana: numero de la ventana sobre la que hay que realizar la accion.
    :return:
    """

    # Enviamos el mensaje.
    client_socket.send(msg.encode())

    # Si el mensaje enviado ha sido 'CLOSE'.
    if msg == "CLOSE":

        # Cerramos el socket.
        client_socket.close()
        print(" [Client]: CLOSE socket")

        # Escondemos la ventana del chat y borramos la conversacion.
        app.hideSubWindow("Ventana Inicio-Identificado-Client-" + str(num_ventana))
        app.clearListBox("Chat-Client-" + str(num_ventana))

    # Anadimos el mensaje a enviar en el ListBox (Chat) y borramos de la entry (ChatEntrada) ese mismo mensaje.
    else:
        app.addListItem("Chat-Client-"+str(num_ventana), "[Yo]: "+msg)

    app.clearEntry("ChatEntrada-Client-"+str(num_ventana), callFunction=True)


def recibir_mensaje(client_socket, app, num_ventana, users_Info):
    """
    Se encarga de recibir mensajes del usuario contra el que nos hemos conectado.
    A continuacion, imprime dicho mensaje en la ventana correspondiente a dicho chat.
    :param client_socket: socket abierto contra el otro usuario.
    :param app: objeto app, para poder hacer referencia a las acciones de la GUI.
    :param num_ventana: numero de la ventana sobre la que hay que realizar la accion.
    :return:
    """

    while True:
        try:
            data = client_socket.recv(1024).decode('ascii')
            print("[Client from Server('"+users_Info[str(num_ventana)]['IP']+"', "+users_Info[str(num_ventana)]['Puerto']+")]: "+data)

            # Si recibimos 'CLOSE' => cerrar socket y ventana del chat.
            if data == "CLOSE":

                # Mostramos mensaje informativo de que la otra persona termino el chat.
                app.infoBox("Ventana Inicio-Identificado-Client-"+str(num_ventana),
                            "El usuario " + users_Info[str(num_ventana)]['Nombre'] + " terminó el chat contigo.")

                # Cerramos socket.
                client_socket.close()
                print(" [Client]: CLOSE socket.")

                # Borramos la informacion correspondiente a dicho usuario de users_Info.
                users_Info[str(num_ventana)] = 'Null'

                # Escondemos la ventana del chat y borramos la conversacion.
                app.hideSubWindow("Ventana Inicio-Identificado-Client-"+str(num_ventana))
                app.clearListBox("Chat-Client-" + str(num_ventana))

                # Cortamos el bucle.
                break

            else:
                app.addListItem("Chat-Client-" + str(num_ventana),
                                "[" + users_Info[str(num_ventana)]['Nombre'] + "]: " + data)

        except:
            print("Error")
            break
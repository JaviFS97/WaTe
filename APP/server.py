import socket
import threading
import api
from random import randint

Num_Max_client = 3
Num_Now_client = 0

my_server = 'Null'

# Es una variable global que contiene informacion necesaria para llevar a cabo la conexion.
# Contiene la informacion necesaria de todos los users con los que se ha hablado, durante una sesion.
# Con un maximo de 3 usuarios que te hayan llamado.
# SOLO CONTIENE INFORMACION DE LOS LLAMADOS SERVERS.
users_Info = {'0': 'Null',
              '1': 'Null',
              '2': 'Null'}


def handler_cliente(new_socket, client_address, app, num_ventana):
    """
    Funcion que se ejecutara como hilo mientras se mantenga la comunicacion con el cliente.
    Queda a la espera de datos por parte del cliente.
    :param new_socket: el nuevo socket asignado por el server para la comunicacion con el cliente.
    :param client_address: tanto la ip como el puerto del cliente.
    :return: None
    """

    global Num_Max_client, Num_Now_client
    print(" [Server]: Acceso a handler_cliente.")
    first_time = True
    users_Info[str(num_ventana)]['Nombre'] = new_socket.recv(1024).decode('ascii')
    while True:
        try:
            # Informacion recibida
            data = new_socket.recv(1024).decode('ascii')
            print(" [Server from Client("+str(client_address)+"]: "+data)

            # Si es el primer mensaje que nos mandan, mostramos la interfaz grafica.
            if first_time:
                # Si alguien nos ha llamado, mostramos una ventana para el chat.
                # Mostramos una nueva ventana donde poder llevar a cabo el chat 0, 1 o 2..
                app.showSubWindow("Ventana Inicio-Identificado-Server-" + str(num_ventana))

                first_time = False

            # Si recibimos 'CLOSE' => cerrar socket y ventana del chat.
            if str(data) == "CLOSE":
                Num_Now_client -= 1

                app.infoBox("Ventana Inicio-Identificado-Server-" + str(num_ventana),
                            "El usuario '" + users_Info[str(num_ventana)]['Nombre'] + "' terminó el chat contigo.")
                # Cerramos socket.
                new_socket.close()

                # Colocamos la informacion del socket a Null
                users_Info[str(num_ventana)] = "Null"

                # Escondemos la ventana del chat y borramos la conversacion
                app.hideSubWindow("Ventana Inicio-Identificado-Server-" + str(num_ventana))
                app.clearListBox("Chat-Server-" + str(num_ventana))

                print(" [Server from Client(" + str(client_address) + "]: CLOSE => (" + str(Num_Now_client) + "/" + str(Num_Max_client) + ")=(now/max)...")

                # Cortamos el bucle.
                break

            else:
                # Agregamos dicho mensaje a la interfaz grafica
                app.addListItem("Chat-Server-" + str(num_ventana),
                                "[" + users_Info[str(num_ventana)]['Nombre'] + "]: " + data)

        except:
            print("Error")
            break


def enviar_mensaje(msg, app, num_ventana):
    """
    Se encarga de enviar mensajes siendo server.
    Si el mensaje es 'CLOSE', pregunta por el asentimiento del usuario por terminar el chat.
    :param msg: mensaje introducido en la input.
    :param app: instancia de la interfaz grafica.
    :param num_ventana: del chat perteneciente a esta comunicacion.
    :return: None
    """
    global Num_Max_client, Num_Now_client

    # Si el mensaje ha enviar es 'CLOSE'.
    if msg == "CLOSE":
        respuesta = app.yesNoBox("Terminar conversacion",
                                 "Deseas terminar el chat con " + users_Info[str(num_ventana)]['Nombre'] + " ?")
        if respuesta:
            users_Info[str(num_ventana)]['Socket'].send(msg.encode())
            Num_Now_client -= 1

            # Cerramos socket.
            users_Info[str(num_ventana)]['Socket'].close()

            # Colocamos la informacion del socket a Null
            users_Info[str(num_ventana)] = "Null"

            # Escondemos la ventana del chat y borramos la conversacion
            app.hideSubWindow("Ventana Inicio-Identificado-Server-" + str(num_ventana))
            app.clearListBox("Chat-Server-" + str(num_ventana))

            print(" [Server from Client]: CLOSE => (" + str(Num_Now_client) + "/" + str(Num_Max_client) + ")=(now/max)...")

    # Si el mensaje a enviar no es 'CLOSE'
    else:
        # Enviamos el mensaje.
        users_Info[str(num_ventana)]['Socket'].send(msg.encode())
        # Anadimos el mensaje a enviar en el ListBox (Chat)
        app.addListItem("Chat-Server-"+str(num_ventana), "[Yo]: "+msg)

    # Pase lo que pase,borramos de la entry (ChatEntrada) ese mismo mensaje.
    app.clearEntry("ChatEntrada-Server-"+str(num_ventana), callFunction=True)


def tienes_chats_server():
    """
    Recorre users_Info para comprobar si hay algun chat server activo.
    Si lo hay, devolvera True.
    :return:
    """
    for key in users_Info:
        if users_Info[str(key)] != 'Null':
            return True

    return False

def lanzar_server(Nombre, ClavePublica, app):
    """
    Se ejecuta cada vez que el usuario entra en el sistema. Si funcion es actualizar los datos referentes a la conexion (IP, Puerto, estado) en la BD
    para posteriormente abrir un socket que quede a la escucha de peticiones.
    :param Nombre:
    :param ClavePublica:
    :param app: es la instancia de la interfaz grafica
    :return: None
    """

    global Num_Max_client, Num_Now_client

    # Obtenemos la IP actual de nuestro pc.
    IP = get_IP()

    # Generamos un numero aleatorio para determinar el Puerto.
    Puerto = randint(10000, 60000)

    # Definimso el estado del user como conectado. 1==True
    estadoUser = 1

    # Creacion del socket de escucha
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((IP, Puerto))
        server_socket.listen(Num_Max_client)
        print(" [Server]: Creado socket ( " + IP + ", " + str(Puerto) + " ).")

        global my_server
        my_server = server_socket

    except:
        print("Error al crear socket")

    # Actualizamos la informacion relevante del usuario (IP, Puerto, estadoUser, ClavePublica)
    api.update_userLoginInfo(Nombre, IP, Puerto, estadoUser, ClavePublica)

    while True:
        print(" [Server]: Esperando clientes("+str(Num_Now_client)+"/"+str(Num_Max_client)+")=(now/max)...")

        # Creacion de otro socket independiente al de escucha para chatear con el cliente.
        new_socket, client_address = server_socket.accept()
        Num_Now_client += 1
        print(" [Server]: Conexion aceptada con "+str(client_address)+".")

        user_Info = {#"IP": client_address[0],
                     #"Puerto": client_address[1],
                    "Nombre": 'Null',
                    "Socket": new_socket}

        # Calculamos la longitud de users_Info, pasa saber en que posicion insertar en la misma.
        long = len(users_Info)

        # Insertamos la informacion en la variable global users_Info, en la que este vacia.
        num_ventana = -1
        cuenta = 0
        while cuenta < long:
            if users_Info[str(cuenta)] == "Null":
                users_Info[str(cuenta)] = user_Info
                num_ventana = cuenta
                break

            cuenta += 1
        # Si ya tiene 3 chat abiertos
        else:
            app.infoBox("Maximo numeros de chats activos",
                        "Ya tienes 3 chats activos.\n Si deseas hablar con otra persona, cierra uno de tus chats activos.")

        if (num_ventana >= 0) and (num_ventana < 3):
            # Creacion hilo para ejecucion concurrente
            server_thread = threading.Thread(target=handler_cliente, args=(new_socket,
                                                                           client_address,
                                                                           app,
                                                                           num_ventana))
            server_thread.daemon = True
            server_thread.start()


def parar_server():

    # Para el socket del server. El que queda a la escucha de peticiones.
    my_server.close()

    # todo Hay que parar los sockets creados cuando llega una peticion de conex.


def get_IP():
    """
    Funcion que retorna la ip actual del ordenador en la red LAN.
    :return: ip del ordenador
    """

    # Abrimos un socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Intentamos conectar contra google.
        s.connect(('8.8.8.8', 1))
        # Nos dice cual es la IP y Puerto utilizados.
        IPandPort = s.getsockname()

    except:
        # Si no se pudo conectar, por defecto colocamos la ip 127.0.0.1
        IP = '127.0.0.1'
    finally:
        # Cerramos socket
        s.close()

    IP = IPandPort[0]
    return IP


if __name__ == '__main__':
    print(get_IP())

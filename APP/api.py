import requests
import json

#ID_AUTHORIZATION= 'eE609B43dc1f72CF'
#HEADER = {'authorization': ID_AUTHORIZATION, 'Content-Type': 'application/json'}
HEADER = {'Content-Type': 'application/json'}
URL = "http://localhost/WaTe/API/wate.php"


def get_StatusServer():
    """
    Indica si hay conexion al servidor y a la BD.
    :return:
    """

    return True


def get_AllUser():
    """
    Obtiene todos los usuarios que hay registrados en la BD. Mostrando todos sus campos.
    :return: None
    """

    response = requests.request("GET", URL+"/users/search", headers=HEADER)
    binary = response.content.decode('utf-8')
    output = json.loads(binary)

    if response.status_code == 200:
        return output


def get_UserLoginInfo(Nombre):
    """
    Obtiene la informacion relativa al login del usuario (password y salt).
    :param Nombre:
    :return:
    """

    parametros = {"Nombre": Nombre,
                  "Login": "True"} # Necesaria la bandera 'Login' a True

    response = requests.request("GET", URL+"/users/search", headers=HEADER, params=parametros)
    if response.status_code == 200:
        if response.content == "false":
            response_Data = {'status_code': "ERROR"}
            return response_Data

        # Para convertir el json en un dicc
        binary = response.content.decode('utf-8')
        output = json.loads(binary)

        response_Data = {'status_code': "OK",
                         'Salt': output["Salt"],
                         'PasswordHash': output["Password"],
                         'Estado': output["Estado"]}
        return response_Data

    else:
        response_Data = {'status_code': "ERROR"}
        return response_Data


def get_IPandPort(Nombre):
    """
    Obtiene la informacion relativa del server de dicha persona(IP y Puerto).
    :param Nombre:
    :return:
    """
    parametros = {"Nombre": Nombre,
                  "Login": "False"}  # Necesaria la bandera 'Login' a False para no confundir con login}

    response = requests.request("GET", URL+"/users/search", headers=HEADER, params=parametros)
    if response.status_code == 200:
        if response.content == "false":
            response_Data = {'status_code': "ERROR"}
            return response_Data

        # Para convertir el json en un dicc
        binary = response.content.decode('utf-8')
        output = json.loads(binary)

        response_Data = {'status_code': "OK",
                         'IP': output["IP"],
                         'Puerto': output["Puerto"],
                         'Estado': output["Estado"]}
        return response_Data

    else:
        response_Data = {'status_code': "ERROR"}
        return response_Data


def get_PublicKey(idUser):
    """
    Pasado un id de usuario nos devuelve su clave publica.

    :param idUser: el id del usuario
    :return publicKey: - la clave publica correspondiente a dicho usuario
                       - None si no existe usuario
    """

    parametros = {"id": idUser}
    response = requests.request("GET", URL, headers=HEADER, params=parametros)

    # Si fue bien
    if response.status_code == 200:
        # Para convertir el json en un dicc
        binary = response.content.decode('utf-8')
        output = json.loads(binary)

        return output['ClavePublica']

    else:
        print("Error al obtener la clave publica")
        return None


def create_User(Nombre, SaltYHashPassword):
    """
    Se encarga de crear una entrada en la BD con la informacion relativa al usuario.

    :param Nombre: con el que se desea llamar el usuario.
    :param SaltYHashPassword: Contiene el salt y el hash del password.

    :return:
    """

    print(Nombre, SaltYHashPassword)

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Nombre\"\r\n\r\n"+Nombre+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Password\"\r\n\r\n"+SaltYHashPassword['hash']+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Salt\"\r\n\r\n"+SaltYHashPassword['salt']+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    }

    response = requests.request("POST", URL+"/users/register", data=payload, headers=headers)

    # Si fue bien
    if response.status_code == 200:
        return True

    else:
        print("Error al crear user")
        return False


def update_userLoginInfo(Nombre, IP, Puerto, estadoUser, ClavePublica):
    """
    Cuando realizamos el login es necesario actualizar tanto la IP, como el puerto, estadoUser y clavepublica.

    :param Nombre:
    :param IP:
    :param Puerto:
    :param estadoUser:
    :param ClavePublica:
    :return:
    """
    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Nombre\"\r\n\r\n"+Nombre+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"IP\"\r\n\r\n"+IP+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Puerto\"\r\n\r\n"+str(Puerto)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ClavePublica\"\r\n\r\n"+ClavePublica+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Estado\"\r\n\r\n"+str(estadoUser)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    }

    response = requests.request("POST", URL+"/users/update", data=payload, headers=headers)

    #print(response.text)
    # Si fue bien
    if response.status_code == 200:
        return True

    else:
        print("Error al actualizar user")
        return False


def update_userLogoutInfo(Nombre):
    """
    Cuando realizamos el logut es necesario actualizar tanto la IP, como el puerto, estadoUser y clavepublica.

    :param Nombre:
    :return:
    """
    IP = 'Null'
    Puerto = 'Null'
    estadoUser = '0'
    ClavePublica = 'Null'

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Nombre\"\r\n\r\n"+Nombre+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"IP\"\r\n\r\n"+IP+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Puerto\"\r\n\r\n"+str(Puerto)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ClavePublica\"\r\n\r\n"+ClavePublica+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"Estado\"\r\n\r\n"+str(estadoUser)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    }

    response = requests.request("POST", URL+"/users/update", data=payload, headers=headers)

    #print(response.text)
    # Si fue bien
    if response.status_code == 200:
        return True

    else:
        print("Error al actualizar user")
        return False

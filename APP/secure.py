import hashlib
import random

def generatingSalt():
    """
    Generamos un salt para evitar ataques por tablas rainbow.
    :return: salt
    """
    salt = []
    # Cogemos 10 caracteres aleatorios de la lista.
    for i in range(10):
        Oldsalt= random.choice("abcdefghijklmnopqrstvwxyz0123456789")
        salt.append(Oldsalt)

    return salt


def hashingPassword(password):
    """
    Recibe la contrasenia del registro, se obtiene un salt aleatorio, se concatena a la contrasenia el salt para obtener un hash.
    :param password: contrasenia introducida por el usuario al registrarse
    :return: diccionario con el salt y el hash, para almacenarlo en la BD.
    """

    # Obtenemos el salt
    salt = ''.join(generatingSalt())

    # Concatenamos al password el salt y realizamos el hash
    hash = hashlib.sha256(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()

    # Guardamos en una lista el valor del salt y el hash completo, para almacenarlos en la BD.
    hashedPassword = {'salt': salt,
                      'hash': hash}

    return hashedPassword


def compareHash(password, saltBD , hashBD):
    """
    Comprueba si el password que introduce el usuario junto al salt almacenado en la BD coincide con el hash de la BD.
    :param password:
    :param hashBD:
    :param saltBD:
    :return:
    """

    hash = hashlib.sha256(password.encode('utf-8') + saltBD.encode('utf-8')).hexdigest()
    if hash == str(hashBD):
        return True
    else:
        return False


if __name__ == '__main__':
    print(hashingPassword("hola"))


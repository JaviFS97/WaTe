
# WaTe v1.0
# Tabla de contenidos

 1. **Introducción**.
 2. **Funcionalidades**:
	 2.1. **Arquitectura.**
	 2.2. **Seguridad**:
			 2.2.1.  Password y salt.
			 2.2.2. ~~Cifrado conexión.~~ ( Se implementará en v1.5)
			 2.2.3. ~~Cifrado archivos y firma.~~ ( Se implementará en v2.0)
 3. **Estructura del proyecto.**
 4. **Servidor de descubrimiento y API.**
 5. **Comunicaciones.**
 6. **Recursos.**
 7. **Ejecución.**


## 1. Introducción:
El objetivo es llevar a cabo una aplicación P2P de **chat por texto**, ~~chat por video y almacenamiento seguro de ficheros.~~ (v2.0)

Para ello, crearemos una aplicación que nos permita:

 - Transmitir y recibir texto cifrado entre pares de usuarios.
 - ~~Transmitir y recibir vídeo, sin audio, entre pares de usuarios.~~
 - ~~Transmitir y recibir archivos cifrados y firmados.~~ 
 
 Utilizando un protocolo P2P propio y soportando una comunicación unicast entre únicos pares.

## 2. Funcionalidades

### 2.1 Arquitectura:
A grandes rasgos, la aplicación P2P de chat de texto ~~y de video~~ deberá permitir que el usuario realice las siguientes acciones:

*  **Gestionar sus nicks** (creación). Para ello deberá solicitar un nick al usuario, y registrarlo a continuación en el servidor de descubrimiento. Este nick estará "reservado", a través del uso de una contraseña, a dicho usuario.

* **Realizar chat de texto con otro/s usuario/s**. La aplicación muestra una lista con los usuarios conectados en dicho instante.
Tras la elección del usuario, se abre una conexión directa con dicho usuarios, pudiendo tanto enviar como recibir texto.
La conversación se da por terminada cuando cualquiera de los dos usuarios finaliza el chat.
 
*  (Se implementará en v2.0) ~~**Realizar una videollamada con otro usuario**. Para ello la aplicación deberá permitir que el usuario escriba el nick del usuario con el que desea conectar. Tras ello, abrir una conexión directa con este usuario y empezar a capturar, enviar y recibir el video. También deberá permitir pausar y finalizar la llamada.~~

*  (Se implementará en v2.0) ~~**Realizar un sistema de almacenamiento seguro de archivos entre pares de usuarios**. Para ello la aplicación deberá que el usuario envíe archivos cifrados y firmados al usuario que haya elegido. Que el usuario destino pueda acceder a él, descargarlo y comprobar si su procedencia y contenido es el esperado.~~

### 2.2 Seguridad:
#### 2.2.1. Password y salt.
Para no dejar en plano las contraseñas que se almacenan en la BD, se utiliza el algoritmo de hashing sha256 para 'ocultarlas' . 
Para obtener este hash, se realiza la siguiente acción: generamos un salt con un longitud de 10 carácteres, concatenamos este salt a la contraseña introducida por el usuario y realizamos el hash == hash (salt + password). De esta manera, nos protegemos frente ataques de tablas rainbow.

####  2.2.2. ~~Cifrado conexión.~~ ( Se implementará en v1.5)
#### 2.2.3. ~~Cifrado archivos y firma.~~ ( Se implementará en v2.0)


##  3. **Estructura del proyecto.**
El proyecto está compuesto por las siguientes carpetas:
* **APP**: contiene toda la lógica de la aplicación junto con la interfaz gráfica.
-- api.py: contiene las funciones que se encargan de la comunicación con el servidor de descubrimiento.
-- client.py: contiene las funciones de generación de sockets y el envío y recepción de mensajes por dichos sockets.
-- main.py: contiene todo el flujo natural de la aplicación junto con la programación de la interfaz gráfica.
-- secure.py: funciones que aportan seguridad a la aplicación.
-- server.py: contiene las funciones de generación de sockects, handler al recibir conexiones y envío y recepción de mensajes.

* **Images**:  contiene las imágenes utilizadas por la interfaz gráfica.
* **API**: contiene la lógica del servidor, es decir, que hacer en caso de recibir una petición cuando se conectan contra él.
-- db.php: contiene las credenciales para la conexión contra dicha BD.
-- utils.php: tanto para iniciar sesión en la BD como funciones con utilidades de parseo .
-- wate.php: donde se realizan las consultas a la BD y que devuelven a la aplicación los datos requeridos.


## 4. Servidor de descubrimiento (DS):
Como un tablón de anuncios donde cada nuevo participante en la red pueda anunciar su dirección IP y puerto de escucha, de forma que el resto de participantes puedan conectarse a él.
Su función es mantener una pequeña base de datos con todos los usuarios registrados en la plataforma, guardando para cada uno de ellos:	
- Nick,
- Password,
- Salt,
- Clave pública, (se implementará en la v2.0)
- Dirección IP,
- Puerto de escucha,
-  Estado. 

## Descripción del API , Endpoints:
URL = "http://localhost/WaTe/API/wate.php"

### Gestión de identidades
- **Registrarse:** 
Cuando el usuario se registra en la ventana de inicio de la aplicación.
	* url: URL/users/register
	* Parámetros:
	-- Nick: del user.
	-- HashPassword: hash(salt+password)
	-- Salt: 
	* Respuesta: Si todo fue bien, respuesta HTTP = 200.
- **Obtener datos login:** 
Cuando el usuario introduce su nick y contraseña se contrasta con los datos obtenidos de la BD.
	* url : URL+/users/search
	* Parámetros: 
	-- Nick: del user.
	-- Login: bandera que debe estar a 'True'. 
	* Respuesta: Si todo fue bien, un json con el hash(salt+password) y el salt. 

- **Obtener IP y Puerto de un usuario:**	
Cuando un usuario quiere conocer donde se encuentra escuchando el server del usuario con el que quiere comunicarse.
	* url : URL+/users/search
	* Parámetros: 
	-- Nick: del user.
	-- Login: bandera que debe estar a 'False'. 
	* Respuesta: Si todo fue bien,  json con el IP y Puerto.

- **Obtener todos los usuarios:**	
Cuando un usuario quiere conocer todos los usuarios presentes en la BD.
	* url : URL+/users/search
	* Parámetros: 
	-- Nick: del user.
	-- Login: bandera que debe estar a 'False'. 
	* Respuesta: Si todo fue bien, un json que contiene toda la información de todos los usuarios.


- **Actualizar datos BD:**
	Para actualizar una serie de campos cuando el login se realiza con éxito,
	* url : URL+/users/update
	* Parámetros: 
	-- IP: donde tiene el server escuchando.
	-- Puerto: donde tiene el server escuchando.
	-- Estado usuario: 1 == activo
	-- ClavePublica: 
	* Respuesta: Si todo fue bien, respuesta HTTP = 200.

	O cuando el usuario abandona la aplicación.
	* url : URL+/users/update
	* Parámetros: 
	-- IP: null
	-- Puerto: null
	-- Estado usuario: 0 == desconectado
	-- ClavePublica: null
	* Respuesta: Si todo fue bien, respuesta HTTP = 200.




### ~~Gestión de ficheros~~ (Se implementará en la v2.0)

## 5. Comunicaciones.

## ~~Comandos de control~~  (Se implementará en la v2.0)


Son los mensajes que se intercambian directamente los pares para controlar todos los aspectos de la videollamada, como señalización de inicio, pausa, final, etc.

 - **Comando LLAMANDO**:
Objetivo: Señaliza que un nodo quiere establecer una videollamada con otro.
**Sintaxis**: LLAMANDO nick UDPport, donde UDPport es el puerto UDP en el que el llamante desea recibir el video del llamado.
**Posibles respuestas/errores:**
-- LLAMADA_ACEPTADA nick dstUDPport, donde dstUDPport es donde el
llamado recibirá el video
-- LLAMADA_DENEGADA nick

- **Comando PARAR:**
Objetivo: Señaliza que se desea pausar temporalmente una llamada, sin cortarla.
**Sintaxis**: PARAR nick
**Posibles respuestas/errores:** Ninguna

- **Comando REANUDAR:**
Objetivo: Señaliza que se desea reanudar una llamada anteriormente pausada.
**Sintaxis**: REANUDAR nick
**Posibles respuestas/errores:** Ninguna


- **Comando TERMINAR:**
**Objetivo**: Señaliza que se desea finalizar una llamada.
**Sintaxis**: TERMINAR nick
**Posibles respuestas/errores:** Ninguna.


## 6. Recursos:
Para la interfaz gráfica se ha utilizado el framework appJar. http://appjar.info/
Se utilizó la versión 1.0, se incluye en el repositorio un zip con todos sus archivos por si cambian de versión.
o se puede instalar a través de pip3: `sudo pip3 install appjar`

Para la conexión contra la API se utilizó la librería requests.

Para la captura de imágenes de la webcam, se utilizó el binding para Python de la librería OpenCV puede ser muy útil.


## 7. Ejecución:
Acceder al terminal para ejecutar Xampp.

    cd /opt/lampp/
    sudo ./manager-linux-x64.run
Una vez hecho esto, inciar el servidor apache y la base de datos MySQL DATABASE.
Para acceder a la base de datos, escribir en el navegador: http://localhost/phpmyadmin/

Descargar el repositorio. El cual estará compuesto por:
-- API/
-- APP/
-- Images/

Accedemos a /opt/lampp/htdocs, donde creamos una carpeta llamada 'WaTe'. En su interior colocamos la carpeta API que se encuentra en el repositorio.

Posterior a esto, creamos una carpeta con el nombre que queramos para almacenar 'APP' y 'Images'

    cd APP/
    python3 main.py
A partir de este momento, se mostrará la pantalla de inicio de la interfaz gráfica.


PD. por ahora solo sirve si nos encontramos en una misma red local.
PD2. si queremos ejecutarlo entre 2 ordenadores, uno de ellos tendrá alojado el server junto a la BD. Por lo que el otro ordenador tendrá que apuntar a su dirección ip, esto quiere decir que, habrá que acceder al archivo api.py y modificar 'localhost' por la IP del ordenador que contenga el servidor.

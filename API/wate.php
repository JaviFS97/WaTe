<?php
include "db.php";
include "utils.php";

// Establecemos conexion con la base de datos
$dbConn =  connect($db);

// Obtenemos la uri
$uri = $_SERVER['PATH_INFO'];
//echo $uri;


// listar todos los usuarios o solo uno
if (strcmp($uri, "/users/search")==0){

  if ($_SERVER['REQUEST_METHOD'] == 'GET'){

      //Mostrar toda la informacion de un usuario, por su id
      if (isset($_GET['id'])){        
        $sql = $dbConn->prepare("SELECT * FROM Usuarios where id=:id");
        $sql->bindValue(':id', $_GET['id']);
        $sql->execute();
        header("HTTP/1.1 200 OK");
        echo json_encode(  $sql->fetch(PDO::FETCH_ASSOC)  );
        exit();

      }elseif (isset($_GET['Nombre'])) {

        //Informacion relativa al login del usuario, por su nombre
        $status = $_GET['Login'];
        if ( $status == "True"){
          $sql = $dbConn->prepare("SELECT Salt, Password, Estado FROM Usuarios where Nombre=:Nombre");
          $sql->bindValue(':Nombre', $_GET['Nombre']);
          $sql->execute();
          header("HTTP/1.1 200 OK");
          echo json_encode(  $sql->fetch(PDO::FETCH_ASSOC)  );
          exit();

        //Informacion relativa al server del usuario, por su nombre
        }elseif ($status == "False"){
          $sql = $dbConn->prepare("SELECT IP, Puerto, Estado FROM Usuarios where Nombre=:Nombre");
          $sql->bindValue(':Nombre', $_GET['Nombre']);
          $sql->execute();
          header("HTTP/1.1 200 OK");
          echo json_encode(  $sql->fetch(PDO::FETCH_ASSOC)  );
          exit();


        }else{
          header("HTTP/1.1 404 Not Found");
          echo json_encode(  "URL erronea"  );
        }

      
      //Mostrar todos los usuarios
      }else {        
        $sql = $dbConn->prepare("SELECT * FROM Usuarios");
        $sql->execute();
        $sql->setFetchMode(PDO::FETCH_ASSOC);
        header("HTTP/1.1 200 OK");
        echo json_encode( $sql->fetchAll()  );
        exit();
    }
  }
}

// Crear un nuevo usuario
if (strcmp($uri, "/users/register")==0){

  if ($_SERVER['REQUEST_METHOD'] == 'POST'){
    
      $input = $_POST;

      print_r( $input);

      $sql = "INSERT INTO Usuarios
            (Nombre, Password, Salt)
            VALUES
            (:Nombre, :Password, :Salt)";

      $statement = $dbConn->prepare($sql);
      bindAllValues($statement, $input);
      $statement->execute();
      $postId = $dbConn->lastInsertId();

      if($postId){
        $input['id'] = $postId;
        header("HTTP/1.1 200 OK");
        echo json_encode($input);
        exit();
    }
  }
}


//Borrar
if (strcmp($uri, "/users/delete")==0){

  if ($_SERVER['REQUEST_METHOD'] == 'DELETE')
  {
    $id = $_GET['id'];
    $statement = $dbConn->prepare("DELETE FROM posts where id=:id");
    $statement->bindValue(':id', $id);
    $statement->execute();
    header("HTTP/1.1 200 OK");
    exit();
  }
}


//Actualizar los campos IP y Puerto de un usuario.
if (strcmp($uri, "/users/update")==0){

  if (strcmp($_SERVER['REQUEST_METHOD'], 'POST')==0) {
    /*
    HAY QUE CONVERTIRLO EN PUT

    parse_str(file_get_contents('php://input'), $_PUT);
    echo "contenido: \n";
    print_r( $_PUT[0]);
    $input = $_PUT;
    */
    $input = $_POST;

    print_r ($input);

    $nombre = $input['Nombre'];
    $ip = $input['IP'];
    $puerto = $input['Puerto'];
    $estado = $input['Estado'];
    $clavePublica = $input['ClavePublica'];

    $sql = "
          UPDATE Usuarios
          SET IP='$ip', Puerto='$puerto' ,ClavePublica='$clavePublica', Estado='$estado'
          WHERE Nombre='$nombre'
           ";

    $statement = $dbConn->prepare($sql);
    bindAllValues($statement, $input);

    $statement->execute();
    header("HTTP/1.1 200 OK");
    exit();

  }else{
    header("HTTP/1.1 400 Bad Request");
  }
}


//En caso de que ninguna de las opciones anteriores se haya ejecutado
header("HTTP/1.1 400 Bad Request");

?>

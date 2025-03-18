
# Ejemplo de autenticación OAuth2 en Flask

Este proyecto representa un esquema minimalista de autenticación basado en OAuth2 - OpenID. 

## Preparación del entorno de pruebas

Para poder ejecutar este proyecto, es necesario disponer de un servidor SSO compatible con el protocolo OAuth2.

### Keycloak

Para este ejemplo, optaremos por un servidor [Keycloak](https://www.keycloak.org). Se puede utilizar el siguiente comando que pone en marcha el servidor en un contenedor Docker:

```shell
docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:24.0.2 start-dev
```

Acto seguido, se ha de crear un cliente en el servidor Keycloak. Para ello, se ha de acceder a la [interfaz de administración de Keycloak](http://localhost:8080/admin) con el usuario `admin` y la contraseña `admin`. Una vez dentro, se ha de crear un nuevo cliente con los siguientes datos:

- **Client ID**: `123`
- **Client Protocol**: `openid-connect`
- **Access Type**: `confidential`
- **Standard Flow Enabled**: `true`
- **Direct Access Grants Enabled**: `true`
- **Valid Redirect URIs**: `http://localhost:5000/callback`
- **Web Origins**: `*`

Lo siguiente es crear uno o varios usuarios en el servidor Keycloak. Para ello, se ha de acceder a la [interfaz de administración de Keycloak](http://localhost:8080/admin) y añadir usuarios con sus respectivas contraseñas.

### Amazon Cognito

Otra opción es utilizar [Amazon Cognito](https://aws.amazon.com/es/cognito/). Para ello, se ha de crear un nuevo usuario en el servicio y configurar un nuevo cliente de aplicación.

Para crear usuarios, ha de visitarse la [consola de Amazon Cognito](https://console.aws.amazon.com/cognito/users/). Una vez dentro, se ha de seleccionar el pool de usuarios y crear un nuevo usuario. Se puede indicar el nombre de usuario y los atributos del usuario; también se puede indicar una contraseña temporal que el usuario deberá cambiar en su primer acceso o utilizar una generada automáticamente.

El siguiente paso es crear un **cliente de aplicación**. Para ello, ha de visitarse la [consola de Amazon Cognito](https://console.aws.amazon.com/cognito/users/). Una vez dentro, se ha de seleccionar el pool de usuarios y acceder al apartado de **Clientes de aplicación** (**App clients**). Se ha de crear un nuevo cliente de aplicación con los siguientes datos:

- **Tipo de aplicación**: Aplicación web tradicional
- **Nombre de cliente**: *(elegir un nombre)*
- **URL de retorno**: `http://localhost:5000/callback`

Tras introducir estos datos, se ha de guardar el cliente y se mostrarán los datos de configuración del cliente. Se han de copiar los valores de **ID de cliente** y **Secreto de cliente** para configurar la aplicación cliente.

Es importante conocer los *endpoints* de autorización y acceso a los recursos. Dichos endpoints dependen del pool de usuarios y de la región en la que se haya creado el pool. Para obtener los datos de configuración, se tomará el ID del pool de usuarios y la región para construir los *endpoints* de la siguiente forma:

- **Dominio del pool de usuarios**: `https://<pool>.auth.<region>.amazoncognito.com`
- **Endpoint de autorización**: `https://<pool>.auth.<region>.amazoncognito.com/oauth2/authorize`
- **Endpoint de acceso al token**: `https://<pool>.auth.<region>.amazoncognito.com/oauth2/token`
- **Endpoint de detalles del propietario del recurso**: `https://<pool>.auth.<region>.amazoncognito.com/oauth2/userInfo`

Más información en [User-interactive managed login and classic hosted UI endpoints](https://docs.aws.amazon.com/cognito/latest/developerguide/managed-login-endpoints.html).

Una vez hecho esto, se han de configurar los datos del SSO en el fichero `config.ini` (ver más abajo).



## Puesta en marcha

Una vez hecho esto, se procederá a poner en marcha la aplicación cliente. Para ello, se ha de clonar este repositorio y ejecutar los siguientes comandos:

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Una vez instaladas las dependencias, se han de configurar los datos del SSO en el fichero `config.ini` (ver más abajo) y ejecutar la aplicación con el siguiente comando:

```shell
flask run
```


## Ajustes

Los ajustes han de incorporarse a un fichero `config.ini` o mediante variables de entorno. Dicho fichero contendrá algo similar a:

```ini
[App]
secret_key=zzzzzzzzzzzzzz

[OAuth2]
client_id=yyyyyyyyyyyy
client_secret=xxxxxxxxxxxxxxxxxxxxxxxxxxx
redirect_uri=http://localhost:5000/callback
url_authorize=https://example.com/oauth2/authorize
url_access_token=https://example.com/oauth2/token
url_resource_owner_details=https://example.com/oauth2/userInfo
```

## Funcionamiento

Esta demo funciona del siguiente modo:

1. El usuario accede al documento raíz (`/`), desde la ruta [http://localhost:5000](http://localhost:5000).
2. Al no tener un token de acceso previamente obtenido, es redirigido a la URL de autorización (`/login`). Ahí se le presenta un botón para acceder al servidor SSO.
3. El servidor SSO socilita autenticación y autorización al usuario para conceder el acceso a la demo.
4. Una vez que el usuario confirma, es redirigido de vuelta a la demo, en la ruta `/callback`. En ese momento se procesa la petición de retorno, obteniendo el token de acceso
y los datos del usuario.
5. El token de acceso se almacena en la sesión junto con los datos del usuario y se redirige al documento raíz.
6. Ahora ya tiene token de acceso y puede acceder a los datos protegidos, mostrándolos junto con las credenciales obtenidas.




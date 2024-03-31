
# Ejemplo de autenticación OAuth2 en Flask

Este proyecto representa un esquema minimalista de autenticación basado en OAuth2 - OpenID. 

## Preparación del entorno de pruebas

Para poder ejecutar este proyecto, es necesario disponer de un servidor SSO compatible con el protocolo OAuth2. Para este ejemplo, optaremos por un servidor [Keycloak](https://www.keycloak.org). Se puede utilizar el siguiente comando que pone en marcha el servidor en un contenedor Docker:

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

Una vez hecho esto, se procederá a poner en marcha la aplicación cliente. Para ello, se ha de clonar este repositorio y ejecutar los siguientes comandos:

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Una vez instaladas las dependencias, se han de configurar los datos del SSO en el fichero `.env` (ver más abajo) y ejecutar la aplicación con el siguiente comando:

```shell
flask run
```


## Ajustes

Los ajustes han de incorporarse a un fichero ``.env`` o mediante variables de entorno. Dicho fichero contendrá algo similar a:

```
CLIENT_ID=123
CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxx
REDIRECT_URI=http://localhost:5000/callback
URL_AUTHORIZE=http://localhost:8080/realms/master/protocol/openid-connect/auth
URL_ACCESS_TOKEN=http://localhost:8080/realms/master/protocol/openid-connect/token
URL_RESOURCE_OWNER_DETAILS=http://localhost:8080/realms/master/protocol/openid-connect/userinfo
SECRET_KEY=yyyyyyyyyyyyy
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




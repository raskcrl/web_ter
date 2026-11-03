# Web Ter(NOMBRE PROVIVIONAL) — Plataforma de Rehabilitación Física

Aplicación web desarrollada con Django que busca apoyar a las personas en la consulta y organización de ejercicios de rehabilitación física desde casa.

El proyecto cuenta con un catálogo público de ejercicios y rutinas, además de funcionalidades personales para que los usuarios registrados puedan guardar rutinas y, en futuras fases, llevar un seguimiento de sus actividades y progreso.

---

## 1. Tecnologías utilizadas

El proyecto utiliza las siguientes tecnologías:

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12.10 | Lenguaje principal del proyecto. |
| Django | 6.1.2 (última versión reportada en el entorno; verificar `requirements.txt`) | Framework para el desarrollo del backend y las vistas web. |
| MariaDB | 10.4.32 | Sistema gestor de base de datos utilizado mediante XAMPP. |
| MySQL / SQL | Compatible con el entorno MariaDB | Administración y consulta de datos. |
| HTML5 | — | Estructura de las páginas web. |
| CSS3 | — | Diseño visual y adaptación a diferentes dispositivos. |
| JavaScript | — | Funcionalidades del lado del cliente cuando son necesarias. |
| Git | 2.55.0.windows.5 | Control de versiones. |
| GitHub | — | Repositorio remoto del proyecto. |
| Visual Studio Code | 1.143.1 | Editor de código. |
| XAMPP | — | Entorno local para administrar el servidor de base de datos. |

**Nota sobre Django:** se ha reportado Django 6.1.2 en el entorno, pero algunos archivos del proyecto contienen referencias a Django 5.0.14. Para conocer la versión definitiva, ejecutar:

```powershell
.\venv\Scripts\python.exe -m django --version
```

También se recomienda consultar `requirements.txt`, ya que es el archivo que contiene las dependencias declaradas del proyecto.

---

## 2. Tecnologías y arquitectura

### Backend: Django

Django es el framework principal del proyecto. Se encarga de:

- Gestionar las solicitudes y respuestas del servidor.
- Administrar las rutas de navegación.
- Procesar formularios.
- Gestionar usuarios y autenticación.
- Conectar las aplicaciones con la base de datos.
- Consultar, registrar y modificar información.
- Renderizar las plantillas HTML.

Se utiliza la arquitectura basada en aplicaciones de Django, lo que permite separar las funcionalidades del sistema en módulos independientes.

### Frontend: HTML, CSS y JavaScript

La interfaz se desarrolla utilizando:

- **HTML5:** estructura y contenido de las páginas.
- **CSS3:** estilos, distribución de elementos y diseño responsive.
- **JavaScript:** interacciones adicionales cuando se requieren.

Las plantillas utilizan el sistema de templates de Django para mostrar información dinámica procedente del backend.

### Base de datos: MariaDB

Se utiliza MariaDB mediante XAMPP para almacenar la información del sistema.

La base de datos del proyecto se llama:

```text
web_ter_db
```

Django se comunica con la base de datos mediante su sistema ORM, permitiendo trabajar con modelos de Python en lugar de escribir consultas SQL manualmente para las operaciones habituales.

---

## 3. Requisitos previos

Antes de ejecutar el proyecto se necesita:

1. Windows.
2. Python 3.12.10.
3. Visual Studio Code.
4. XAMPP con MariaDB.
5. Git.
6. El repositorio del proyecto.

Se recomienda utilizar la misma versión de Python para mantener la compatibilidad con el entorno de desarrollo.

---

## 4. Instalación del proyecto

### 4.1. Clonar el repositorio

Abrir una terminal de PowerShell y ejecutar:

```powershell
git clone https://github.com/raskcrl/web_ter.git
```

Entrar a la carpeta del proyecto:

```powershell
cd web_ter
```

### 4.2. Crear el entorno virtual

Crear un entorno virtual para instalar las dependencias de manera aislada:

```powershell
py -3.12 -m venv venv
```

### 4.3. Activar el entorno virtual

Ejecutar:

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell muestra que los scripts están restringidos, se puede utilizar directamente el ejecutable del entorno virtual en los siguientes comandos, sin necesidad de activar el entorno.

### 4.4. Actualizar pip

```powershell
python -m pip install --upgrade pip
```

### 4.5. Instalar dependencias

Instalar las dependencias declaradas en el archivo `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Si se utiliza el ejecutable directamente:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 5. Configuración de la base de datos

### 5.1. Iniciar XAMPP

Abrir el panel de control de XAMPP e iniciar el servicio de MariaDB, identificado normalmente como MySQL en el panel.

### 5.2. Crear la base de datos

Abrir phpMyAdmin desde el navegador:

```text
http://localhost/phpmyadmin
```

Crear una base de datos con el siguiente nombre:

```text
web_ter_db
```

Se recomienda utilizar la codificación:

```text
utf8mb4
```

### 5.3. Configurar la conexión en Django

La conexión se configura en:

```text
config/settings.py
```

Dentro de ese archivo se encuentra la configuración `DATABASES`.

La configuración debe coincidir con los datos del servidor MariaDB local:

- Motor de base de datos compatible con MySQL.
- Nombre: `web_ter_db`.
- Host: `localhost`.
- Puerto: `3306`.
- Usuario y contraseña correspondientes a la instalación local.

**Importante:** no publicar contraseñas ni credenciales reales en GitHub. Si se utilizan credenciales locales, deben mantenerse fuera del repositorio.

---

## 6. Preparar la base de datos

Una vez configurada la conexión, ejecutar las migraciones:

```powershell
python manage.py migrate
```

Este comando crea las tablas necesarias para las aplicaciones registradas en Django.

Para comprobar que el proyecto no tiene errores de configuración:

```powershell
python manage.py check
```

Para comprobar si existen cambios de modelos que todavía no tienen migración:

```powershell
python manage.py makemigrations --check --dry-run
```

---

## 7. Crear un administrador

Para acceder al panel de administración de Django, crear un superusuario:

```powershell
python manage.py createsuperuser
```

El sistema solicitará:

- Nombre de usuario.
- Correo electrónico.
- Contraseña.

El panel de administración estará disponible en:

```text
http://127.0.0.1:8000/admin/
```

Desde este panel se pueden administrar categorías, ejercicios y rutinas, de acuerdo con los modelos registrados en cada aplicación.

---

## 8. Ejecutar el proyecto

Con el entorno virtual preparado y la base de datos iniciada, ejecutar:

```powershell
python manage.py runserver
```

También se puede utilizar directamente:

```powershell
.\venv\Scripts\python.exe manage.py runserver
```

Abrir el navegador y visitar:

```text
http://127.0.0.1:8000/
```

Para detener el servidor, presionar:

```text
CTRL + C
```

**Importante:** cada vez que se quiera trabajar en el proyecto, se debe iniciar XAMPP y ejecutar el servidor de Django desde la carpeta raíz del proyecto.

---

## 9. Estructura del proyecto

La estructura principal está organizada de la siguiente manera:

```text
web_ter/
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   └── Aplicación principal y página de inicio
│
├── usuarios/
│   └── Registro, inicio de sesión y perfil
│
├── ejercicios/
│   └── Catálogo, categorías y detalles de ejercicios
│
├── rutinas/
│   └── Gestión y consulta de rutinas
│
├── seguimiento/
│   └── Módulo destinado al seguimiento del progreso
│
├── principal/
│   └── Aplicación destinada a funcionalidades principales
│
├── static/
│   ├── css/
│   └── Archivos estáticos del proyecto
│
├── media/
│   └── Archivos multimedia cargados por los usuarios
│
├── templates/
│   └── Plantillas generales, si corresponde
│
├── venv/
│   └── Entorno virtual de Python
│
├── manage.py
├── requirements.txt
└── .gitignore
```

La carpeta `venv` es el entorno virtual local y no debe subirse al repositorio.

---

## 10. Aplicaciones y funcionalidades desarrolladas

### 10.1. Core — Página principal

Aplicación encargada de la página de inicio del sistema.

Funcionalidades implementadas:

- Landing page.
- Barra de navegación.
- Presentación del proyecto.
- Acceso al catálogo de ejercicios.
- Diseño adaptable a diferentes tamaños de pantalla.
- Navegación dinámica según el estado de autenticación del usuario.

### 10.2. Usuarios — Autenticación y perfiles

Aplicación encargada de gestionar las cuentas de usuario.

Funcionalidades implementadas:

- Registro de usuarios.
- Inicio de sesión.
- Cierre de sesión.
- Perfil personal.
- Edición de nombre, apellido y correo electrónico.
- Foto de perfil.
- Eliminación de foto de perfil.
- Cambio de contraseña.
- Protección de páginas privadas mediante autenticación.

Se utiliza el sistema de autenticación integrado de Django.

### 10.3. Ejercicios — Catálogo de ejercicios

Aplicación encargada de organizar y mostrar los ejercicios disponibles.

Funcionalidades implementadas:

- Categorías de ejercicios.
- Listado general.
- Filtrado por categoría.
- Página de detalle de cada ejercicio.
- Instrucciones de ejecución.
- Dificultad.
- Duración.
- Imágenes y videos opcionales.
- Administración desde Django Admin.

El catálogo es público, por lo que cualquier visitante puede consultar los ejercicios sin iniciar sesión.

### 10.4. Rutinas — Gestión de rutinas

Aplicación encargada de organizar ejercicios en rutinas.

Funcionalidades implementadas:

- Listado de rutinas disponibles.
- Detalle de cada rutina.
- Asociación de ejercicios a una rutina.
- Orden de los ejercicios.
- Guardado de rutinas por usuario.
- Consulta de rutinas guardadas.
- Protección de las acciones personales mediante autenticación.

Las rutinas disponibles se pueden consultar públicamente. Sin embargo, para guardar rutinas en una cuenta y consultar las rutinas guardadas se requiere iniciar sesión.

La gestión del contenido de las rutinas se realiza mediante Django Admin.

### 10.5. Seguimiento — Progreso del usuario

Aplicación destinada a futuras funcionalidades de seguimiento.

Su objetivo es permitir que los usuarios registren sus actividades y consulten su progreso.

**Estado:** pendiente de implementación.

### 10.6. Principal

Aplicación contemplada dentro de la estructura del proyecto para funcionalidades generales.

**Estado:** pendiente de desarrollo o integración, según las necesidades de las siguientes fases.

---

## 11. Acceso público y acceso privado

El proyecto diferencia las funcionalidades públicas de las personales.

| Funcionalidad | Visitante | Usuario registrado |
|---|---|---|
| Ver página principal | Sí | Sí |
| Consultar ejercicios | Sí | Sí |
| Consultar categorías | Sí | Sí |
| Ver detalles de ejercicios | Sí | Sí |
| Consultar rutinas | Sí | Sí |
| Ver detalles de rutinas | Sí | Sí |
| Guardar rutinas en su cuenta | No | Sí |
| Consultar rutinas guardadas | No | Sí |
| Consultar y editar su perfil | No | Sí |
| Registrar actividades | Pendiente | Pendiente |

Esta separación permite que cualquier persona conozca el contenido del sistema, mientras que las funciones personales quedan protegidas para los usuarios autenticados.

---

## 12. Pruebas y validaciones

Durante el desarrollo se han realizado pruebas para verificar el funcionamiento de las aplicaciones.

Entre las validaciones realizadas se encuentran:

- Comprobación de configuración de Django.
- Pruebas de registro e inicio de sesión.
- Pruebas de cierre de sesión.
- Protección de páginas privadas.
- Pruebas de edición de perfil.
- Pruebas del catálogo público.
- Pruebas de categorías y detalles de ejercicios.
- Pruebas de consulta y guardado de rutinas.
- Verificación de migraciones.
- Pruebas de integración entre aplicaciones.

En la implementación de rutinas se reportaron 71 pruebas aprobadas. En una auditoría anterior de las funcionalidades principales se reportaron 53 pruebas aprobadas.

Para ejecutar todas las pruebas disponibles:

```powershell
python manage.py test
```

---

## 13. Estado actual del desarrollo

El proyecto se está desarrollando por fases para mantener una implementación ordenada y evitar modificar funcionalidades que ya están funcionando.

| Fase | Descripción | Estado |
|---|---|---|
| 1 | Preparación del entorno y creación del proyecto | Completada |
| 2 | Desarrollo de la página principal | Completada |
| 3 | Registro, autenticación y perfiles | Completada |
| 4 | Catálogo de ejercicios | Completada |
| 5 | Gestión de rutinas | Implementada |
| 5.1 | Integración visual de rutinas en navegación y perfil | Pendiente de confirmar |
| 6 | Seguimiento del progreso | Pendiente |
| 7 | Panel personal e historial de actividades | Pendiente |
| 8 | Pruebas generales y preparación de presentación | Pendiente |

---

## 14. Consideraciones importantes

- No eliminar el entorno virtual para intentar solucionar errores de la base de datos.
- No modificar las credenciales de la base de datos sin comprobar primero la configuración existente.
- No ejecutar migraciones innecesarias.
- No modificar modelos o relaciones sin revisar las dependencias de las aplicaciones.
- Mantener separadas las funcionalidades públicas y privadas.
- Los datos personales deben permanecer asociados al usuario correspondiente.
- No subir archivos de configuración con contraseñas, archivos `.env`, bases de datos locales ni el entorno virtual.
- Mantener actualizado `requirements.txt` cuando se agreguen dependencias.
- Realizar pruebas antes de integrar nuevas funcionalidades.

El proyecto se desarrolla de manera incremental, procurando conservar el funcionamiento de los módulos que ya han sido implementados.

---

## 15. Repositorio

**GitHub:** https://github.com/raskcrl/web_ter

---

## 16. Objetivo del proyecto

Desarrollar una plataforma web que facilite la consulta y organización de ejercicios de rehabilitación física desde casa, ofreciendo una experiencia sencilla y accesible.

El sistema busca proporcionar un catálogo organizado de ejercicios, permitir la creación y consulta de rutinas y, posteriormente, incorporar herramientas para registrar actividades y visualizar el progreso personal.

El contenido de rehabilitación y las rutinas deberán ser definidos o revisados por profesionales de la salud. La plataforma funciona como una herramienta de consulta y organización, no como sustituto de una valoración o indicación médica.

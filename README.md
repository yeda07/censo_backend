# Censo Resguardo - desarrollo local

Requiere Python 3.11, Node.js y npm. El backend usa SQLite local por defecto; no necesita acceso a Render.

## Backend (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

La primera vez, `createsuperuser` solicita correo, nombre de usuario y contrasena. El formulario web inicia sesion con el correo. La API queda en `http://127.0.0.1:8000/` y Django Admin en `http://127.0.0.1:8000/admin/`.

Para cambiar la base de datos o configurar despliegue, copie `.env.example` a `.env` y ajuste sus valores. Nunca publique `.env`. En produccion configure `DJANGO_DEBUG=false`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CORS_ALLOWED_ORIGINS` y `DATABASE_URL`.

## Frontend

Abra otra terminal en `../CensoReguardo-Actividades-fronet`:

```powershell
npm install
npm run dev
```

Vite abre `http://localhost:3030/` y usa `http://127.0.0.1:8000` como API por defecto. Para otra API, copie el `.env.example` del frontend a `.env` y cambie `VITE_API_URL`.

Para comprobar los proyectos:

```powershell
.\.venv\Scripts\python manage.py check
.\.venv\Scripts\python manage.py makemigrations --check --dry-run
```

En el frontend, ejecute `npm run build`.

## Autenticacion en dos pasos

En la web, abra el avatar y entre a **Mi perfil** para activar 2FA con una aplicacion TOTP. La activacion exige la contrasena y un codigo del autenticador. Guarde los ocho codigos de recuperacion que se muestran una sola vez; cada uno sirve una sola vez para iniciar sesion o desactivar 2FA. Al activar o desactivar se invalidan los JWT anteriores. El inicio de sesion de Django Admin (`/admin/`) es independiente y no esta cubierto por este 2FA.

## Datos de prueba

Con SQLite vacia, puede cargar tres censos ficticios para recorrer la aplicacion:

```powershell
.\.venv\Scripts\python manage.py cargar_datos_prueba
```

El comando se puede ejecutar de nuevo sin duplicar esos registros. Ana DEMO tiene su actividad realizada, Bruno DEMO tiene una pendiente y Carla DEMO tiene una vencida con multa. Todos los nombres y documentos son ficticios.

Para probar paginacion, filtros, captura familiar, reportes y paz y salvo con mas volumen en SQLite local:

```powershell
.\.venv\Scripts\python manage.py cargar_datos_prueba_ampliados
```

Este comando conserva los datos existentes y agrega 32 familias DEMO (una de 12 integrantes y otra sin censar), 102 personas, censos en dos vigencias, 60 actividades y 90 asignaciones adicionales. Incluye estados realizados, pendientes y vencidos con multa. Es repetible y no crea ni modifica usuarios o contrasenas.

## Actividades y paz y salvo

Una actividad asignada inicia pendiente. La fecha limite cuenta completa: al dia siguiente, si no fue confirmada, pasa a no realizada y genera una multa fija de 100. Confirmarla como realizada, incluso despues del vencimiento, elimina esa multa. El paz y salvo solo se habilita cuando todas las actividades asignadas al censo estan realizadas.

La API actualiza los vencimientos al consultar actividades o el estado del paz y salvo. Para actualizar la base aunque nadie abra la aplicacion, programe este comando una vez al dia, despues de la medianoche de Colombia:

```powershell
.\.venv\Scripts\python manage.py actualizar_actividades
```

Antes de importar datos antiguos, revise las multas historicas: la version anterior podia crearlas mientras la actividad aun estaba pendiente.

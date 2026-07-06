import reflex as rx
import os

# Si la app detecta la variable en la nube, la usa; si no (en tu PC), usa tu Postgres local
database_url = os.environ.get(
    "DATABASE_URL", 
    "postgresql://tu_usuario_local:tu_clave_local@localhost:5432/tu_nombre_db_local"
)

config = rx.Config(
    app_name="tu_app",  # Deja aquí el nombre real que ya tiene tu aplicación
    db_url=database_url,
)
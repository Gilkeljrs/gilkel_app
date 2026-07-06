import reflex as rx
import os


database_url = os.environ.get(
    "DATABASE_URL", 
    "postgresql://tu_usuario_local:tu_clave_local@localhost:5432/tu_nombre_db_local"
)

config = rx.Config(
    app_name="gilkel_app", 
    db_url=database_url,
)
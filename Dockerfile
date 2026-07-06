# Imagen ligera de Python
FROM python:3.11-slim

# Instalar dependencias esenciales del sistema
RUN apt-get update && apt-get install -y \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY . .

# Inicializar configuración básica de Reflex
RUN reflex init

# Exponer el puerto del Backend (la API)
EXPOSE 8000

# Comando para arrancar ÚNICAMENTE el backend de Python en producción
CMD ["reflex", "run", "--backend-only", "--env", "prod"]
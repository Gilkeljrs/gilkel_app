# Usamos una imagen oficial de Python
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias para Node y Reflex
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar el requirements e instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# LIMITAR MEMORIA DE NODE PARA QUE NO META EL BAJÓN EN RENDER
ENV NODE_OPTIONS="--max-old-space-size=256"

# Inicializar y exportar el frontend estático para ahorrar RAM
RUN reflex init
RUN reflex export --frontend-only

# Exponer los puertos que usa Reflex
EXPOSE 8000

# Arrancar solo el backend en producción para que consuma poquita RAM
CMD ["reflex", "run", "--backend-only", "--env", "prod"]
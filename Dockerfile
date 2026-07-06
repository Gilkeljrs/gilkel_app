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

# Inicializar Reflex en modo producción (esto compila el frontend)
RUN reflex init

# Exponer los puertos que usa Reflex (frontend y backend)
EXPOSE 3000
EXPOSE 8000

# Comando para arrancar la app en producción
CMD ["reflex", "run", "--env", "prod"]
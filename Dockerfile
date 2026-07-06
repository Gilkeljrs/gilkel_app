# Usamos una imagen oficial de Python ligera
FROM python:3.11-slim

# Instalar dependencias del sistema indispensables
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar librerías de Python sin guardar basura en cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

# AJUSTES DE MEMORIA ULTRA EXTREMOS PARA PROTEGER LOS 512MB
ENV NODE_OPTIONS="--max-old-space-size=200"
ENV GENERATE_SOURCEMAP=false

# Inicializar Reflex
RUN reflex init

# Exponer los puertos necesarios
EXPOSE 3000
EXPOSE 8000

# Arrancar la app de forma unificada pero ultra optimizada
CMD ["reflex", "run", "--env", "prod"]
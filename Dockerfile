# --- Etapa 1: Compilador (Builder) ---
FROM python:3.9-slim as builder

# 1. Instalar herramientas pesadas necesarias solo para compilar
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libpq-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    libz-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Crear un entorno virtual aislado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Copiar archivo requirements.txt e instalar dependencias con pip (muestra barra de progreso)
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 2: Imagen Final Ligera (Runtime) ---
FROM python:3.9-slim

# 1. Instalar librerías básicas y Chromium para el Scraping
RUN apt-get update && apt-get install -y \
    libgl1 \
    chromium \
    chromium-driver \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiar el entorno virtual ya compilado de la Etapa 1
COPY --from=builder /opt/venv /opt/venv

# 3. Activar el entorno virtual para que FastAPI lo use por defecto
ENV PATH="/opt/venv/bin:$PATH"

# 4. Copiar el código del proyecto
WORKDIR /app
COPY . /app

# 5. Exponer el puerto y arrancar directamente con Uvicorn (más rápido)
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

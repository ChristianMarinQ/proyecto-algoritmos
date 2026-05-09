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
    && rm -rf /var/lib/apt/lists/*

# 2. Crear un entorno virtual aislado
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Instalar dependencias
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv
# Instalar directamente del Pipfile ignorando el lockfile viejo
RUN pipenv install --system --skip-lock

# --- Etapa 2: Imagen Final Ligera (Runtime) ---
FROM python:3.9-slim

# 1. Instalar SÓLO librerías básicas para ejecución (libgl1 es para gráficas)
RUN apt-get update && apt-get install -y \
    libgl1 \
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

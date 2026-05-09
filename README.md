<div align="center">
  <img src="https://img.icons8.com/color/120/000000/graph.png" alt="Logo">
  <h1>📊 BibliometryStats Dashboard</h1>
  <p>Una herramienta avanzada para la extracción, análisis y visualización de datos bibliométricos utilizando algoritmos clásicos e Inteligencia Artificial.</p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Angular-DD0031?style=flat&logo=angular&logoColor=white" alt="Angular">
    <img src="https://img.shields.io/badge/Sentence--BERT-FF9900?style=flat&logo=huggingface&logoColor=white" alt="SBERT">
  </p>
</div>

---

## 🌟 Descripción del Proyecto

Este proyecto es una plataforma integral diseñada para facilitar la investigación científica mediante el análisis bibliométrico automatizado. Permite descargar metadatos de artículos desde bases de datos reconocidas (como IEEE, ScienceDirect y Sage), limpiar los datos y aplicar algoritmos de procesamiento de lenguaje natural (NLP) para descubrir patrones ocultos, similitudes y tendencias.

## ✨ Características Principales

*   🤖 **Data Downloader**: Automatización web (Web Scraping) para descargar metadatos en formato `.bib`.
*   📊 **Visual Analysis**: Mapas de calor geográficos, nubes de palabras dinámicas y líneas temporales de publicación.
*   ☁️ **Word Counting & Networks**: Extracción de palabras clave y descubrimiento de relaciones léxicas.
*   🌲 **Dendrogramas**: Clustering jerárquico de abstracts para evaluar la coherencia temática usando métricas como *Ward*, *Average* y *Complete linkage*.
*   🧠 **Text Similarity**: Comparación profunda de artículos utilizando:
    *   Algoritmos Clásicos: Levenshtein, Jaccard, Coseno TF-IDF, Distancia Euclidiana.
    *   Inteligencia Artificial: Modelos *Sentence-BERT* (all-MiniLM y Multilingual).

## 🚀 Requisitos Previos

Asegúrate de tener instalado en tu sistema:
*   [Python 3.9 o superior](https://www.python.org/downloads/)
*   [Node.js y npm](https://nodejs.org/)
*   [Pipenv](https://pipenv.pypa.io/en/latest/) (Instalable vía `pip install pipenv`)

## 🛠️ Instalación y Ejecución Local

Sigue estos pasos para tener el proyecto corriendo en tu máquina local.

### 1. Clonar el repositorio
```bash
git clone https://github.com/ChristianMarinQ/nombre_de_tu_repositorio.git
cd nombre_de_tu_repositorio
```

### 2. Configurar el Backend (FastAPI)
Abre una terminal en la raíz del proyecto e instala las dependencias de Python:
```bash
# Instalar dependencias usando pipenv
pipenv install

# Activar el entorno virtual e iniciar el servidor local
pipenv run uvicorn main:app --reload
```
La API estará corriendo en `http://localhost:8000`.

### 3. Configurar el Frontend (Angular)
Abre otra terminal, navega a la carpeta del frontend y ejecuta la aplicación:
```bash
cd frontend

# Instalar las dependencias de Node.js
npm install

# Iniciar el servidor de desarrollo de Angular
npm start
```
El panel de control estará disponible en tu navegador en `http://localhost:4200`.

---

## 🏗️ Arquitectura
*   **Backend**: Construido con Python y FastAPI. Utiliza `scikit-learn` para TF-IDF, `sentence-transformers` para IA, y `matplotlib` para la generación de gráficas estáticas.
*   **Frontend**: Aplicación SPA (Single Page Application) construida en Angular 17+ con estilos personalizados Glassmorphism y un diseño responsive.

## 🤝 Creado por
Desarrollado por **[@ChristianMarinQ](https://github.com/ChristianMarinQ)**.

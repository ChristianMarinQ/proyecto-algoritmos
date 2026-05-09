"""
This module generates statistics from the scrapped articles

Top 15 authors

Year distribution

Top 15 journal

Top 15 publisher

"""

import os
import ast
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
from services.statistics.geographical_analysis import generate_geographical_heatmap

def extract_statistics(articles):
    """
    Generates statistics for the scrapped articles and returns paths to the generated files.
    """
    try:
        from wordcloud import WordCloud
    except ImportError:
        WordCloud = None
        
    file_paths = {}

    project_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../images'))
    research_files_dir = os.path.join(project_dir, "statisticsFiles")
    os.makedirs(research_files_dir, exist_ok=True)

    df = pd.DataFrame(articles)
    df['authors'] = df['authors'].apply(safe_parse_authors)
    df['first_author'] = df['authors'].apply(
        lambda x: x[0] if isinstance(x, list) and x else None)

    if 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # 1. Mapa de Calor Geográfico (Req 5.1)
    geo_path = os.path.join(research_files_dir, "heatmap_geografico.png")
    geo_path, geo_counts = generate_geographical_heatmap(articles, geo_path)
    file_paths["heatmap_geografico"] = geo_path
    file_paths["geographical_data"] = geo_counts

    # 2. Nube de palabras dinámica (Req 5.2)
    if WordCloud:
        all_text = " ".join([f"{a.get('abstract', '')} {a.get('keywords', '')}" for a in articles])
        if all_text.strip():
            wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(all_text)
            wc_path = os.path.join(research_files_dir, "wordcloud_dinamica.png")
            wc.to_file(wc_path)
            file_paths["wordcloud_dinamica"] = wc_path

    # 3. Línea temporal por Año y Revista (Req 5.3)
    if 'year' in df.columns and 'journal' in df.columns:
        # Filtrar journals top 5 para no saturar el gráfico
        top_5_journals = df['journal'].value_counts().head(5).index
        timeline_df = df[df['journal'].isin(top_5_journals)]
        timeline_pivot = timeline_df.groupby(['year', 'journal']).size().unstack(fill_value=0)
        
        path_img = os.path.join(research_files_dir, "timeline_journals.png")
        timeline_pivot.plot(kind="line", marker='o', figsize=(10, 6))
        plt.title("Línea Temporal de Publicaciones por Revista")
        plt.xlabel("Año")
        plt.ylabel("Cantidad de Artículos")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(title="Revista", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(path_img)
        plt.close()
        file_paths["timeline_journals"] = path_img

    # Estadísticas originales
    # Top 15 autores
    top_authors = df['first_author'].value_counts().head(15)
    path_img = os.path.join(research_files_dir, "top_15_autores.png")
    top_authors.plot(kind="bar", title="Top 15 Autores (Primer autor)")
    plt.ylabel("Cantidad de productos")
    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    file_paths["top_15_autores"] = path_img

    # Año por tipo
    year_by_type = df.groupby(['ENTRYTYPE', 'year']).size().unstack(fill_value=0)
    path_img = os.path.join(research_files_dir, "publicaciones_por_ano_y_tipo.png")
    year_by_type.T.plot(kind="bar", stacked=True, figsize=(10, 6))
    plt.title("Publicaciones por Año y Tipo de Producto")
    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    file_paths["publicaciones_ano_tipo"] = path_img

    # Cantidad total por tipo
    type_counts = df['ENTRYTYPE'].value_counts()
    path_img = os.path.join(research_files_dir, "cantidad_por_tipo.png")
    type_counts.plot(kind="bar", title="Cantidad por Tipo de Producto", color="skyblue")
    plt.tight_layout()
    plt.savefig(path_img)
    plt.close()
    file_paths["cantidad_tipo"] = path_img

    return file_paths


def safe_parse_authors(value):
    """
    Ensures the string value for authors 
    """
    if isinstance(value, list):
        return value
    try:
        return ast.literal_eval(value)
    except Exception:
        return []

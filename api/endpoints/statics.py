"""
Router for statistics service
"""

from fastapi import APIRouter, HTTPException
from reader_resources.reader_implementation import ReaderImplementation
# Ensure this is a function in statistics.py
from services.statistics.generate_statistics import extract_statistics
from utils.utils import Utils
from services.cache_service import CacheService


router = APIRouter()


@router.get("/")
def get_statistics():
    """
    Returns statistics for research articles
    """
    cached = CacheService.get("statistics")
    if cached:
        return cached

    try:
        reader = ReaderImplementation()
        abstracts = reader.read_bib_files()
        rutas = extract_statistics(abstracts)

        response = {
            "authors": Utils.image_to_base64(rutas["top_15_autores"]),
            "anio": Utils.image_to_base64(rutas["publicaciones_ano_tipo"]),
            "cantidad_tipo": Utils.image_to_base64(rutas["cantidad_tipo"]),
            "heatmap": Utils.image_to_base64(rutas.get("heatmap_geografico")),
            "timeline": Utils.image_to_base64(rutas.get("timeline_journals")),
            "wordcloud": Utils.image_to_base64(rutas.get("wordcloud_dinamica")),
            "geo_data": rutas.get("geographical_data", {})
        }

        CacheService.set("statistics", response)
        return response

    except (IOError, ValueError) as e:
        return HTTPException(status_code=500, detail=str(e))

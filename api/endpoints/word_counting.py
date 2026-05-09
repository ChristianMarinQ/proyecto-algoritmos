"""
Router for word counting an co word network results
"""
import os
from fastapi import APIRouter, HTTPException
from reader_resources.reader_implementation import ReaderImplementation
# Ensure this is a function in statistics.py
from services.word_counting.word_counting import execute_wordcounting
from utils.utils import Utils
from services.cache_service import CacheService


router = APIRouter()


@router.get("/")
def get_statistics():
    """
    Returns results for co-word network
    """
    cached = CacheService.get("word_counting")
    if cached:
        return cached

    try:
        reader = ReaderImplementation()
        abstracts = reader.read_bib_files()
        rutas = execute_wordcounting(abstracts)
        resultados = {}

        for key, path in rutas.items():
            if isinstance(path, str) and os.path.exists(path):
                resultados[key] = {
                    "name": key,
                    "image": Utils.image_to_base64(path)
                }

        response = {
            "response": list(resultados.values()),
            "frequencies": rutas.get("frequencies", []),
            "discovered_terms": rutas.get("discovered_terms", [])
        }

        CacheService.set("word_counting", response)
        return response

    except (IOError, ValueError) as e:
        return HTTPException(status_code=500, detail=str(e))

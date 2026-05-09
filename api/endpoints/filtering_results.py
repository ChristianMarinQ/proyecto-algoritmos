"""
Router for the filtering results
"""

from fastapi import APIRouter, HTTPException
from reader_resources.reader_implementation import ReaderImplementation
from services.cache_service import CacheService


router = APIRouter()


@router.get("/")
def get_filtering_results():
    """
    Returns the filtering results
    """
    cached = CacheService.get("filtering_results")
    if cached:
        return cached

    try:
        reader = ReaderImplementation()
        reader.read_bib_files()
        results = reader.print_results()

        response = {
            "articles":  f"{results['articles']} articles found",
            "journals":  f"{results['journals']} journals found",
            "keywords":  f"{results['keywords']} keywords found",
            "authors":  f"{results['authors']} authors found",
            "reapeated":  f"{results['reapeated']} reapeated found"
        }

        CacheService.set("filtering_results", response)
        return response

    except (IOError, ValueError) as e:
        return HTTPException(status_code=500, detail=str(e))

"""
This module contains all the endpoints for the abstract comparassion
"""
from fastapi import APIRouter, HTTPException
from services.abstractComparasion.text_preprocessing import TextPreprocessing
from services.abstractComparasion.dendrogram_ploting import TextVectorization
from reader_resources.reader_implementation import ReaderImplementation
from utils.utils import Utils
from services.cache_service import CacheService

router = APIRouter()


@router.get("/")
def get_abstracts_comparasion():
    """
    This method returns the results form the abstract comparasion 
    """
    cached = CacheService.get("abstracts_comparasion")
    if cached:
        return cached

    try:
        reader = ReaderImplementation()
        articles = reader.read_bib_files()

        preprocessing = TextPreprocessing()
        for article in articles:
            if 'abstract' in article:
                preprocessing.preprocess_text(
                    article['abstract'], article['title'])
        preprocessed_abstracts = preprocessing.preprocessed_abstracts

        dendrogram = TextVectorization()
        results = dendrogram.transform_text(
            preprocessed_abstracts=preprocessed_abstracts)

        response = {
            "ward": Utils.image_to_base64(results["ward_dendogram"]),
            "average": Utils.image_to_base64(results["average_dendogram"]),
            "complete": Utils.image_to_base64(results["complete_dendogram"]),
            "metrics": results["metrics"]
        }

        CacheService.set("abstracts_comparasion", response)
        return response

    except (IOError, ValueError) as e:
        return HTTPException(status_code=500, detail=str(e))

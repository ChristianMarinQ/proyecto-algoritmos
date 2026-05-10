from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.text_similarity.similarity_algorithms import calculate_similarities
from reader_resources.reader_implementation import ReaderImplementation

router = APIRouter()

from typing import List

class SimilarityRequest(BaseModel):
    article_ids: List[str]

@router.get("/articles")
def get_articles_list():
    try:
        reader = ReaderImplementation()
        articles = reader.read_bib_files()
        
        # Retorna solo titulos y IDs de articulos que tengan abstract
        response = []
        for i, art in enumerate(articles):
            if 'abstract' in art:
                response.append({
                    "id": art.get("ID", str(i)), 
                    "title": art.get("title", f"Artículo Sin Título {i}")
                })
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
def compare_articles(request: SimilarityRequest):
    try:
        reader = ReaderImplementation()
        articles = reader.read_bib_files()
        
        if len(request.article_ids) < 2:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos 2 artículos para comparar")
            
        selected_articles = []
        for a_id in request.article_ids:
            art = next((a for i, a in enumerate(articles) if a.get("ID", str(i)) == a_id), None)
            if not art:
                raise HTTPException(status_code=404, detail=f"Artículo no encontrado")
            if not art.get("abstract"):
                raise HTTPException(status_code=400, detail=f"El artículo '{art.get('title', 'Sin título')}' no tiene abstract")
            selected_articles.append(art)
            
        abstracts = [art.get("abstract") for art in selected_articles]
        titles = [art.get("title") for art in selected_articles]
        
        results_data = calculate_similarities(abstracts)
        results = results_data["results"]
        visualizations = results_data["visualizations"]
        
        from utils.utils import Utils
        response = {
            "articles": titles,
            "results": results,
            "visualizations": {
                "performance_chart": Utils.image_to_base64(visualizations.get("performance_chart")),
                "ranking_chart": Utils.image_to_base64(visualizations.get("ranking_chart"))
            }
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

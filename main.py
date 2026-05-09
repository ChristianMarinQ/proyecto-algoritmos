"""
  Main module of the project
"""
# Fix: pyparsing 3.x renamed DelimitedList to delimitedList
# bibtexparser 1.4.x expects the old name
import pyparsing
if not hasattr(pyparsing, 'DelimitedList'):
    pyparsing.DelimitedList = pyparsing.delimitedList

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import statics
from api.endpoints import abstracts_comparasion
from api.endpoints import word_counting
from api.endpoints import filtering_results
from api.endpoints import text_similarity
from api.endpoints import downloader


app = FastAPI(title="Proyecto Final Análisis de algoritmos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    statics.router, prefix="/articlesStatistics",
    tags=["Statistics (Requirement 2)"])

app.include_router(
    word_counting.router, prefix="/wordCounting",
    tags=["Co-word netword and wordclouds  (Requirement 3)"])

app.include_router(
    abstracts_comparasion.router, prefix="/abstractComparasion",
    tags=["Abstracts Comparasion (Requirement 5)"])

app.include_router(
    filtering_results.router, prefix="/filteringResults",
    tags=["Filtering results"])

app.include_router(
    text_similarity.router, prefix="/textSimilarity",
    tags=["Text Similarity (Requirement 6)"])

app.include_router(downloader.router, prefix='/downloader', tags=['Downloader (Requirement 1)'])

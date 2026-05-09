from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from scrappers.ScienceScrapper import ScienceScraper
from scrappers.iee_scrapper import IeeeScrapper
from scrappers.sage_scrapper import SageScraper
from reader_resources.reader_implementation import ReaderImplementation
import time
import os

router = APIRouter()

class DownloadRequest(BaseModel):
    email: str
    password: str
    query: str
    limit: int
    database: str

def run_scraping_job(req: DownloadRequest):
    print(f"Starting scraping job for {req.database} with query '{req.query}'")
    
    # Kill ghost chromedriver processes on Windows to prevent WinError 183/32
    if os.name == 'nt':
        os.system("taskkill /f /im chromedriver.exe /T >nul 2>&1")
        os.system("taskkill /f /im undetected_chromedriver.exe /T >nul 2>&1")
        time.sleep(1)
    
    # 1. Run the selected scraper
    try:
        if req.database == "science_direct" or req.database == "all":
            scraper = ScienceScraper(req.email, req.password, req.query, req.limit)
            scraper.run()
            
        if req.database == "ieee" or req.database == "all":
            scraper = IeeeScrapper(req.email, req.password, req.query, req.limit)
            scraper.run()
            
        if req.database == "sage" or req.database == "all":
            scraper = SageScraper(req.email, req.password, req.query, req.limit)
            scraper.run()
    except Exception as e:
        print(f"Error during scraping: {e}")
        # Note: We continue to ReaderImplementation even if scraping failed to process what we already have

    # 2. Automatically Run the Reader Implementation to unify and filter
    print("Running ReaderImplementation to unify and deduplicate articles...")
    try:
        reader = ReaderImplementation()
        reader.read_bib_files()
        print("ReaderImplementation finished successfully.")
    except Exception as e:
        print(f"Error during ReaderImplementation: {e}")

@router.post("/run")
def start_downloader(request: DownloadRequest, background_tasks: BackgroundTasks):
    # Validaciones
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="El correo y la contraseña son requeridos.")
    if not request.query:
        raise HTTPException(status_code=400, detail="Debe ingresar una palabra clave para buscar.")
    
    # Send to background task so the frontend doesn't hang (scraping takes several minutes)
    background_tasks.add_task(run_scraping_job, request)
    
    return {"message": "El proceso de descarga y unificación ha iniciado en segundo plano. Esto puede tomar varios minutos."}

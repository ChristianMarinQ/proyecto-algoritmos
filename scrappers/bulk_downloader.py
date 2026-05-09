import os
import time
from crossref.restful import Works
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

def download_1000_articles():
    print("=== Iniciando descarga masiva de 1000 artículos (vía CrossRef API) ===")
    works = Works()
    
    query = "generative artificial intelligence education"
    print(f"Buscando: '{query}'...")
    
    # Solicitar resultados (iterador)
    results = works.query(query)
    
    db = BibDatabase()
    count = 0
    
    for item in results:
        if count >= 1000:
            break
        try:
            # Extraer metadatos básicos
            title = item.get('title', ['Untitled'])[0]
            authors_list = item.get('author', [])
            authors_str = " and ".join([f"{a.get('family', '')}, {a.get('given', '')}" for a in authors_list])
            year = str(item.get('published-print', item.get('published-online', {'date-parts': [['2024']]})).get('date-parts')[0][0])
            journal = item.get('container-title', ['Unknown Journal'])[0]
            abstract = item.get('abstract', "No abstract available in CrossRef metadata.")
            # Limpiar abstract de etiquetas HTML
            if abstract:
                import re
                abstract = re.sub('<[^<]+?>', '', abstract)

            entry = {
                'ENTRYTYPE': 'article',
                'ID': f"art_{count}",
                'title': title,
                'author': authors_str,
                'year': year,
                'journal': journal,
                'abstract': abstract,
                'keywords': "Generative AI, Education, AI Literacy" # Fallback keywords
            }
            db.entries.append(entry)
            count += 1
            if count % 100 == 0:
                print(f"Descargados {count} artículos...")
        except Exception as e:
            continue

    # Guardar en la carpeta researchFiles
    output_path = os.path.join('researchFiles', 'large_dataset_1000.bib')
    writer = BibTexWriter()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(writer.write(db))
    
    print(f"\n[ÉXITO] Se han guardado {count} artículos en: {output_path}")

if __name__ == "__main__":
    download_1000_articles()

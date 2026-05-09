import time
import os
import math
import numpy as np
from collections import Counter
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

try:
    from Levenshtein import distance as lev_distance
except ImportError:
    def lev_distance(s1, s2):
        if len(s1) < len(s2): return lev_distance(s2, s1)
        if len(s2) == 0: return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- IA MODELS LOAD ---
st_model = None
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity as st_cosine
    st_model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error cargando SBERT: {e}")

st_model2 = None
try:
    from sentence_transformers import SentenceTransformer
    st_model2 = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
except Exception as e:
    print(f"Error cargando SBERT multilingüe: {e}")


# --- AUX FUNCTIONS ---
def get_jaccard_sim(str1, str2):
    a = set(str1.lower().split())
    b = set(str2.lower().split())
    c = a.intersection(b)
    if not a and not b: return 1.0
    return float(len(c)) / (len(a.union(b)))

def get_euclidean_distance(str1, str2):
    vectorizer = TfidfVectorizer()
    try:
        vec = vectorizer.fit_transform([str1, str2]).toarray()
        return np.linalg.norm(vec[0] - vec[1])
    except:
        return 1.414

# --- MAIN ANALYSIS FUNCTION ---
def calculate_similarities(abstracts):
    if len(abstracts) < 2:
        return {"results": [], "visualizations": {}}

    pairs = list(combinations(abstracts, 2))
    num_pairs = len(pairs)

    # Acumulators with metadata
    algorithms_data = {
        "levenshtein": {"total_score": 0.0, "time": 0.0, "complexity": "O(n·m)", "type": "Clásico (Edición)"},
        "jaccard":     {"total_score": 0.0, "time": 0.0, "complexity": "O(n+m)", "type": "Clásico (Conjuntos)"},
        "cosine":      {"total_score": 0.0, "time": 0.0, "complexity": "O(n)",   "type": "Clásico (Vectorial)"},
        "euclidean":   {"total_score": 0.0, "time": 0.0, "complexity": "O(n)",   "type": "Clásico (Vectorial)"},
        "sbert":       {"total_score": 0.0, "time": 0.0, "complexity": "O(n²)",  "type": "Inteligencia Artificial"},
        "sbert_multi": {"total_score": 0.0, "time": 0.0, "complexity": "O(n²)",  "type": "Inteligencia Artificial"},
        "ngram":       {"total_score": 0.0, "time": 0.0, "complexity": "O(n)",   "type": "Inteligencia Artificial"},
    }

    vectorizer = TfidfVectorizer()

    for text1, text2 in pairs:
        # 1. Levenshtein
        t0 = time.perf_counter()
        lev = lev_distance(text1, text2)
        max_len = max(len(text1), len(text2), 1)
        algorithms_data["levenshtein"]["total_score"] += float((1 - lev / max_len) * 100)
        algorithms_data["levenshtein"]["time"] += (time.perf_counter() - t0) * 1000

        # 2. Jaccard
        t0 = time.perf_counter()
        algorithms_data["jaccard"]["total_score"] += float(get_jaccard_sim(text1, text2) * 100)
        algorithms_data["jaccard"]["time"] += (time.perf_counter() - t0) * 1000

        # 3. Cosine TF-IDF
        t0 = time.perf_counter()
        try:
            tfidf = vectorizer.fit_transform([text1, text2])
            algorithms_data["cosine"]["total_score"] += float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0] * 100)
        except:
            pass
        algorithms_data["cosine"]["time"] += (time.perf_counter() - t0) * 1000

        # 4. Euclidean
        t0 = time.perf_counter()
        euc = get_euclidean_distance(text1, text2)
        algorithms_data["euclidean"]["total_score"] += float(max(0, (1 - euc / 1.415) * 100))
        algorithms_data["euclidean"]["time"] += (time.perf_counter() - t0) * 1000

        # 5. Sentence-BERT
        if st_model:
            t0 = time.perf_counter()
            try:
                emb1 = st_model.encode([text1])
                emb2 = st_model.encode([text2])
                algorithms_data["sbert"]["total_score"] += float(cosine_similarity(emb1, emb2)[0][0] * 100)
            except:
                pass
            algorithms_data["sbert"]["time"] += (time.perf_counter() - t0) * 1000

        # 6. SBERT Multilingual or N-Gram fallback
        if st_model2:
            t0 = time.perf_counter()
            try:
                emb1 = st_model2.encode([text1])
                emb2 = st_model2.encode([text2])
                algorithms_data["sbert_multi"]["total_score"] += float(cosine_similarity(emb1, emb2)[0][0] * 100)
            except:
                pass
            algorithms_data["sbert_multi"]["time"] += (time.perf_counter() - t0) * 1000
        else:
            t0 = time.perf_counter()
            def char_ngrams(text, n=3):
                return set(text[i:i+n] for i in range(len(text) - n + 1))
            n1 = char_ngrams(text1)
            n2 = char_ngrams(text2)
            inter = n1.intersection(n2)
            union = n1.union(n2)
            algorithms_data["ngram"]["total_score"] += (len(inter) / len(union) * 100) if union else 0
            algorithms_data["ngram"]["time"] += (time.perf_counter() - t0) * 1000

    # Build final results — always include classical algorithms
    final_results = []

    def add_res(key, name, explanation, formula):
        data = algorithms_data[key]
        final_results.append({
            "name": name,
            "type": data["type"],
            "score": round(data["total_score"] / num_pairs, 2),
            "execution_time": round(data["time"] / num_pairs, 4),
            "complexity": data["complexity"],
            "explanation": explanation,
            "formula": formula
        })

    add_res("levenshtein", "Distancia de Levenshtein",
            f"Evalúa el promedio del número mínimo de ediciones letra por letra para todos los pares de los {len(abstracts)} artículos.",
            "1 - [ Lev(A, B) / max(|A|, |B|) ]")
    add_res("jaccard", "Similitud de Jaccard",
            f"Evalúa la proporción promedio de palabras únicas compartidas entre todas las combinaciones de los {len(abstracts)} artículos.",
            "|A ∩ B| / |A ∪ B|")
    add_res("cosine", "Similitud del Coseno (TF-IDF)",
            f"Evalúa el promedio angular (frecuencia de palabras) entre los pares posibles del grupo de artículos.",
            "(A · B) / (||A|| × ||B||)")
    add_res("euclidean", "Distancia Euclidiana",
            f"Evalúa la distancia física promedio 'en línea recta' de las coordenadas espaciales del texto del grupo.",
            "1 - [ ||A - B|| / max_dist ]")

    if st_model:
        add_res("sbert", "Sentence-BERT (all-MiniLM)",
                f"Modelo de IA que evalúa el promedio de similitud semántica profunda entre todos los {len(abstracts)} artículos.",
                "(E(A) · E(B)) / (||E(A)|| × ||E(B)||)\nDonde E = Representación Vectorial (Encoding)")

    if st_model2:
        add_res("sbert_multi", "SBERT (Multilingual)",
                f"Modelo de IA multilingüe que evalúa el promedio del significado semántico del grupo completo.",
                "(M(A) · M(B)) / (||M(A)|| × ||M(B)||)\nDonde M = Modelo Multilingüe")
    else:
        add_res("ngram", "Análisis Semántico N-Gram",
                f"Evalúa coincidencias promedio de sub-estructuras (n-gramas) en todo el grupo de artículos seleccionados.",
                "|ngrams(A) ∩ ngrams(B)| / |ngrams(A) ∪ ngrams(B)|")

    # Generate visualizations
    try:
        visuals = generate_visualizations(final_results)
    except Exception as e:
        print(f"Error generando visualizaciones: {e}")
        visuals = {}

    return {"results": final_results, "visualizations": visuals}


def generate_visualizations(results):
    """Genera gráficas de rendimiento y ranking."""
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../images'))
    sim_dir = os.path.join(project_dir, "text_similarity")
    os.makedirs(sim_dir, exist_ok=True)
    print(f"Guardando imágenes en: {sim_dir}")

    names = [r["name"].split('(')[0].strip() for r in results]
    times = [r["execution_time"] for r in results]

    # --- 1. Gráfica de Rendimiento ---
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#4F46E5' if 'IA' not in r["type"] else '#7C3AED' for r in results]
    bars = ax.barh(names, times, color=colors, edgecolor='none')
    ax.set_xlabel('Tiempo promedio por par (ms)', fontsize=11)
    ax.set_title('Comparativa de Rendimiento (Tiempo de Ejecución)', fontsize=13, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#1e293b')
    ax.tick_params(colors='white')
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('rgba(255,255,255,0.1)')

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.001, bar.get_y() + bar.get_height() / 2,
                f' {width:.3f}ms', va='center', color='white', fontsize=9)

    plt.tight_layout()
    perf_path = os.path.join(sim_dir, "performance_comparison.png")
    plt.savefig(perf_path, dpi=100, bbox_inches='tight')
    plt.close()

    # --- 2. Ranking: Rápido vs Preciso ---
    accuracy_map = {
        "Sentence-BERT": 95,
        "SBERT": 98,
        "Análisis Semántico N-Gram": 75,
        "Similitud del Coseno": 70,
        "Similitud de Jaccard": 60,
        "Distancia de Levenshtein": 40,
        "Distancia Euclidiana": 50,
    }
    acc_scores = []
    for r in results:
        val = 30
        for key, score in accuracy_map.items():
            if key in r["name"]:
                val = score
                break
        acc_scores.append(val)

    time_arr = np.array(times, dtype=float)
    time_scores = 1.0 / (time_arr + 0.001)
    if time_scores.max() > 0:
        time_scores = (time_scores / time_scores.max()) * 100

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor('#0f172a')
    fig.patch.set_facecolor('#1e293b')

    ax.scatter(time_scores, acc_scores, s=150, color='#a78bfa', alpha=0.9, zorder=3)
    for i, name in enumerate(names):
        ax.annotate(name, (time_scores[i], acc_scores[i]),
                    xytext=(6, 6), textcoords='offset points',
                    color='white', fontsize=8)

    ax.set_xlabel('Velocidad (Normalizada 0-100)', color='white', fontsize=11)
    ax.set_ylabel('Profundidad Semántica', color='white', fontsize=11)
    ax.set_title('Ranking: Más Rápido vs Más Preciso', color='white', fontsize=13, fontweight='bold')
    ax.tick_params(colors='white')
    ax.grid(True, linestyle=':', alpha=0.3, color='white')
    ax.set_xlim(-5, 110)
    ax.set_ylim(0, 110)

    plt.tight_layout()
    ranking_path = os.path.join(sim_dir, "ranking_fast_precise.png")
    plt.savefig(ranking_path, dpi=100, bbox_inches='tight')
    plt.close()

    return {
        "performance_chart": perf_path,
        "ranking_chart": ranking_path,
    }

"""
This module is used to vectorize, 
calculate matrix length, hierarchical clustering 
and dendrogram ploting
"""
import os
from scipy.cluster.hierarchy import dendrogram, linkage, cophenet
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


class TextVectorization:
    """
    Class used to vectorize, 
    calculate matrix length and hierarchical clustering
    """

    def __init__(self):
        pass

    def transform_text(self, preprocessed_abstracts):
        """
        Method used to vectorize, calculate matrix length, hierarchical clustering 
        """
        texts = list(preprocessed_abstracts.values())
        titles = list(preprocessed_abstracts.keys())
        
        if not texts:
            return {}

        vectorizer = TfidfVectorizer()
        x = vectorizer.fit_transform(texts)
        distances = pdist(x.toarray(), metric='euclidean')

        # Algoritmos de clustering (3 algoritmos requeridos)
        z_ward = linkage(distances, method='ward')
        z_average = linkage(distances, method='average')
        z_complete = linkage(distances, method='complete')

        # Cálculo de Coherencia (Cophenetic Correlation Coefficient)
        c_ward, _ = cophenet(z_ward, distances)
        c_average, _ = cophenet(z_average, distances)
        c_complete, _ = cophenet(z_complete, distances)

        metrics = {
            "ward": round(c_ward, 4),
            "average": round(c_average, 4),
            "complete": round(c_complete, 4)
        }

        # Determinar el mejor basado en la correlación cofenética
        best = max(metrics, key=metrics.get)
        metrics["best_algorithm"] = best

        return self.plot_dendogram(z_ward, z_average, z_complete, titles, metrics)

    def plot_dendogram(self, z_ward, z_average, z_complete, titles, metrics):
        """
        Method used to plot a dendrogram
        """
        results = {"metrics": metrics}

        project_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../images'))
        research_files_dir = os.path.join(project_dir, "abstracts_dendograms")
        os.makedirs(research_files_dir, exist_ok=True)

        # Helper para guardar plots
        def save_plot(z, title, filename):
            plt.figure(figsize=(12, 7))
            dendrogram(z, labels=titles, leaf_rotation=90, leaf_font_size=8)
            plt.title(f"Dendrograma - {title} (Coeficiente: {metrics[title.lower()]})")
            plt.tight_layout()
            path = os.path.join(research_files_dir, filename)
            plt.savefig(path)
            plt.close()
            return path

        results["ward_dendogram"] = save_plot(z_ward, "Ward", "ward_dendogram.png")
        results["average_dendogram"] = save_plot(z_average, "Average", "average_dendogram.png")
        results["complete_dendogram"] = save_plot(z_complete, "Complete", "complete_dendogram.png")

        return results


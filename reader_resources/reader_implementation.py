"""
  This module uses python bibtexparser for the bib files handle
"""

import os
import glob
import re
import uuid
import pyparsing
if not hasattr(pyparsing, 'DelimitedList') and hasattr(pyparsing, 'delimitedList'):
    pyparsing.DelimitedList = pyparsing.delimitedList
import bibtexparser as bib
import hashlib
from reader_resources.create_output_files import OutputFiles
# from reader_resources.abstract_processing import AbstractProcessing


class ReaderImplementation:
    """
      This class is in charge of reading the bib files
    """

    def __init__(self):
        self.bib_files = []
        self.titles = []
        self.authors = []
        self.journals = []
        self.keywords = []
        self.articles = []
        self.abstracts_words = []
        self.repeated_articles = []

    def list_bib_files(self, directory='researchFiles'):
        """
        Lists all .bib files in the specified directory

        Args:
            directory (str): The directory to search in, default is 'researchFiles'

        Returns:
            list: A list of paths to .bib files
        """
        # Get the absolute path of the project directory
        project_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))

        # Create the path to the researchFiles directory
        research_files_dir = os.path.join(project_dir, directory)

        # Check if directory exists
        if not os.path.isdir(research_files_dir):
            raise FileNotFoundError(
                f"Directory {research_files_dir} not found")

        # Find all .bib and .bibtex files in the directory
        bib_file_paths = glob.glob(os.path.join(research_files_dir, '*.bib'))
        bib_file_paths += glob.glob(os.path.join(research_files_dir, '*.bibtex'))
        self.bib_files = bib_file_paths

    def read_bib_files(self):
        """
        Reads each of the bib files indentified in the list_bib_files method
        """
        self.list_bib_files()

        for file in self.bib_files:

            with open(file, encoding='utf-8') as bib_file:
                library = bib.load(bib_file)
            file_entries = library.entries

            for entry in file_entries:
                # One entry equals one article
                # Separates and filters every entry from the article
                self.separate_entry_keys(entry)

        return self.articles

        # PLOT AND OUTPUT FILE GENERATION
        # self.print_results()    # Prints the filter results
        # self.generate_output_files()  # Generates the output files
        # self.plot_results()     # Generates a bar graph for the execution results
        # self.process_abstracts()
        # generate_statistics(self.articles)
        # self.preprocess_abstracts()

    def separate_entry_keys(self, entry):
        """
        Separates the key of a bib entry
        """
        try:
            # Extract title and generate stable ID
            title = entry.get('title', 'Untitled Article')
            article = {
                "ENTRYTYPE": "Filtered Article",
                "title": title,
                "ID": hashlib.md5(title.encode('utf-8')).hexdigest()
            }

            # Extract authors if present
            if 'author' in entry:
                # Split authors by 'and' and strip whitespace
                authors = [author.strip()
                           for author in re.split(' and |,', entry['author'])]
                article['authors'] = str(authors)
                self.inject_authors(authors)  # Injected to plotter

            if 'title' in entry:
                self.inject_titles(title)

            if 'journal' in entry or 'publisher' in entry:
                journal = entry['journal'] if 'journal' in entry else entry['publisher']
                article['journal'] = journal
                self.inject_journals(journal)  # Injected to plotter

            if 'keywords' in entry:
                keywords = [keyword.strip()
                            for keyword in re.split(',', entry['keywords'])]
                article['keywords'] = str(keywords)
                self.inject_keywords(keywords)  # Injected to plotter

            if 'year' in entry:
                year = entry['year']
                article['year'] = year

            if 'abstract' in entry:
                abstract_text = entry['abstract']
                article['abstract'] = abstract_text

            # Prevents a duplicated article
            if self.verify_article_exists(article['title'], article.get('abstract', '')):
                self.repeated_articles.append(article)
            else:
                self.articles.append(article)
        except (KeyError, ValueError, IOError) as e:
            print(f"An article was not processed due to error: {e}")

    def verify_article_exists(self, title, abstract=""):
        """
        Verifies if an article exists in the list of articles
        using a normalized title and optionally the first 15 words of the abstract.
        """
        # Normalizar el título actual
        title_clean = "".join(char for char in title.lower() if char.isalnum())
        
        # Limpiar y extraer las primeras 15 palabras del abstract
        abstract_clean = abstract.strip() if abstract else ""
        words = [w for w in abstract_clean.lower().split() if w.isalnum()]
        abstract_prefix = " ".join(words[:15])

        for article in self.articles:
            # Normalizar el título del artículo ya existente
            existing_title_clean = "".join(char for char in article['title'].lower() if char.isalnum())
            
            if existing_title_clean == title_clean:
                existing_abstract = article.get('abstract', '').strip()
                
                # Si ambos tienen abstracts no vacíos, comparamos las primeras 15 palabras
                if abstract_prefix and existing_abstract:
                    existing_words = [w for w in existing_abstract.lower().split() if w.isalnum()]
                    existing_prefix = " ".join(existing_words[:15])
                    
                    if existing_prefix == abstract_prefix:
                        return True
                else:
                    # Si no hay abstract, confiamos en el título normalizado
                    return True
        return False

    def inject_keywords(self, keywords):
        """
        Injects keywords into the articles
        """
        for keyword in keywords:
            if keyword not in self.keywords:
                self.keywords.append(keyword.strip())

    def inject_titles(self, title):
        """
        Injects titles into the articles
        """
        if title not in self.titles:
            self.titles.append(title.strip())

    def inject_authors(self, authors):
        """
        Injects authors into the articles
        """
        for author in authors:
            if author not in self.authors:
                self.authors.append(author.strip())

    def inject_journals(self, journal):
        """
        Injects journals into the articles
        """
        if journal not in self.journals:
            self.journals.append(journal)


    def generate_output_files(self):
        """
        Generates the output files
        1 bib file for filtered articles
        1 bib file for the repeated files
        """
        OutputFiles.create_output_file(self.articles, "filtered_articles")
        OutputFiles.create_output_file(
            self.repeated_articles, "repeated_articles")
        print("Output files created")

    # def process_abstracts(self):
    #     "Process an plots the abstract words"
    #     abstract = AbstractProcessing()
    #     abstract.filter_keywords(self.abstracts_words)

    def print_results(self):
        """
        Prints the obtained results
        """
        results = {}
        print(len(self.titles), " Titles Filtered")

        print(len(self.articles), " Articles Filtered")
        results["articles"] = len(self.articles)

        print(len(self.journals), " Journals Filtered")
        results["journals"] = len(self.journals)

        print(len(self.keywords), " Keywords Filtered")
        results["keywords"] = len(self.keywords)

        print(len(self.authors), " Authors Filtered")
        results["authors"] = len(self.authors)

        print(len(self.repeated_articles), " Repeated Articles")
        results["reapeated"] = len(self.repeated_articles)

        return results

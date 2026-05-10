import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getStatistics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/articlesStatistics/`);
  }

  getWordCounting(): Observable<any> {
    return this.http.get(`${this.baseUrl}/wordCounting/`);
  }

  getAbstractsComparison(): Observable<any> {
    return this.http.get(`${this.baseUrl}/abstractComparasion/`);
  }

  getFilteringResults(): Observable<any> {
    return this.http.get(`${this.baseUrl}/filteringResults/`);
  }

  getArticlesList(): Observable<any> {
    return this.http.get(`${this.baseUrl}/textSimilarity/articles`);
  }

  compareArticles(article_ids: string[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/textSimilarity/compare`, { article_ids });
  }

  runScraping(config: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/downloader/run`, config);
  }
}

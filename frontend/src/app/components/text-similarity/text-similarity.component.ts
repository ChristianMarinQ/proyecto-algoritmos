import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../api.service';

@Component({
  selector: 'app-text-similarity',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './text-similarity.component.html',
  styleUrls: ['./text-similarity.component.css']
})
export class TextSimilarityComponent implements OnInit {
  articles: any[] = [];
  selectedArticles: string[] = ['', ''];
  
  isLoading = false;
  results: any = null;
  errorMsg: string = '';

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getArticlesList().subscribe({
      next: (res: any) => {
        this.articles = res;
      },
      error: (err: any) => {
        console.error(err);
      }
    });
  }

  addArticle() {
    this.selectedArticles.push('');
  }

  removeArticle(index: number) {
    if (this.selectedArticles.length > 2) {
      this.selectedArticles.splice(index, 1);
    }
  }

  compare() {
    const validArticles = this.selectedArticles.filter(id => id && id.trim() !== '');
    
    if (validArticles.length < 2) {
      this.errorMsg = "Por favor selecciona al menos dos artículos.";
      return;
    }
    
    const uniqueArticles = new Set(validArticles);
    if (uniqueArticles.size !== validArticles.length) {
      this.errorMsg = "Por favor selecciona artículos diferentes. No pueden haber repetidos.";
      return;
    }

    this.errorMsg = '';
    this.isLoading = true;
    this.results = null;

    this.apiService.compareArticles(validArticles).subscribe({
      next: (res: any) => {
        this.results = res;
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error(err);
        this.errorMsg = "Hubo un error al comparar los artículos.";
        this.isLoading = false;
      }
    });
  }
}

import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-word-counting',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './word-counting.component.html',
  styleUrl: './word-counting.component.css'
})
export class WordCountingComponent implements OnInit {
  isLoading = true;
  data: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getWordCounting().subscribe({
      next: (res) => {
        this.data = res;
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.isLoading = false;
      }
    });
  }
}

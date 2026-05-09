import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-filtering-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './filtering-results.component.html',
  styleUrl: './filtering-results.component.css'
})
export class FilteringResultsComponent implements OnInit {
  isLoading = true;
  data: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getFilteringResults().subscribe({
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

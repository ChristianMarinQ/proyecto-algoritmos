import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-abstract-comparasion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './abstract-comparasion.component.html',
  styleUrl: './abstract-comparasion.component.css'
})
export class AbstractComparasionComponent implements OnInit {
  isLoading = true;
  data: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getAbstractsComparison().subscribe({
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

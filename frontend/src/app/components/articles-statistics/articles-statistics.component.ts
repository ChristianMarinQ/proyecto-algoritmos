import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

@Component({
  selector: 'app-articles-statistics',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './articles-statistics.component.html',
  styleUrl: './articles-statistics.component.css'
})
export class ArticlesStatisticsComponent implements OnInit {
  isLoading = true;
  data: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getStatistics().subscribe({
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

  exportToPDF() {
    const data = document.getElementById('export-content');
    if (!data) return;

    html2canvas(data, { 
      scale: 2,
      backgroundColor: '#0f172a',
      useCORS: true 
    }).then(canvas => {
      const imgWidth = 208;
      const pageHeight = 295;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      const contentDataURL = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      let position = 0;

      pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight; // Error corregido aquí en la lógica de paginación
        pdf.addPage();
        pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }
      pdf.save('Reporte_Bibliometrico.pdf');
    });
  }
}

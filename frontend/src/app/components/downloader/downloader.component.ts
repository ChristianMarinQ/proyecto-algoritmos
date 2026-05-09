import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../api.service';

@Component({
  selector: 'app-downloader',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './downloader.component.html',
  styleUrls: ['./downloader.component.css']
})
export class DownloaderComponent {
  formData = {
    email: '',
    password: '',
    query: '',
    limit: 100,
    database: 'all'
  };

  isLoading = false;
  statusMessage = '';
  isError = false;

  constructor(private apiService: ApiService) {}

  onSubmit() {
    if (!this.formData.email || !this.formData.password || !this.formData.query || !this.formData.limit) {
      this.isError = true;
      this.statusMessage = 'Por favor, llena todos los campos del formulario antes de continuar.';
      return;
    }

    this.isLoading = true;
    this.statusMessage = '';
    this.isError = false;

    this.apiService.runScraping(this.formData).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.isError = false;
        this.statusMessage = res.message || 'El proceso se ha iniciado exitosamente en el servidor. Puede tardar varios minutos en completarse.';
      },
      error: (err: any) => {
        this.isLoading = false;
        this.isError = true;
        this.statusMessage = err.error?.detail || 'Ha ocurrido un error al intentar iniciar el proceso de descarga.';
        console.error(err);
      }
    });
  }
}

import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { ArticlesStatisticsComponent } from './components/articles-statistics/articles-statistics.component';
import { WordCountingComponent } from './components/word-counting/word-counting.component';
import { AbstractComparasionComponent } from './components/abstract-comparasion/abstract-comparasion.component';
import { FilteringResultsComponent } from './components/filtering-results/filtering-results.component';
import { TextSimilarityComponent } from './components/text-similarity/text-similarity.component';
import { DownloaderComponent } from './components/downloader/downloader.component';

export const routes: Routes = [
  { path: '', redirectTo: 'filtering', pathMatch: 'full' },
  { path: 'filtering', component: FilteringResultsComponent },
  { path: 'statistics', component: ArticlesStatisticsComponent },
  { path: 'words', component: WordCountingComponent },
  { path: 'dendrograms', component: AbstractComparasionComponent },
  { path: 'similarity', component: TextSimilarityComponent },
  { path: 'downloader', component: DownloaderComponent },
  { path: '**', redirectTo: 'filtering' }
];

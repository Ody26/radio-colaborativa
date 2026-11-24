import type { Routes } from '@angular/router';

import { sesionSalaGuard } from './core/sesion/sesion-sala.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/inicio/inicio.page').then((m) => m.InicioPage),
  },
  {
    path: 'unirse/:codigo',
    loadComponent: () => import('./pages/unirse/unirse.page').then((m) => m.UnirsePage),
  },
  {
    path: 'sala/:codigo',
    canActivate: [sesionSalaGuard],
    loadComponent: () => import('./pages/sala/sala.page').then((m) => m.SalaPage),
  },
  {
    path: '**',
    redirectTo: '',
  },
];

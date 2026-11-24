import { inject } from '@angular/core';
import type { CanActivateFn } from '@angular/router';
import { Router } from '@angular/router';

import { SesionService } from './sesion.service';

export const sesionSalaGuard: CanActivateFn = (ruta) => {
  const codigo = (ruta.paramMap.get('codigo') ?? '').toUpperCase();
  const sesion = inject(SesionService);
  const router = inject(Router);
  return sesion.tieneSesionPara(codigo) || router.createUrlTree(['/unirse', codigo]);
};

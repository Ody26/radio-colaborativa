import type { HttpInterceptorFn } from '@angular/common/http';
import { HttpErrorResponse, HttpStatusCode } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';

import { SesionService } from '../sesion/sesion.service';

export const autenticacionInterceptor: HttpInterceptorFn = (peticion, siguiente) => {
  const sesion = inject(SesionService);
  const token = sesion.token();
  if (!token || !peticion.url.startsWith('/api/')) {
    return siguiente(peticion);
  }

  const autenticada = peticion.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  return siguiente(autenticada).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse && error.status === HttpStatusCode.Unauthorized) {
        sesion.cerrar();
      }
      return throwError(() => error);
    }),
  );
};

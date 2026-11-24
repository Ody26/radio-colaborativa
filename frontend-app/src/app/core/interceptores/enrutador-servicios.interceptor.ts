import type { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import type { ConfiguracionServicios } from '../configuracion/configuracion.service';
import { ConfiguracionService } from '../configuracion/configuracion.service';

const SERVICIO_POR_PREFIJO: ReadonlyArray<readonly [string, keyof ConfiguracionServicios]> = [
  ['/api/salas', 'urlRoomQueue'],
  ['/api/catalogo', 'urlMusicCatalog'],
];

export const enrutadorServiciosInterceptor: HttpInterceptorFn = (peticion, siguiente) => {
  const destino = SERVICIO_POR_PREFIJO.find(([prefijo]) => peticion.url.startsWith(prefijo));
  if (!destino) {
    return siguiente(peticion);
  }
  const urlBase = inject(ConfiguracionService).servicios[destino[1]];
  return siguiente(peticion.clone({ url: `${urlBase}${peticion.url}` }));
};

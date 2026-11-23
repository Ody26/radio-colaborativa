import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

export interface ConfiguracionServicios {
  urlMusicCatalog: string;
  urlRoomQueue: string;
  urlRealtimeSync: string;
}

export const RUTA_CONFIGURACION = 'assets/configuracion.json';

@Injectable({ providedIn: 'root' })
export class ConfiguracionService {
  private readonly http = inject(HttpClient);
  private configuracion?: ConfiguracionServicios;

  async cargar(): Promise<void> {
    this.configuracion = await firstValueFrom(this.http.get<ConfiguracionServicios>(RUTA_CONFIGURACION));
  }

  get servicios(): ConfiguracionServicios {
    if (!this.configuracion) {
      throw new Error('La configuración de servicios no se ha cargado');
    }
    return this.configuracion;
  }
}

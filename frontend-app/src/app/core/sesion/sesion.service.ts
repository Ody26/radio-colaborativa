import { Injectable, computed, signal } from '@angular/core';

import type { SesionParticipante } from '../modelos/sala';

const CLAVE_ALMACENAMIENTO = 'radio-colaborativa.sesion';

@Injectable({ providedIn: 'root' })
export class SesionService {
  private readonly sesionActual = signal<SesionParticipante | null>(this.leerAlmacenada());

  readonly sesion = this.sesionActual.asReadonly();
  readonly token = computed(() => this.sesionActual()?.token ?? null);
  readonly participante = computed(() => this.sesionActual()?.participante ?? null);
  readonly sala = computed(() => this.sesionActual()?.sala ?? null);

  guardar(sesion: SesionParticipante): void {
    this.sesionActual.set(sesion);
    this.escribirAlmacenada(sesion);
  }

  cerrar(): void {
    this.sesionActual.set(null);
    this.escribirAlmacenada(null);
  }

  tieneSesionPara(codigo: string): boolean {
    const sesion = this.sesionActual();
    return (
      sesion !== null &&
      sesion.sala.codigo === codigo.toUpperCase() &&
      new Date(sesion.expira_en).getTime() > Date.now()
    );
  }

  private leerAlmacenada(): SesionParticipante | null {
    try {
      const texto = sessionStorage.getItem(CLAVE_ALMACENAMIENTO);
      return texto ? (JSON.parse(texto) as SesionParticipante) : null;
    } catch {
      return null;
    }
  }

  private escribirAlmacenada(sesion: SesionParticipante | null): void {
    try {
      if (sesion) {
        sessionStorage.setItem(CLAVE_ALMACENAMIENTO, JSON.stringify(sesion));
      } else {
        sessionStorage.removeItem(CLAVE_ALMACENAMIENTO);
      }
    } catch {
      // Sin almacenamiento disponible la sesión vive solo en memoria.
    }
  }
}

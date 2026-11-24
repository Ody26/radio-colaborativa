import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import type { Observable } from 'rxjs';

import type { Participante, SalaPublica, SesionParticipante } from '../modelos/sala';

@Injectable({ providedIn: 'root' })
export class SalasApiService {
  private readonly http = inject(HttpClient);
  private readonly rutaBase = '/api/salas';

  crearSala(nombre?: string): Observable<SalaPublica> {
    return this.http.post<SalaPublica>(this.rutaBase, nombre ? { nombre } : {});
  }

  obtenerSala(codigo: string): Observable<SalaPublica> {
    return this.http.get<SalaPublica>(this.rutaSala(codigo));
  }

  unirse(codigo: string, apodo?: string): Observable<SesionParticipante> {
    return this.http.post<SesionParticipante>(`${this.rutaSala(codigo)}/unirse`, apodo ? { apodo } : {});
  }

  cambiarApodo(codigo: string, apodo: string): Observable<SesionParticipante> {
    return this.http.patch<SesionParticipante>(`${this.rutaSala(codigo)}/participantes/yo`, { apodo });
  }

  listarParticipantes(codigo: string): Observable<Participante[]> {
    return this.http.get<Participante[]>(`${this.rutaSala(codigo)}/participantes`);
  }

  private rutaSala(codigo: string): string {
    return `${this.rutaBase}/${encodeURIComponent(codigo)}`;
  }
}

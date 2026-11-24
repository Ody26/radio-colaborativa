import type { OnInit } from '@angular/core';
import { Component, inject, input, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import {
  IonBackButton,
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonInput,
  IonSpinner,
  IonToolbar,
} from '@ionic/angular';
import { finalize } from 'rxjs';

import { ViniloComponent } from '../../componentes/vinilo/vinilo.component';
import { obtenerMensajeError } from '../../core/api/mensaje-error';
import { SalasApiService } from '../../core/api/salas-api.service';
import type { SalaPublica } from '../../core/modelos/sala';
import { SesionService } from '../../core/sesion/sesion.service';
import { APODO_MAXIMO, APODO_MINIMO } from '../../core/validacion/reglas';

@Component({
  selector: 'app-unirse',
  templateUrl: 'unirse.page.html',
  styleUrls: ['unirse.page.scss'],
  imports: [
    ReactiveFormsModule,
    RouterLink,
    IonHeader,
    IonToolbar,
    IonButtons,
    IonBackButton,
    IonContent,
    IonInput,
    IonButton,
    IonSpinner,
    ViniloComponent,
  ],
})
export class UnirsePage implements OnInit {
  private readonly salasApi = inject(SalasApiService);
  private readonly sesion = inject(SesionService);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(NonNullableFormBuilder);

  readonly codigo = input.required<string>();

  readonly sala = signal<SalaPublica | null>(null);
  readonly cargando = signal(true);
  readonly uniendose = signal(false);
  readonly error = signal<string | null>(null);

  readonly formulario = this.formBuilder.group({
    apodo: ['', [Validators.minLength(APODO_MINIMO), Validators.maxLength(APODO_MAXIMO)]],
  });

  ngOnInit(): void {
    this.salasApi
      .obtenerSala(this.codigo().toUpperCase())
      .pipe(finalize(() => this.cargando.set(false)))
      .subscribe({
        next: (sala) => this.sala.set(sala),
        error: (error: unknown) => this.error.set(obtenerMensajeError(error)),
      });
  }

  unirse(): void {
    const sala = this.sala();
    if (!sala || this.formulario.invalid || this.uniendose()) {
      this.formulario.markAllAsTouched();
      return;
    }
    const apodo = this.formulario.controls.apodo.value.trim() || undefined;
    this.uniendose.set(true);
    this.error.set(null);

    this.salasApi
      .unirse(sala.codigo, apodo)
      .pipe(finalize(() => this.uniendose.set(false)))
      .subscribe({
        next: (sesion) => {
          this.sesion.guardar(sesion);
          void this.router.navigate(['/sala', sesion.sala.codigo], { replaceUrl: true });
        },
        error: (error: unknown) => this.error.set(obtenerMensajeError(error)),
      });
  }
}

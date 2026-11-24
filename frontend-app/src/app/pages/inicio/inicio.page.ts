import { Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { IonButton, IonContent, IonIcon, IonInput, IonSpinner } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { add } from 'ionicons/icons';
import { finalize, switchMap } from 'rxjs';

import { ViniloComponent } from '../../componentes/vinilo/vinilo.component';
import { obtenerMensajeError } from '../../core/api/mensaje-error';
import { SalasApiService } from '../../core/api/salas-api.service';
import { SesionService } from '../../core/sesion/sesion.service';
import { NOMBRE_SALA_MAXIMO, NOMBRE_SALA_MINIMO, PATRON_CODIGO_SALA } from '../../core/validacion/reglas';

@Component({
  selector: 'app-inicio',
  templateUrl: 'inicio.page.html',
  styleUrls: ['inicio.page.scss'],
  imports: [ReactiveFormsModule, IonContent, IonInput, IonButton, IonIcon, IonSpinner, ViniloComponent],
})
export class InicioPage {
  private readonly salasApi = inject(SalasApiService);
  private readonly sesion = inject(SesionService);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(NonNullableFormBuilder);

  readonly creando = signal(false);
  readonly error = signal<string | null>(null);

  readonly formularioCrear = this.formBuilder.group({
    nombre: ['', [Validators.minLength(NOMBRE_SALA_MINIMO), Validators.maxLength(NOMBRE_SALA_MAXIMO)]],
  });

  readonly formularioUnirse = this.formBuilder.group({
    codigo: ['', [Validators.required, Validators.pattern(PATRON_CODIGO_SALA)]],
  });

  constructor() {
    addIcons({ add });
  }

  crearSala(): void {
    if (this.formularioCrear.invalid || this.creando()) {
      this.formularioCrear.markAllAsTouched();
      return;
    }
    const nombre = this.formularioCrear.controls.nombre.value.trim() || undefined;
    this.creando.set(true);
    this.error.set(null);

    this.salasApi
      .crearSala(nombre)
      .pipe(
        switchMap((sala) => this.salasApi.unirse(sala.codigo)),
        finalize(() => this.creando.set(false)),
      )
      .subscribe({
        next: (sesion) => {
          this.sesion.guardar(sesion);
          void this.router.navigate(['/sala', sesion.sala.codigo]);
        },
        error: (error: unknown) => this.error.set(obtenerMensajeError(error)),
      });
  }

  irASala(): void {
    if (this.formularioUnirse.invalid) {
      this.formularioUnirse.markAllAsTouched();
      return;
    }
    const codigo = this.formularioUnirse.controls.codigo.value.toUpperCase();
    void this.router.navigate(['/sala', codigo]);
  }
}

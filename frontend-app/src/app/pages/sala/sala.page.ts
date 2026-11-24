import type { OnInit } from '@angular/core';
import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import {
  AlertController,
  IonButton,
  IonContent,
  IonHeader,
  IonIcon,
  IonItem,
  IonLabel,
  IonList,
  IonModal,
  IonNote,
  IonTitle,
  IonToolbar,
} from '@ionic/angular';
import { addIcons } from 'ionicons';
import { add, createOutline, exitOutline, musicalNotesOutline, shareSocialOutline } from 'ionicons/icons';

import {
  AvataresParticipantesComponent,
  obtenerIniciales,
} from '../../componentes/avatares-participantes/avatares-participantes.component';
import { ViniloComponent } from '../../componentes/vinilo/vinilo.component';
import { obtenerMensajeError } from '../../core/api/mensaje-error';
import { SalasApiService } from '../../core/api/salas-api.service';
import { AvisosService } from '../../core/avisos/avisos.service';
import type { Participante } from '../../core/modelos/sala';
import { SesionService } from '../../core/sesion/sesion.service';
import { APODO_MAXIMO, APODO_MINIMO } from '../../core/validacion/reglas';

@Component({
  selector: 'app-sala',
  templateUrl: 'sala.page.html',
  styleUrls: ['sala.page.scss'],
  imports: [
    IonContent,
    IonButton,
    IonIcon,
    IonModal,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonList,
    IonItem,
    IonLabel,
    IonNote,
    AvataresParticipantesComponent,
    ViniloComponent,
  ],
})
export class SalaPage implements OnInit {
  private readonly salasApi = inject(SalasApiService);
  private readonly avisos = inject(AvisosService);
  private readonly alertController = inject(AlertController);
  private readonly router = inject(Router);
  protected readonly sesion = inject(SesionService);
  protected readonly obtenerIniciales = obtenerIniciales;

  readonly participantes = signal<Participante[]>([]);
  readonly participantesAbiertos = signal(false);

  constructor() {
    addIcons({ add, createOutline, exitOutline, musicalNotesOutline, shareSocialOutline });
  }

  ngOnInit(): void {
    this.cargarParticipantes();
  }

  abrirParticipantes(): void {
    this.cargarParticipantes();
    this.participantesAbiertos.set(true);
  }

  async compartir(): Promise<void> {
    const sala = this.sesion.sala();
    if (!sala) {
      return;
    }
    const enlace = `${window.location.origin}/sala/${sala.codigo}`;
    if (navigator.share) {
      try {
        await navigator.share({
          title: sala.nombre,
          text: `Únete a mi sala de radio (código ${sala.codigo})`,
          url: enlace,
        });
      } catch {
        // El usuario canceló el diálogo de compartir.
      }
      return;
    }
    try {
      await navigator.clipboard.writeText(enlace);
      await this.avisos.informar('Enlace copiado. Compártelo con tus amigos.');
    } catch {
      await this.avisos.informar(`Comparte este enlace: ${enlace}`);
    }
  }

  async agregarCancion(): Promise<void> {
    await this.avisos.informar('La búsqueda de canciones llega muy pronto.');
  }

  async editarApodo(): Promise<void> {
    const alerta = await this.alertController.create({
      header: 'Cambiar apodo',
      inputs: [
        {
          name: 'apodo',
          type: 'text',
          value: this.sesion.participante()?.apodo,
          attributes: { minlength: APODO_MINIMO, maxlength: APODO_MAXIMO },
        },
      ],
      buttons: [
        { text: 'Cancelar', role: 'cancel' },
        { text: 'Guardar', handler: (datos: { apodo: string }) => this.guardarApodo(datos.apodo) },
      ],
    });
    await alerta.present();
  }

  salir(): void {
    this.sesion.cerrar();
    void this.router.navigate(['/'], { replaceUrl: true });
  }

  private guardarApodo(apodo: string): boolean {
    const limpio = apodo.trim();
    const sala = this.sesion.sala();
    if (!sala || limpio.length < APODO_MINIMO || limpio.length > APODO_MAXIMO) {
      void this.avisos.advertir(`El apodo debe tener entre ${APODO_MINIMO} y ${APODO_MAXIMO} caracteres`);
      return false;
    }
    this.salasApi.cambiarApodo(sala.codigo, limpio).subscribe({
      next: (sesion) => {
        this.sesion.guardar(sesion);
        this.cargarParticipantes();
        void this.avisos.informar(`Ahora eres ${sesion.participante.apodo}`);
      },
      error: (error: unknown) => void this.avisos.advertir(obtenerMensajeError(error)),
    });
    return true;
  }

  private cargarParticipantes(): void {
    const sala = this.sesion.sala();
    if (!sala) {
      return;
    }
    this.salasApi.listarParticipantes(sala.codigo).subscribe({
      next: (participantes) => this.participantes.set(participantes),
      error: (error: unknown) => void this.avisos.advertir(obtenerMensajeError(error)),
    });
  }
}

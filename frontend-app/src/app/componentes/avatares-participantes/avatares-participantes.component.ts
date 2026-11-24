import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import type { Participante } from '../../core/modelos/sala';

const FONDOS = ['var(--rc-menta)', 'var(--rc-coral-suave)', 'var(--rc-violeta-suave)'];

export function obtenerIniciales(apodo: string): string {
  return apodo
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((palabra) => palabra[0])
    .join('')
    .toUpperCase();
}

@Component({
  selector: 'app-avatares-participantes',
  template: `
    @for (avatar of visibles(); track avatar.id) {
      <span class="avatar" [style.background]="avatar.fondo">{{ avatar.iniciales }}</span>
    }
    @if (restantes() > 0) {
      <span class="avatar restantes">+{{ restantes() }}</span>
    }
  `,
  styles: `
    :host {
      display: inline-flex;
    }
    .avatar {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 2px solid var(--ion-background-color);
      color: var(--ion-color-dark);
      font-size: 12px;
      font-weight: 700;
    }
    .avatar + .avatar {
      margin-left: -10px;
    }
    .restantes {
      background: var(--ion-color-dark);
      color: #ffffff;
      font-size: 11px;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AvataresParticipantesComponent {
  readonly participantes = input.required<Participante[]>();
  readonly maximo = input(2);

  readonly visibles = computed(() =>
    this.participantes()
      .slice(0, this.maximo())
      .map((participante, indice) => ({
        id: participante.id_participante,
        iniciales: obtenerIniciales(participante.apodo),
        fondo: FONDOS[indice % FONDOS.length],
      })),
  );

  readonly restantes = computed(() => Math.max(this.participantes().length - this.maximo(), 0));
}

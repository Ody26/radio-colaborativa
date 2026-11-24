import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-vinilo',
  template: `
    <div class="disco" [class.girando]="girando()">
      <div class="surco">
        <div class="etiqueta" [style.background]="color()"><span class="centro"></span></div>
      </div>
    </div>
  `,
  styles: `
    :host {
      display: inline-block;
    }
    .disco {
      width: var(--rc-vinilo-tamano, var(--rc-vinilo-base));
      height: var(--rc-vinilo-tamano, var(--rc-vinilo-base));
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background: var(--ion-color-dark);
      box-shadow: 0 20px 40px rgba(27, 21, 48, 0.18);
    }
    .surco {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 78%;
      height: 78%;
      border-radius: 50%;
      border: 2px solid #3a3254;
    }
    .etiqueta {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 44%;
      height: 44%;
      border-radius: 50%;
    }
    .centro {
      width: 14%;
      height: 14%;
      border-radius: 50%;
      background: var(--ion-color-dark);
    }
    .girando {
      animation: girar 6s linear infinite;
    }
    @keyframes girar {
      to {
        transform: rotate(360deg);
      }
    }
    @media (prefers-reduced-motion: reduce) {
      .girando {
        animation: none;
      }
    }
  `,
  host: { 'aria-hidden': 'true', '[style.--rc-vinilo-base]': 'tamano() + "px"' },
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ViniloComponent {
  readonly tamano = input(190);
  readonly color = input('var(--ion-color-secondary)');
  readonly girando = input(false);
}

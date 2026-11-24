import { Injectable, inject } from '@angular/core';
import { ToastController } from '@ionic/angular';

@Injectable({ providedIn: 'root' })
export class AvisosService {
  private readonly toastController = inject(ToastController);

  async informar(mensaje: string): Promise<void> {
    await this.mostrar(mensaje, 'dark');
  }

  async advertir(mensaje: string): Promise<void> {
    await this.mostrar(mensaje, 'danger');
  }

  private async mostrar(mensaje: string, color: 'dark' | 'danger'): Promise<void> {
    const aviso = await this.toastController.create({ message: mensaje, color, duration: 2500, position: 'bottom' });
    await aviso.present();
  }
}

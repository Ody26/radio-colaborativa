import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { inject, provideAppInitializer } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import {
  PreloadAllModules,
  RouteReuseStrategy,
  provideRouter,
  withComponentInputBinding,
  withPreloading,
} from '@angular/router';
import { IonicRouteStrategy, provideIonicAngular } from '@ionic/angular';

import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';
import { ConfiguracionService } from './app/core/configuracion/configuracion.service';
import { autenticacionInterceptor } from './app/core/interceptores/autenticacion.interceptor';
import { enrutadorServiciosInterceptor } from './app/core/interceptores/enrutador-servicios.interceptor';

bootstrapApplication(AppComponent, {
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    provideIonicAngular(),
    provideHttpClient(withInterceptors([autenticacionInterceptor, enrutadorServiciosInterceptor])),
    provideAppInitializer(() => inject(ConfiguracionService).cargar()),
    provideRouter(routes, withPreloading(PreloadAllModules), withComponentInputBinding()),
  ],
});

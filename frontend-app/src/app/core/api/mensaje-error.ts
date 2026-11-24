import { HttpErrorResponse } from '@angular/common/http';

export function obtenerMensajeError(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) {
      return 'No se pudo conectar con el servidor. Revisa tu conexión e intenta de nuevo.';
    }
    const detalle = (error.error as { detail?: unknown } | null)?.detail;
    if (typeof detalle === 'string') {
      return detalle;
    }
  }
  return 'Ocurrió un error inesperado. Intenta de nuevo.';
}

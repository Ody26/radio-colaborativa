export interface SalaPublica {
  id_sala: string;
  codigo: string;
  nombre: string;
  estado: 'activa';
  fecha_creacion: string;
  fecha_expiracion: string;
  participantes_conectados: number;
}

export interface Participante {
  id_participante: string;
  apodo: string;
  unido_en: string;
}

export interface SesionParticipante {
  token: string;
  token_tipo: 'bearer';
  expira_en: string;
  participante: Participante;
  sala: SalaPublica;
}

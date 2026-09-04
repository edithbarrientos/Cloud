/**
 * Componente: Contrato Canónico de Salida - Espejo Node.js (camelCase)
 */

export interface ITelemetryConsumption {
  modeloUtilizado: string;
  tokensPromptEntrada: number;
  tokensCompletionSalida: number;
  tokensTotalesFacturables: number;
  latenciaComputoMilisegundos: number;
}

export interface ISecurityAudit {
  guardrailsEntradaAprobados: boolean;
  guardrailsSalidaAprobados: boolean;
  scoreConfianzaRag: number;
}

export interface IAIEngineResponse {
  correlationId: string;
  canalUsuarioId: string;
  textRespuestaGenerada: string;
  telemetriaConsumo: ITelemetryConsumption;
  auditoriaSecurity: ISecurityAudit;
}
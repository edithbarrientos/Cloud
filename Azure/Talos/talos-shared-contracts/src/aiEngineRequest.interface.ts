/**
 * Autor: EdithBG <edithbg@corporativo.internal>
 * Componente: Contrato Canónico de Entrada - Espejo Node.js (camelCase)
 */

export interface IRagContext {
  origenDocumentoId: string;
  fragmentoLegalVeridico: string;
}

export interface IChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface IChatContext {
  textoUsuarioLibre: string;
  historialRecienteCache: IChatMessage[];
}

export interface IRoutingConfig {
  modeloAsignado: string;
  temperaturaComputo: number;
  maxTokensPermitidos: number;
  perfilAgente: 'logistica' | 'finanzas' | 'legal' | 'retencion' | 'general';
}

export interface IAIEngineRequest {
  correlationId: string; // Identificador único global de trazabilidad W3C
  canalUsuarioId: string;
  configuracionRuteo: IRoutingConfig;
  contextoInyectadoRag?: IRagContext;
  conversacionActual: IChatContext;
}
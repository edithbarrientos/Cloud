# -*- coding: utf-8 -*-
import logging
from ai_agentic_core.interceptors.base_interceptor import BaseCognitiveInterceptor
from typing import Dict, Any

class GlossaryInterceptor(BaseCognitiveInterceptor):
    """Plugin de Gobierno encargado de homologar taxónomias ambiguas en RAM."""
    def __init__(self):
        super().__init__()
        self._canonical_glossary = ["financial_revenue", "gross_margin", "customer_pii_identity"]
        self._cached_grams = {
            term: set(term[i:i+2] for i in range(len(term) - 1)) for term in self._canonical_glossary
        }

    async def _execute_pre(self, tenant_id: str, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        raw_kpi = json_payload.get("kpi_target", "UNKNOWN_KPI")
        if raw_kpi in self._cached_grams:
            if self.consecutive_failures > 0: self.reset_circuit()
            return json_payload
            
        term_lower = raw_kpi.lower()
        ambiguous_grams = set(term_lower[i:i+2] for i in range(len(term_lower) - 1)) if len(term_lower) >= 2 else {term_lower}
        
        matches = [(t, len(ambiguous_grams & g) / len(ambiguous_grams | g)) for t, g in self._cached_grams.items()]
        best_match, max_similarity = max(matches, key=lambda x: x, default=(raw_kpi, 0.0))

        if max_similarity >= 0.40:
            self.logger.warning(f"[GLOSSARY_ALIGN] Termino '{raw_kpi}' homologado a canonico '{best_match}' ({round(max_similarity, 2)})")
            json_payload["kpi_target"] = best_match
            json_payload["_glossary_confidence"] = max_similarity
            
        if self.consecutive_failures > 0: self.reset_circuit()
        return json_payload

    async def _execute_post(self, tenant_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        return report_data

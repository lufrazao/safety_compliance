"""
Compliance checking engine that evaluates regulations based on airport variables.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import json
from datetime import datetime, date, timedelta
from app.models import (
    Airport, Regulation, ComplianceRecord, ComplianceStatus,
    AirportSize, AirportType, RequirementClassification, EvaluationType
)


class ComplianceEngine:
    """Engine for checking airport compliance with ANAC regulations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def regulation_applies_to_airport(self, regulation: Regulation, airport: Airport) -> bool:
        """
        Determine if a regulation applies to a specific airport based on its variables.
        Aligned with ANAC RBAC directives.
        """
        # Check size requirements
        if regulation.applies_to_sizes:
            try:
                applicable_sizes = json.loads(regulation.applies_to_sizes)
                # Se size não estiver definido, calcular a partir de usage_class ou annual_passengers
                airport_size = airport.size
                if not airport_size:
                    if airport.usage_class:
                        # usage_class é string no banco de dados
                        usage_class_val = str(airport.usage_class)
                        if usage_class_val in ['PRIVADO', 'I']:
                            airport_size = AirportSize.SMALL
                        elif usage_class_val == 'II':
                            airport_size = AirportSize.MEDIUM
                        elif usage_class_val == 'III':
                            airport_size = AirportSize.LARGE
                        elif usage_class_val == 'IV':
                            airport_size = AirportSize.INTERNATIONAL
                    elif airport.annual_passengers:
                        if airport.annual_passengers < 200000:
                            airport_size = AirportSize.SMALL
                        elif airport.annual_passengers < 1000000:
                            airport_size = AirportSize.MEDIUM
                        elif airport.annual_passengers < 10000000:
                            airport_size = AirportSize.LARGE
                        else:
                            airport_size = AirportSize.INTERNATIONAL
                    else:
                        airport_size = AirportSize.SMALL  # Default
                
                size_val = airport_size.value if hasattr(airport_size, 'value') else str(airport_size) if airport_size else None
                if size_val and size_val not in applicable_sizes:
                    return False
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Check type requirements
        if regulation.applies_to_types:
            try:
                applicable_types = json.loads(regulation.applies_to_types)
                at = airport.airport_type
                airport_type_val = "commercial"
                if at is not None:
                    airport_type_val = at.value if hasattr(at, 'value') else str(at)
                if airport_type_val not in applicable_types:
                    return False
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass
        
        # Check passenger threshold
        # If min_passengers is set, we need to verify
        if regulation.min_passengers:
            # If airport has annual_passengers, use it directly
            if airport.annual_passengers:
                if airport.annual_passengers < regulation.min_passengers:
                    return False
            else:
                # If annual_passengers is not provided, infer from usage_class or airport size
                # This ensures regulations are not incorrectly excluded
                if airport.usage_class:
                    # Usar usage_class para inferir passageiros (usage_class é string)
                    usage_class_val = str(airport.usage_class)
                    if usage_class_val == 'PRIVADO' or usage_class_val == 'I':
                        inferred_passengers = 100000  # Estimativa conservadora
                    elif usage_class_val == 'II':
                        inferred_passengers = 600000
                    elif usage_class_val == 'III':
                        inferred_passengers = 3000000
                    elif usage_class_val == 'IV':
                        inferred_passengers = 10000000
                    else:
                        inferred_passengers = 100000
                    
                    if inferred_passengers < regulation.min_passengers:
                        return False
                elif airport.size:
                    # Fallback para size se usage_class não estiver disponível
                    size_passenger_ranges = {
                        'small': (0, 200000),
                        'medium': (200000, 1000000),
                        'large': (1000000, 10000000),
                        'international': (10000000, float('inf'))
                    }
                    sz = airport.size
                    sz_val = sz.value if hasattr(sz, 'value') else str(sz) if sz else None
                    if sz_val and sz_val in size_passenger_ranges:
                        size_min, size_max = size_passenger_ranges[sz_val]
                        # Use the minimum of the range as conservative estimate
                        # If regulation requires more than the max of the range, it doesn't apply
                        if regulation.min_passengers > size_max:
                            return False
                        # If regulation requires less than min of range, it might apply
                        # But be conservative: if it's close to the threshold, don't apply
                        # Only apply if the regulation threshold is clearly within the size range
                        if regulation.min_passengers > size_min:
                            # Regulation requires more than minimum of size range
                            # Only apply if airport size suggests it could meet the requirement
                            # For safety, we'll be conservative and not apply if threshold is above size minimum
                            if regulation.min_passengers > (size_min + (size_max - size_min) * 0.5):
                                return False
        
        # Check international operations requirement
        if regulation.requires_international and not airport.has_international_operations:
            return False
        
        # Check cargo operations requirement
        if regulation.requires_cargo and not airport.has_cargo_operations:
            return False
        
        # Check maintenance facility requirement
        if regulation.requires_maintenance and not airport.has_maintenance_facility:
            return False
        
        # Check minimum runways
        if regulation.min_runways and airport.number_of_runways < regulation.min_runways:
            return False
        
        # Check minimum aircraft weight
        if regulation.min_aircraft_weight:
            if airport.max_aircraft_weight:
                if airport.max_aircraft_weight < regulation.min_aircraft_weight:
                    return False
            else:
                # If weight not provided, infer from usage_class or airport size
                # Large/international airports typically handle larger aircraft
                if airport.usage_class:
                    # Usar usage_class para inferir peso (usage_class é string)
                    usage_class_val = str(airport.usage_class)
                    if usage_class_val == 'PRIVADO' or usage_class_val == 'I':
                        inferred_weight = 20  # Estimativa conservadora em toneladas
                    elif usage_class_val == 'II':
                        inferred_weight = 100
                    elif usage_class_val == 'III':
                        inferred_weight = 250
                    elif usage_class_val == 'IV':
                        inferred_weight = 400
                    else:
                        inferred_weight = 20
                    
                    if inferred_weight < regulation.min_aircraft_weight:
                        return False
                elif airport.size:
                    # Fallback para size se usage_class não estiver disponível
                    size_weight_ranges = {
                        'small': (0, 50),
                        'medium': (50, 150),
                        'large': (150, 300),
                        'international': (300, float('inf'))
                    }
                    if airport.size and airport.size.value in size_weight_ranges:
                        size_min_weight, size_max_weight = size_weight_ranges[airport.size.value]
                        if regulation.min_aircraft_weight > size_max_weight:
                            return False
        
        return True
    
    def get_applicable_regulations(self, airport: Airport) -> List[Regulation]:
        """Get all regulations that apply to a specific airport."""
        all_regulations = self.db.query(Regulation).all()
        applicable = []
        
        for regulation in all_regulations:
            if self.regulation_applies_to_airport(regulation, airport):
                applicable.append(regulation)
        
        return applicable
    
    def check_compliance(self, airport_id: int, auto_create_records: bool = True) -> dict:
        """
        Perform a comprehensive compliance check for an airport.
        Returns a summary and creates/updates compliance records.
        """
        airport = self.db.query(Airport).filter(Airport.id == airport_id).first()
        if not airport:
            raise ValueError(f"Airport with id {airport_id} not found")
        
        # Garantir que size e annual_passengers estejam calculados se não estiverem definidos
        if not airport.size or (airport.annual_passengers is None):
            if airport.usage_class:
                # usage_class é string no banco de dados
                usage_class = str(airport.usage_class)
                if usage_class == 'PRIVADO':
                    airport.size = AirportSize.SMALL
                    airport.annual_passengers = 0
                elif usage_class == 'I':
                    airport.size = AirportSize.SMALL
                    airport.annual_passengers = 100000
                elif usage_class == 'II':
                    airport.size = AirportSize.MEDIUM
                    airport.annual_passengers = 600000
                elif usage_class == 'III':
                    airport.size = AirportSize.LARGE
                    airport.annual_passengers = 3000000
                elif usage_class == 'IV':
                    airport.size = AirportSize.INTERNATIONAL
                    airport.annual_passengers = 10000000
                # Salvar no banco se foi calculado
                self.db.commit()
            elif not airport.size:
                # Fallback: se não houver usage_class, usar default
                airport.size = AirportSize.SMALL
                airport.annual_passengers = 100000
                self.db.commit()
        
        applicable_regulations = self.get_applicable_regulations(airport)
        
        # Get or create compliance records
        compliance_records = []
        for regulation in applicable_regulations:
            record = self.db.query(ComplianceRecord).filter(
                ComplianceRecord.airport_id == airport_id,
                ComplianceRecord.regulation_id == regulation.id
            ).first()
            
            if not record and auto_create_records:
                # Create new record with pending status and generate initial action items
                action_items = self._generate_action_items(regulation, airport)
                record = ComplianceRecord(
                    airport_id=airport_id,
                    regulation_id=regulation.id,
                    status=ComplianceStatus.PENDING_REVIEW,
                    action_items=json.dumps(action_items) if action_items else None
                )
                self.db.add(record)
                self.db.commit()
                self.db.refresh(record)
            elif record:
                rec_st = record.status
                rec_st_val = rec_st.value if (rec_st and hasattr(rec_st, 'value')) else str(rec_st) if rec_st else "pending_review"
                if rec_st_val in ["non_compliant", "pending_review"]:
                    if not record.action_items:
                        action_items = self._generate_action_items(regulation, airport)
                        if action_items:
                            record.action_items = json.dumps(action_items)
                            self.db.commit()
                            self.db.refresh(record)
            
            if record:
                compliance_records.append(record)
        
        # Count by status
        status_counts = {
            ComplianceStatus.COMPLIANT: 0,
            ComplianceStatus.NON_COMPLIANT: 0,
            ComplianceStatus.PARTIAL: 0,
            ComplianceStatus.PENDING_REVIEW: 0,
            ComplianceStatus.NOT_APPLICABLE: 0
        }
        
        for record in compliance_records:
            st = record.status
            st_val = st.value if (st and hasattr(st, 'value')) else (str(st) if st else "pending_review")
            try:
                st_enum = ComplianceStatus(st_val) if isinstance(st_val, str) else st
            except (ValueError, TypeError):
                st_enum = ComplianceStatus.PENDING_REVIEW
            status_counts[st_enum] = status_counts.get(st_enum, 0) + 1
        
        # Calculate ANAC compliance scores
        compliance_scores = self._calculate_anac_scores(compliance_records, applicable_regulations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(airport, compliance_records, compliance_scores)
        
        # Se nenhuma norma aplicável, verificar se o banco tem normas
        if len(applicable_regulations) == 0:
            total_in_db = self.db.query(Regulation).count()
            if total_in_db == 0:
                recommendations.insert(0, "Nenhuma norma cadastrada. Execute POST /api/seed para carregar as normas RBAC-153 e RBAC-154.")
            else:
                recommendations.insert(0, "Nenhuma norma se aplica a este aeroporto com as características atuais. Verifique classe por uso, tipo e tamanho.")
        
        return {
            "airport_id": airport_id,
            "total_regulations": len(applicable_regulations),
            "applicable_regulations": len(applicable_regulations),
            "compliant_count": status_counts[ComplianceStatus.COMPLIANT],
            "non_compliant_count": status_counts[ComplianceStatus.NON_COMPLIANT],
            "partial_count": status_counts[ComplianceStatus.PARTIAL],
            "pending_count": status_counts[ComplianceStatus.PENDING_REVIEW],
            "compliance_records": compliance_records,
            "recommendations": recommendations,
            "anac_scores": compliance_scores
        }
    
    def _calculate_anac_scores(self, records: List[ComplianceRecord], regulations: List[Regulation]) -> dict:
        """
        Calculate ANAC compliance scores based on D/C/B/A classification system.
        Returns scores for DOCS, TOPS, and overall compliance.
        """
        # Separate by classification
        d_items = []  # Essential (must have 85% compliance)
        c_items = []  # Complementary
        b_items = []  # Recommended practices
        a_items = []  # Best practices
        
        # Separate by evaluation type
        docs_items = []
        tops_items = []
        
        total_d_weight = 0
        total_c_weight = 0
        total_b_weight = 0
        total_a_weight = 0
        
        compliant_d_weight = 0
        compliant_c_weight = 0
        compliant_b_weight = 0
        compliant_a_weight = 0
        
        for record in records:
            regulation = next((r for r in regulations if r.id == record.regulation_id), None)
            if not regulation:
                continue
            
            classification = regulation.requirement_classification
            weight = regulation.weight or 1
            eval_type = regulation.evaluation_type or EvaluationType.BOTH
            if hasattr(eval_type, 'value'):
                eval_type = eval_type
            elif isinstance(eval_type, str):
                try:
                    eval_type = EvaluationType(eval_type)
                except (ValueError, TypeError):
                    eval_type = EvaluationType.BOTH
            
            rec_st = record.status
            rec_st_val = rec_st.value if (rec_st and hasattr(rec_st, 'value')) else str(rec_st) if rec_st else "pending_review"
            is_compliant = rec_st_val == "compliant"
            
            cls_val = classification.value if (classification and hasattr(classification, 'value')) else (str(classification) if classification else None)
            if cls_val == "D":
                d_items.append(record)
                total_d_weight += weight
                if is_compliant:
                    compliant_d_weight += weight
            elif cls_val == "C":
                c_items.append(record)
                total_c_weight += weight
                if is_compliant:
                    compliant_c_weight += weight
            elif cls_val == "B":
                b_items.append(record)
                total_b_weight += weight
                if is_compliant:
                    compliant_b_weight += weight
            elif cls_val == "A":
                a_items.append(record)
                total_a_weight += weight
                if is_compliant:
                    compliant_a_weight += weight
            
            # Track by evaluation type
            if eval_type in [EvaluationType.DOCS, EvaluationType.BOTH]:
                docs_items.append(record)
            if eval_type in [EvaluationType.TOPS, EvaluationType.BOTH]:
                tops_items.append(record)
        
        # Calculate percentages
        d_percentage = (compliant_d_weight / total_d_weight * 100) if total_d_weight > 0 else 0
        c_percentage = (compliant_c_weight / total_c_weight * 100) if total_c_weight > 0 else 0
        b_percentage = (compliant_b_weight / total_b_weight * 100) if total_b_weight > 0 else 0
        a_percentage = (compliant_a_weight / total_a_weight * 100) if total_a_weight > 0 else 0
        
        # Check if essential (D) items meet 85% threshold
        essential_compliant = d_percentage >= 85.0
        
        # Calculate overall weighted score
        total_weight = total_d_weight + total_c_weight + total_b_weight + total_a_weight
        compliant_weight = compliant_d_weight + compliant_c_weight + compliant_b_weight + compliant_a_weight
        overall_score = (compliant_weight / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "essential_compliant": essential_compliant,
            "essential_percentage": round(d_percentage, 2),
            "complementary_percentage": round(c_percentage, 2),
            "recommended_percentage": round(b_percentage, 2),
            "best_practices_percentage": round(a_percentage, 2),
            "overall_score": round(overall_score, 2),
            "d_items_total": len(d_items),
            "d_items_compliant": len([r for r in d_items if r.status == ComplianceStatus.COMPLIANT]),
            "c_items_total": len(c_items),
            "b_items_total": len(b_items),
            "a_items_total": len(a_items),
            "docs_items_total": len(docs_items),
            "tops_items_total": len(tops_items)
        }
    
    def _generate_recommendations(self, airport: Airport, records: List[ComplianceRecord], scores: dict = None) -> List[str]:
        """Generate actionable recommendations based on compliance status."""
        recommendations = []
        
        non_compliant = [r for r in records if r.status == ComplianceStatus.NON_COMPLIANT]
        pending = [r for r in records if r.status == ComplianceStatus.PENDING_REVIEW]
        
        if non_compliant:
            recommendations.append(
                f"Urgent: {len(non_compliant)} regulation(s) are non-compliant. "
                "Review and address immediately to avoid penalties."
            )
        
        if pending:
            recommendations.append(
                f"Action required: {len(pending)} regulation(s) need compliance review. "
                "Schedule inspections to verify compliance status."
            )
        
        # ANAC-specific recommendations based on scores
        if scores:
            if not scores.get("essential_compliant", True):
                essential_pct = scores.get("essential_percentage", 0)
                recommendations.append(
                    f"⚠️ CRITICAL: Essential requirements (D) compliance is {essential_pct:.1f}%. "
                    f"Minimum 85% required for ACOP. Focus on D-classified items immediately."
                )
            else:
                recommendations.append(
                    f"✓ Essential requirements (D) compliance: {scores.get('essential_percentage', 0):.1f}% - "
                    "Meets ANAC minimum threshold."
                )
            
            overall = scores.get("overall_score", 0)
            if overall < 70:
                recommendations.append(
                    f"Overall compliance score is {overall:.1f}%. Consider focusing on complementary (C) "
                    "and recommended (B) practices to improve ACOP rating."
                )
        
        # Size-specific recommendations
        ap_sz = airport.size
        ap_sz_val = ap_sz.value if (ap_sz and hasattr(ap_sz, 'value')) else (str(ap_sz) if ap_sz else None)
        if ap_sz_val == "small":
            recommendations.append(
                "As a small airport, ensure you have basic safety equipment and "
                "trained personnel as per ANAC minimum requirements."
            )
        elif ap_sz_val in ["large", "international"]:
            recommendations.append(
                "As a large/international airport, ensure comprehensive safety management "
                "systems (SMS) are in place and regularly audited."
            )
        
        # Type-specific recommendations
        if airport.has_international_operations:
            recommendations.append(
                "International operations require additional security and customs compliance. "
                "Verify AVSEC requirements are met."
            )
        
        return recommendations
    
    def _generate_action_items(self, regulation: Regulation, airport: Airport) -> List[str]:
        """
        Generate actionable items based on regulation requirements and airport characteristics.
        This helps airport teams understand what needs to be done to achieve compliance.
        """
        action_items = []
        requirements = (regulation.requirements or "").lower()
        safety_val = regulation.safety_category.value if (regulation.safety_category and hasattr(regulation.safety_category, 'value')) else ""
        
        # Generate action items based on regulation requirements and safety category
        if safety_val == "operational_safety":
            if "sms" in requirements or "sistema de gerenciamento" in requirements:
                action_items.append("Desenvolver e documentar política de segurança operacional")
                action_items.append("Implementar processo de gestão de riscos operacionais")
                action_items.append("Estabelecer sistema de garantia de segurança (auditorias internas)")
                action_items.append("Criar programa de promoção da segurança")
                sz_val = airport.size.value if (airport.size and hasattr(airport.size, 'value')) else (str(airport.size) if airport.size else None)
                if sz_val in ["large", "international"]:
                    action_items.append("Realizar auditoria externa anual do SMS")
            
            if "incidentes" in requirements or "acidentes" in requirements:
                action_items.append("Implementar sistema de registro de incidentes")
                action_items.append("Estabelecer procedimento de notificação à ANAC (24h para graves)")
                action_items.append("Treinar equipe em investigação de incidentes")
            
            if "treinamento" in requirements:
                action_items.append("Desenvolver programa de treinamento inicial para novo pessoal")
                action_items.append("Estabelecer programa de reciclagem anual")
                action_items.append("Manter registro de todos os treinamentos realizados")
        
        elif safety_val == "fire_safety":
            if "scir" in requirements or "combate a incêndio" in requirements:
                action_items.append("Determinar categoria SCIR baseada na maior aeronave operacional")
                action_items.append("Contratar/treinamento equipe de SCIR adequada à categoria")
                action_items.append("Garantir tempo de resposta máximo de 3 minutos")
                sz_val = airport.size.value if (airport.size and hasattr(airport.size, 'value')) else (str(airport.size) if airport.size else None)
                if sz_val in ["medium", "large", "international"]:
                    action_items.append("Adquirir veículos de combate a incêndio certificados")
            
            if "equipamentos" in requirements or "extintores" in requirements:
                action_items.append("Instalar extintores em todas as áreas conforme norma")
                action_items.append("Implementar sistema de hidrantes operacional")
                action_items.append("Estabelecer programa de inspeção mensal de equipamentos")
            
            if "detecção" in requirements or "alarme" in requirements:
                action_items.append("Instalar sistema de detecção automática de incêndio")
                action_items.append("Integrar sistema com central de monitoramento")
                action_items.append("Realizar testes semanais do sistema de alarme")
        
        elif safety_val == "security":
            if "avsec" in requirements or "segurança da aviação" in requirements:
                action_items.append("Desenvolver programa AVSEC documentado")
                action_items.append("Treinar pessoal de segurança conforme padrões AVSEC")
                action_items.append("Implementar controle de acesso a áreas restritas")
            
            if "internacionais" in requirements or "alfandegário" in requirements:
                action_items.append("Coordenar com Receita Federal para controle alfandegário")
                action_items.append("Estabelecer área de inspeção de imigração")
                action_items.append("Implementar sistema de rastreamento de bagagens")
            
            if "inspeção" in requirements or "bagagens" in requirements:
                action_items.append("Adquirir equipamentos de raio-X para bagagens")
                action_items.append("Instalar detectores de metais")
                action_items.append("Treinar e certificar pessoal de inspeção")
            
            if "perimétrica" in requirements or "perímetro" in requirements:
                action_items.append("Avaliar e melhorar cerca perimétrica")
                action_items.append("Instalar iluminação noturna no perímetro")
                action_items.append("Implementar sistema de vigilância por câmeras")
                action_items.append("Estabelecer rotina de patrulhamento")
        
        elif safety_val == "infrastructure":
            if "pistas" in requirements or "pátios" in requirements:
                action_items.append("Estabelecer rotina de inspeção diária de pistas")
                action_items.append("Implementar programa de manutenção preventiva de pátios")
                action_items.append("Garantir sinalização adequada conforme padrões ICAO")
            
            if "sinalização" in requirements:
                action_items.append("Auditar sinalização existente conforme padrões ICAO")
                action_items.append("Atualizar marcações de pista se necessário")
                action_items.append("Verificar visibilidade de placas de identificação")
            
            if "iluminação" in requirements:
                action_items.append("Verificar operação de sistema de iluminação de pista")
                action_items.append("Implementar sistema de backup para emergências")
                action_items.append("Estabelecer programa de manutenção preventiva")
            
            if "drenagem" in requirements:
                action_items.append("Inspecionar sistema de drenagem após chuvas")
                action_items.append("Limpar e manter canais e bueiros")
                action_items.append("Avaliar necessidade de melhorias estruturais")
            
            if "carga" in requirements:
                action_items.append("Garantir área de carga coberta adequada")
                action_items.append("Adquirir equipamentos de movimentação de carga")
                action_items.append("Implementar controle de temperatura quando necessário")
        
        elif safety_val == "emergency_response":
            if "plano de emergência" in requirements:
                action_items.append("Desenvolver plano de emergência aeroportuária documentado")
                action_items.append("Coordenar com órgãos externos (bombeiros, polícia, saúde)")
                action_items.append("Realizar exercício completo a cada 2 anos")
                action_items.append("Realizar exercícios parciais anuais")
            
            if "comunicação" in requirements:
                action_items.append("Verificar sistema de comunicação de emergência")
                action_items.append("Garantir rádios para equipes de resposta")
                action_items.append("Estabelecer rotina de testes mensais")
            
            if "resgate" in requirements or "ambulâncias" in requirements:
                action_items.append("Garantir disponibilidade de ambulâncias")
                action_items.append("Adquirir equipamentos de resgate adequados")
                action_items.append("Estabelecer área médica no terminal")
        
        elif safety_val == "environmental":
            if "ruído" in requirements:
                action_items.append("Instalar sistema de monitoramento de ruído")
                action_items.append("Estabelecer rotina de relatórios trimestrais")
                action_items.append("Desenvolver medidas de mitigação se necessário")
            
            if "resíduos" in requirements:
                action_items.append("Desenvolver plano de gestão de resíduos")
                action_items.append("Implementar separação de resíduos")
                action_items.append("Garantir destinação adequada de resíduos perigosos")
            
            if "emissões" in requirements:
                action_items.append("Implementar monitoramento de qualidade do ar")
                action_items.append("Avaliar medidas de redução de emissões")
                action_items.append("Priorizar uso de equipamentos elétricos quando possível")
        
        elif safety_val == "wildlife_management":
            action_items.append("Estabelecer programa de gerenciamento de fauna documentado")
            action_items.append("Implementar inspeções diárias antes das primeiras operações")
            action_items.append("Manter registro de todos os avistamentos de fauna")
            if airport.size.value in ["medium", "large", "international"]:
                action_items.append("Implementar controle de vegetação")
                action_items.append("Remover fontes de alimento para fauna")
                action_items.append("Adquirir equipamentos de dispersão de fauna")
        
        elif safety_val == "maintenance":
            if "calibração" in requirements:
                action_items.append("Identificar todos os equipamentos críticos que requerem calibração")
                action_items.append("Estabelecer cronograma de calibração anual")
                action_items.append("Manter certificados de calibração atualizados")
            
            if "preventiva" in requirements:
                action_items.append("Desenvolver programa de manutenção preventiva")
                action_items.append("Manter registro detalhado de todas as manutenções")
                action_items.append("Estabelecer cronograma de manutenções")
            
            if "manutenção aeronáutica" in requirements or "hangares" in requirements:
                action_items.append("Garantir hangares certificados pela ANAC")
                action_items.append("Verificar certificação de equipamentos de manutenção")
                action_items.append("Garantir pessoal qualificado e certificado")
                action_items.append("Implementar controle de ferramentas")
        
        elif safety_val == "personnel_certification":
            if "supervisores" in requirements:
                action_items.append("Verificar certificação ANAC de supervisores")
                action_items.append("Garantir reciclagem a cada 2 anos")
                action_items.append("Manter registro de certificações e experiência")
            
            if "treinamento" in requirements:
                action_items.append("Desenvolver programa de treinamento de segurança")
                action_items.append("Garantir treinamento inicial para todos os funcionários")
                action_items.append("Estabelecer programa de reciclagem anual")
                action_items.append("Manter certificados de conclusão de treinamentos")
        
        elif safety_val == "air_traffic_services":
            if "torre" in requirements or "controle" in requirements:
                action_items.append("Verificar certificação da torre de controle")
                action_items.append("Garantir pessoal ATC certificado e atualizado")
            
            if "navegação" in requirements:
                action_items.append("Verificar certificação de equipamentos de navegação (ILS, VOR, etc.)")
                action_items.append("Estabelecer cronograma de calibração")
                action_items.append("Implementar sistema de backup")
            
            if "comunicação" in requirements or "vhf" in requirements:
                action_items.append("Verificar operação de sistema de comunicação VHF")
                action_items.append("Confirmar certificação de frequências")
                action_items.append("Implementar sistema de backup")
                action_items.append("Estabelecer rotina de testes diários")
        
        # Add general action items if none were generated
        if not action_items:
            action_items.append(f"Revisar requisitos da norma {regulation.code}")
            action_items.append("Realizar auditoria interna para verificar conformidade")
            action_items.append("Documentar evidências de conformidade")
            action_items.append("Estabelecer cronograma de implementação se necessário")
        
        return action_items
    
    def update_compliance_status(
        self,
        record_id: int,
        status: Optional[ComplianceStatus] = None,
        notes: Optional[str] = None,
        action_items: Optional[List[str]] = None,
        completed_action_items: Optional[List[int]] = None,
        action_item_due_dates: Optional[Dict[int, str]] = None,
        verified_by: Optional[str] = None,
        custom_fields: Optional[Dict] = None
    ) -> ComplianceRecord:
        """Update the compliance status of a record."""
        record = self.db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
        if not record:
            raise ValueError(f"Compliance record with id {record_id} not found")
        
        # Get current action items to calculate status
        current_action_items = []
        if record.action_items:
            try:
                current_action_items = json.loads(record.action_items) if isinstance(record.action_items, str) else record.action_items
            except (json.JSONDecodeError, TypeError):
                current_action_items = []
        
        # Update action item due dates
        if action_item_due_dates is not None:
            # Merge with existing due dates
            existing_due_dates = {}
            if record.action_item_due_dates:
                try:
                    existing_due_dates = json.loads(record.action_item_due_dates) if isinstance(record.action_item_due_dates, str) else record.action_item_due_dates
                except (json.JSONDecodeError, TypeError):
                    existing_due_dates = {}
            
            # Update with new dates
            existing_due_dates.update(action_item_due_dates)
            record.action_item_due_dates = json.dumps(existing_due_dates) if existing_due_dates else None
        
        # Check for expired items and remove them from completed
        if record.action_item_due_dates and current_action_items:
            try:
                due_dates = json.loads(record.action_item_due_dates) if isinstance(record.action_item_due_dates, str) else record.action_item_due_dates
                today = date.today()
                expired_items = []
                
                for item_idx_str, due_date_str in due_dates.items():
                    try:
                        item_idx = int(item_idx_str)
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                        if due_date < today:
                            expired_items.append(item_idx)
                    except (ValueError, TypeError):
                        continue
                
                # Remove expired items from completed list
                if expired_items and record.completed_action_items:
                    try:
                        completed = json.loads(record.completed_action_items) if isinstance(record.completed_action_items, str) else record.completed_action_items
                        if isinstance(completed, list):
                            completed = [idx for idx in completed if idx not in expired_items]
                            record.completed_action_items = json.dumps(completed) if completed else None
                    except (json.JSONDecodeError, TypeError):
                        pass
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Update completed action items
        if completed_action_items is not None:
            record.completed_action_items = json.dumps(completed_action_items) if completed_action_items else None
            
            # Auto-update status based on completed action items
            if status is None and current_action_items:
                total_items = len(current_action_items)
                completed_count = len(completed_action_items) if completed_action_items else 0
                
                if completed_count == 0:
                    # No items completed, keep current status (or set to pending if not set)
                    if record.status == ComplianceStatus.COMPLIANT:
                        record.status = ComplianceStatus.PENDING_REVIEW
                elif completed_count > 0 and completed_count < total_items:
                    # Some items completed
                    record.status = ComplianceStatus.PARTIAL
                elif completed_count == total_items:
                    # All items completed
                    record.status = ComplianceStatus.COMPLIANT
        
        # If status is explicitly set to compliant, mark all action items as completed
        if status == ComplianceStatus.COMPLIANT and current_action_items:
            all_indices = list(range(len(current_action_items)))
            record.completed_action_items = json.dumps(all_indices)
        
        # If status is explicitly set to non-compliant, clear all completed action items
        if status == ComplianceStatus.NON_COMPLIANT:
            record.completed_action_items = None
        
        if status is not None:
            record.status = status
        if notes is not None:
            record.notes = notes
        if custom_fields is not None:
            # Convert dict to JSON string if needed
            if isinstance(custom_fields, dict):
                record.custom_fields = json.dumps(custom_fields) if custom_fields else None
            elif isinstance(custom_fields, str):
                record.custom_fields = custom_fields
            else:
                record.custom_fields = None
        if action_items is not None:
            record.action_items = json.dumps(action_items) if action_items else None
        if verified_by is not None:
            record.verified_by = verified_by
        record.last_verified = datetime.now().isoformat()
        
        self.db.commit()
        self.db.refresh(record)
        
        return record

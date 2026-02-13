"""
Script para adicionar as normas RBAC-153 que estão faltando no banco de dados.
As normas RBAC-153 estão definidas no seed_data.py mas não foram criadas porque
o banco já tinha normas RBAC-154 quando o seed foi executado.
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import (
    Regulation, SafetyCategory, RequirementClassification, EvaluationType
)
import json


def add_rbac153_regulations():
    """Adiciona as normas RBAC-153 que estão faltando."""
    db = SessionLocal()
    
    try:
        # Verificar se já existem normas RBAC-153
        existing_rbac153 = db.query(Regulation).filter(
            Regulation.code.like('RBAC-153%')
        ).count()
        
        if existing_rbac153 > 0:
            print(f"Já existem {existing_rbac153} normas RBAC-153 no banco.")
            print("Deseja continuar mesmo assim? (s/n): ", end='')
            response = input().strip().lower()
            if response != 's':
                print("Operação cancelada.")
                return
        
        # Definir as normas RBAC-153 (copiadas do seed_data.py)
        rbac153_regulations = [
            # D - Essenciais
            {
                "code": "RBAC-153-01",
                "title": "Determinação da CAT (Categoria Contraincêndio) do Aeródromo",
                "description": "Requisitos para determinação da categoria contraincêndio baseada na maior aeronave que opera regularmente",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Determinar a CAT do aeródromo baseada na maior aeronave que opera regularmente. Categorias de 1 a 9 conforme RBAC-153. Documentar e notificar à ANAC.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.201",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "CAT determinada e documentada, notificação à ANAC quando houver mudança"
            },
            {
                "code": "RBAC-153-04",
                "title": "Carro Contraincêndio de Aeródromo (CCI)",
                "description": "Requisitos para veículos de combate a incêndio conforme categoria do aeródromo",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Manter CCI adequado à categoria do aeródromo. Especificações técnicas conforme RBAC-153: capacidade de água e espuma conforme categoria (ex: CAT 1-2: mínimo 500L água + 50L espuma; CAT 3-4: mínimo 2000L água + 200L espuma; CAT 5-7: mínimo 6000L água + 600L espuma; CAT 8-9: mínimo 12000L água + 1200L espuma), velocidade mínima de 80 km/h, capacidade de bombeamento, certificação e manutenção regular conforme cronograma.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.501",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "CCI certificado e operacional, adequado à categoria, manutenção em dia"
            },
            {
                "code": "RBAC-153-06",
                "title": "Equipe de Serviço do SESCINC",
                "description": "Requisitos para composição e disponibilidade da equipe de serviço do SESCINC",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Manter equipe de serviço do SESCINC com composição mínima conforme categoria. Composição por CAT: CAT 1-2: mínimo 2 BA; CAT 3-4: mínimo 3 BA; CAT 5-6: mínimo 4 BA; CAT 7-8: mínimo 5 BA; CAT 9: mínimo 6 BA. Funções obrigatórias: BA-CE (Chefe de Equipe), BA-LR (Líder de Resgate), BA-MC (Motorista/Operador de CCI), BA-RE (Resgatista). Disponibilidade 24/7 para aeroportos comerciais com equipe completa e pronta para resposta imediata.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.601",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Equipe completa e disponível 24/7, pessoal certificado, composição adequada à categoria"
            },
            {
                "code": "RBAC-153-07",
                "title": "Tempo-Resposta do SESCINC",
                "description": "Requisitos para tempo de resposta do serviço de combate a incêndio",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Tempo de resposta máximo de 3 minutos para aeroportos comerciais, medido do ponto crítico mais distante (ACT - Área Crítica Teórica). Para aeroportos com operações noturnas, o tempo deve ser medido considerando condições noturnas. Realizar aferições semestrais no mínimo, documentar resultados, manter registro histórico e notificar à ANAC quando houver não conformidade.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.701",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Tempo-resposta ≤ 3min, aferições realizadas regularmente, registros documentados"
            },
            {
                "code": "RBAC-153-08",
                "title": "Capacitação de Recursos Humanos para o SESCINC",
                "description": "Requisitos obrigatórios de capacitação para bombeiros de aeródromo",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Todo bombeiro de aeródromo deve possuir capacitação obrigatória: CBA-1 (Curso de Habilitação de Bombeiro de Aeródromo 1), CBA-2, CBA-AT (Atualização), e especializações conforme função (CBA-CE, CBA-MC). Manter registro de certificações.",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.801",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "100% do pessoal certificado, certificações válidas, registro atualizado"
            },
            {
                "code": "RBAC-153-11",
                "title": "Plano Contraincêndio de Aeródromo (PCINC)",
                "description": "Requisitos para elaboração e manutenção do PCINC",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Elaborar e manter PCINC documentado conforme RBAC-153. Conteúdo mínimo: organização do serviço, recursos disponíveis, procedimentos operacionais, coordenação com outros serviços, exercícios simulados. Atualizar periodicamente.",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.1101",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "PCINC documentado e atualizado, exercícios realizados conforme cronograma"
            },
            
            # C - Complementares
            {
                "code": "RBAC-153-02",
                "title": "Operações Compatíveis com a CAT",
                "description": "Requisitos para operações de aeronaves compatíveis com a categoria contraincêndio",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "min_passengers": 200000,
                "requirements": "Estabelecer procedimentos para operações de aeronaves compatíveis com a CAT. Notificar à ANAC quando aeronave maior que a CAT operar. Implementar medidas compensatórias quando necessário.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.301",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Procedimentos documentados, notificações realizadas quando aplicável"
            },
            {
                "code": "RBAC-153-03",
                "title": "Agentes Extintores para Combate a Incêndio",
                "description": "Requisitos para agentes extintores (espuma, pó químico, CO2)",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "min_passengers": 200000,
                "requirements": "Manter estoque adequado de agentes extintores conforme categoria: espuma AFFF (Aqueous Film Forming Foam) classe 3% ou 6%, pó químico (PQ) classe ABC, gás carbônico (CO2). Quantidades mínimas por categoria: CAT 1-2: mínimo 200L espuma; CAT 3-4: mínimo 500L espuma; CAT 5-7: mínimo 1000L espuma; CAT 8-9: mínimo 2000L espuma. Agentes devem estar certificados, com validade em dia e armazenados adequadamente.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.401",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Estoque adequado, agentes certificados, validade em dia"
            },
            {
                "code": "RBAC-153-05",
                "title": "Veículos de Apoio ao SESCINC",
                "description": "Requisitos para veículos de apoio (CACE, CRS)",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "min_passengers": 200000,
                "requirements": "Manter veículos de apoio conforme necessidade: CACE (Carro de Apoio ao Chefe de Equipe), CRS (Carro de Resgate e Salvamento). Equipamentos e certificação adequados.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.1301",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Veículos de apoio disponíveis e operacionais quando necessário"
            },
            {
                "code": "RBAC-153-09",
                "title": "Equipamentos de Uso do SESCINC",
                "description": "Requisitos para EPI, EPR, trajes de proteção e equipamentos de resgate",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Manter equipamentos adequados: EPI (Equipamento de Proteção Individual), EPR (Equipamento de Proteção Respiratória), TP (Traje de Proteção), ferramentas de resgate, equipamentos médicos básicos. Manutenção e inspeção regular.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.901",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Equipamentos disponíveis, certificados e em bom estado de conservação"
            },
            {
                "code": "RBAC-153-10",
                "title": "Programa de Treinamento Recorrente para Bombeiro de Aeródromo (PTR-BA)",
                "description": "Requisitos para programa de treinamento recorrente",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Implementar PTR-BA com treinamento teórico e prático. Frequência mínima anual. Conteúdo: combate a incêndio, resgate, uso de equipamentos, procedimentos operacionais. Registrar treinamentos e avaliar desempenho.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.1001",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "PTR-BA implementado, treinamentos realizados conforme cronograma, registros atualizados"
            },
            {
                "code": "RBAC-153-12",
                "title": "Infraestrutura da Seção Contraincêndio (SCI)",
                "description": "Requisitos para infraestrutura da seção contraincêndio",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "min_passengers": 200000,
                "requirements": "Manter SCI com localização estratégica, dimensões mínimas conforme RBAC-153 (área mínima variável por categoria), equipamentos e facilidades adequadas: garagem para CCI e veículos de apoio, sala de comando, vestiários, depósito de agentes extintores, área de manutenção. Acesso rápido às pistas e áreas críticas (ACT) com tempo de resposta adequado. Localização deve permitir acesso a todas as áreas críticas do aeródromo.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.1201",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "SCI adequada, localização estratégica, facilidades operacionais"
            },
            {
                "code": "RBAC-153-14",
                "title": "Informações ao Órgão Regulador (ANAC)",
                "description": "Requisitos para comunicação com a ANAC sobre SESCINC",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "requirements": "Notificar à ANAC sobre mudanças na CAT, atualizações do PCINC, resultados de exercícios simulados, registro de incidentes. Manter comunicação regular através do SEI! ANAC.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.1401",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Notificações realizadas conforme exigências, comunicação regular mantida"
            },
            
            # B - Recomendadas
            {
                "code": "RBAC-153-13",
                "title": "Posto Avançado de Contraincêndio (PACI)",
                "description": "Requisitos para postos avançados em aeroportos grandes",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
                "min_passengers": 1000000,
                "requirements": "Estabelecer PACI em pontos estratégicos do aeródromo para aeroportos grandes/internacionais. Localização adequada, equipamentos básicos, comunicação com SCI.",
                "requirement_classification": RequirementClassification.B,
                "weight": 4,
                "anac_reference": "RBAC 153.1203",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "PACI estabelecido em pontos estratégicos, equipamentos disponíveis"
            },
        ]
        
        # Adicionar apenas as normas que não existem
        added_count = 0
        skipped_count = 0
        
        for reg_data in rbac153_regulations:
            # Verificar se a norma já existe
            existing = db.query(Regulation).filter(
                Regulation.code == reg_data["code"]
            ).first()
            
            if existing:
                print(f"⚠️  Norma {reg_data['code']} já existe. Pulando...")
                skipped_count += 1
                continue
            
            # Criar nova norma
            regulation = Regulation(**reg_data)
            db.add(regulation)
            added_count += 1
            print(f"✅ Adicionada: {reg_data['code']} - {reg_data['title']}")
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Migração concluída!")
        print(f"   Adicionadas: {added_count} normas")
        print(f"   Já existiam: {skipped_count} normas")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Migração: Adicionar Normas RBAC-153")
    print("="*60)
    add_rbac153_regulations()

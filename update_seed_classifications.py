"""
Script para atualizar as classificações ANAC nas normas existentes.
Execute este script após recriar o banco de dados.
"""
from app.database import SessionLocal
from app.models import Regulation, RequirementClassification, EvaluationType

def update_regulation_classifications():
    """Atualiza as classificações D/C/B/A, pesos e referências ANAC para todas as normas."""
    db = SessionLocal()
    
    try:
        # Mapeamento de classificações por código de norma
        classifications = {
            # D - Essenciais (críticos, peso 8-10)
            "RBAC-154-02": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 154.323(a)", "eval": EvaluationType.BOTH, "perf": "Registro de incidentes atualizado, pessoal treinado, inspeções realizadas"},
            "RBAC-154-10": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 154.401", "eval": EvaluationType.TOPS, "perf": "Equipe SCIR disponível 24/7, tempo de resposta ≤ 3min"},
            "RBAC-154-11": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 154.403", "eval": EvaluationType.BOTH, "perf": "Equipamentos certificados e operacionais"},
            "RBAC-154-20": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 154.501", "eval": EvaluationType.BOTH, "perf": "Programa AVSEC documentado e implementado"},
            "RBAC-154-21": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 154.503", "eval": EvaluationType.BOTH, "perf": "Controles alfandegários e de imigração operacionais"},
            "RBAC-154-30": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 154.201", "eval": EvaluationType.TOPS, "perf": "Pistas e pátios em condições operacionais"},
            "RBAC-154-32": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 154.203", "eval": EvaluationType.BOTH, "perf": "Sinalização conforme padrões ICAO"},
            "RBAC-154-33": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.205", "eval": EvaluationType.TOPS, "perf": "Iluminação operacional para operações noturnas"},
            "RBAC-154-40": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 154.601", "eval": EvaluationType.BOTH, "perf": "Plano de emergência documentado e testado"},
            "RBAC-154-42": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.603", "eval": EvaluationType.TOPS, "perf": "Sistema de comunicação de emergência operacional"},
            "RBAC-154-60": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.701", "eval": EvaluationType.BOTH, "perf": "Programa de fauna documentado e implementado"},
            "RBAC-154-61": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.703", "eval": EvaluationType.TOPS, "perf": "Inspeções diárias realizadas"},
            "RBAC-154-70": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.801", "eval": EvaluationType.BOTH, "perf": "Programa de manutenção preventiva implementado"},
            "RBAC-154-80": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 154.901", "eval": EvaluationType.BOTH, "perf": "Pessoal certificado e atualizado"},
            "RBAC-154-03": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 154.325", "eval": EvaluationType.BOTH, "perf": "Sistema de investigação de incidentes operacional"},
            "RBAC-154-04": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.327", "eval": EvaluationType.BOTH, "perf": "Programa de treinamento implementado"},
            "RBAC-154-82": {"class": RequirementClassification.D, "weight": 8, "ref": "RBAC 154.903", "eval": EvaluationType.BOTH, "perf": "Todos os funcionários treinados"},
            
            # C - Complementares (importantes, peso 5-7)
            "RBAC-154-01": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 154.301", "eval": EvaluationType.BOTH, "perf": "SMS implementado e auditado"},
            "RBAC-154-05": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.303", "eval": EvaluationType.BOTH, "perf": "Gestão de riscos documentada"},
            "RBAC-154-12": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 154.405", "eval": EvaluationType.BOTH, "perf": "Categoria SCIR adequada à maior aeronave"},
            "RBAC-154-13": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.407", "eval": EvaluationType.BOTH, "perf": "Sistema de detecção operacional"},
            "RBAC-154-22": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.505", "eval": EvaluationType.BOTH, "perf": "Controle de acesso implementado"},
            "RBAC-154-23": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 154.507", "eval": EvaluationType.TOPS, "perf": "Inspeção de bagagens operacional"},
            "RBAC-154-31": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.207", "eval": EvaluationType.BOTH, "perf": "Infraestrutura adequada para aeronaves grandes"},
            "RBAC-154-34": {"class": RequirementClassification.C, "weight": 5, "ref": "RBAC 154.209", "eval": EvaluationType.TOPS, "perf": "Sistema de drenagem funcional"},
            "RBAC-154-41": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.605", "eval": EvaluationType.BOTH, "perf": "Equipamentos de resgate disponíveis"},
            "RBAC-154-43": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.607", "eval": EvaluationType.TOPS, "perf": "Exercícios realizados conforme cronograma"},
            "RBAC-154-50": {"class": RequirementClassification.C, "weight": 5, "ref": "RBAC 154.801", "eval": EvaluationType.BOTH, "perf": "Plano ambiental implementado"},
            "RBAC-154-52": {"class": RequirementClassification.C, "weight": 5, "ref": "RBAC 154.803", "eval": EvaluationType.BOTH, "perf": "Gestão de resíduos implementada"},
            "RBAC-154-62": {"class": RequirementClassification.C, "weight": 5, "ref": "RBAC 154.705", "eval": EvaluationType.BOTH, "perf": "Medidas preventivas implementadas"},
            "RBAC-154-71": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.803", "eval": EvaluationType.BOTH, "perf": "Facilidades certificadas"},
            "RBAC-154-72": {"class": RequirementClassification.C, "weight": 5, "ref": "RBAC 154.805", "eval": EvaluationType.BOTH, "perf": "Calibrações em dia"},
            "RBAC-154-73": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.807", "eval": EvaluationType.BOTH, "perf": "Manutenção preventiva realizada"},
            "RBAC-154-81": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 154.905", "eval": EvaluationType.BOTH, "perf": "Supervisores certificados"},
            "RBAC-154-90": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 154.1001", "eval": EvaluationType.BOTH, "perf": "Serviços ATC certificados"},
            "RBAC-154-91": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 154.1003", "eval": EvaluationType.BOTH, "perf": "Equipamentos de navegação certificados"},
            "RBAC-154-92": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 154.1005", "eval": EvaluationType.TOPS, "perf": "Comunicações VHF operacionais"},
            
            # B - Recomendadas (práticas recomendadas, peso 3-5)
            "RBAC-154-35": {"class": RequirementClassification.B, "weight": 4, "ref": "RBAC 154.211", "eval": EvaluationType.BOTH, "perf": "Infraestrutura de carga adequada"},
            
            # A - Melhores práticas (estado da arte, peso 1-3)
            "RBAC-154-24": {"class": RequirementClassification.A, "weight": 3, "ref": "RBAC 154.509", "eval": EvaluationType.BOTH, "perf": "Sistema avançado de proteção perimétrica com IA e câmeras inteligentes"},
            "RBAC-154-51": {"class": RequirementClassification.A, "weight": 2, "ref": "RBAC 154.805", "eval": EvaluationType.BOTH, "perf": "Sistema avançado de monitoramento contínuo de ruído com análise preditiva"},
            "RBAC-154-53": {"class": RequirementClassification.A, "weight": 2, "ref": "RBAC 154.807", "eval": EvaluationType.BOTH, "perf": "Sistema avançado de controle de emissões com tecnologias de ponta"},
            
            # ============================================
            # RBAC-153: SESCINC Classifications
            # ============================================
            
            # D - Essenciais (críticos, peso 8-10)
            "RBAC-153-01": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "CAT determinada e documentada, notificação à ANAC quando houver mudança"},
            "RBAC-153-04": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "CCI certificado e operacional, adequado à categoria, manutenção em dia"},
            "RBAC-153-06": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 153.XXX", "eval": EvaluationType.TOPS, "perf": "Equipe completa e disponível 24/7, pessoal certificado, composição adequada à categoria"},
            "RBAC-153-07": {"class": RequirementClassification.D, "weight": 10, "ref": "RBAC 153.XXX", "eval": EvaluationType.TOPS, "perf": "Tempo-resposta ≤ 3min, aferições realizadas regularmente, registros documentados"},
            "RBAC-153-08": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "100% do pessoal certificado, certificações válidas, registro atualizado"},
            "RBAC-153-11": {"class": RequirementClassification.D, "weight": 9, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "PCINC documentado e atualizado, exercícios realizados conforme cronograma"},
            
            # C - Complementares (importantes, peso 5-7)
            "RBAC-153-02": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "Procedimentos documentados, notificações realizadas quando aplicável"},
            "RBAC-153-03": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "Estoque adequado, agentes certificados, validade em dia"},
            "RBAC-153-05": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "Veículos de apoio disponíveis e operacionais quando necessário"},
            "RBAC-153-09": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "Equipamentos disponíveis, certificados e em bom estado de conservação"},
            "RBAC-153-10": {"class": RequirementClassification.C, "weight": 7, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "PTR-BA implementado, treinamentos realizados conforme cronograma, registros atualizados"},
            "RBAC-153-12": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "SCI adequada, localização estratégica, facilidades operacionais"},
            "RBAC-153-14": {"class": RequirementClassification.C, "weight": 6, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "Notificações realizadas conforme exigências, comunicação regular mantida"},
            
            # B - Recomendadas (práticas recomendadas, peso 3-5)
            "RBAC-153-13": {"class": RequirementClassification.B, "weight": 4, "ref": "RBAC 153.XXX", "eval": EvaluationType.BOTH, "perf": "PACI estabelecido em pontos estratégicos, equipamentos disponíveis"},
        }
        
        updated = 0
        for code, data in classifications.items():
            regulation = db.query(Regulation).filter(Regulation.code == code).first()
            if regulation:
                regulation.requirement_classification = data["class"]
                regulation.weight = data["weight"]
                regulation.anac_reference = data["ref"]
                regulation.evaluation_type = data["eval"]
                regulation.expected_performance = data.get("perf")
                updated += 1
        
        db.commit()
        print(f"✅ Atualizadas {updated} normas com classificações ANAC")
        
        # Verificar quantas normas ainda não têm classificação
        total = db.query(Regulation).count()
        with_class = db.query(Regulation).filter(Regulation.requirement_classification.isnot(None)).count()
        print(f"Total de normas: {total}")
        print(f"Com classificação: {with_class} ({with_class/total*100:.1f}%)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar classificações: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_regulation_classifications()

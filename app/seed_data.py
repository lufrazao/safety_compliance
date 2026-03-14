"""
Seed script to populate initial ANAC regulations and sample data.
Based on ANAC RBAC standards and safety requirements.
"""
from app.database import SessionLocal, init_db
from app.models import (
    Airport, ANACAirport, Regulation, AirportSize, AirportType, SafetyCategory,
    RequirementClassification, EvaluationType
)
import json

# Bootstrap: principais aeroportos brasileiros para lookup imediato (reference_code, category, usage_class, avsec, pistas)
ANAC_AIRPORTS_BOOTSTRAP = [
    {"code": "SBGR", "name": "Aeroporto Internacional de São Paulo/Guarulhos", "reference_code": "4E", "category": "9C", "city": "Guarulhos", "state": "SP", "usage_class": "IV", "avsec_classification": "AP-3", "number_of_runways": 2},
    {"code": "SBRJ", "name": "Aeroporto Santos Dumont", "reference_code": "4C", "category": "6C", "city": "Rio de Janeiro", "state": "RJ", "usage_class": "IV", "avsec_classification": "AP-3", "number_of_runways": 2},
    {"code": "SBGL", "name": "Aeroporto Internacional do Rio de Janeiro/Galeão", "reference_code": "4E", "category": "8C", "city": "Rio de Janeiro", "state": "RJ", "usage_class": "IV", "avsec_classification": "AP-3", "number_of_runways": 2},
    {"code": "SBCF", "name": "Aeroporto Internacional de Belo Horizonte/Confins", "reference_code": "4E", "category": "7C", "city": "Confins", "state": "MG", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBBR", "name": "Aeroporto Internacional de Brasília", "reference_code": "4E", "category": "8C", "city": "Brasília", "state": "DF", "usage_class": "IV", "avsec_classification": "AP-3", "number_of_runways": 2},
    {"code": "SBSP", "name": "Aeroporto de São Paulo/Congonhas", "reference_code": "4C", "category": "7C", "city": "São Paulo", "state": "SP", "usage_class": "IV", "avsec_classification": "AP-3", "number_of_runways": 2},
    {"code": "SBPA", "name": "Aeroporto Internacional Salgado Filho", "reference_code": "4E", "category": "6C", "city": "Porto Alegre", "state": "RS", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBSV", "name": "Aeroporto Internacional de Salvador", "reference_code": "4E", "category": "6C", "city": "Salvador", "state": "BA", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBFZ", "name": "Aeroporto Internacional Pinto Martins", "reference_code": "4C", "category": "5C", "city": "Fortaleza", "state": "CE", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBCG", "name": "Aeroporto Internacional de Campo Grande", "reference_code": "4C", "category": "4C", "city": "Campo Grande", "state": "MS", "usage_class": "II", "avsec_classification": "AP-1", "number_of_runways": 1},
    {"code": "SBCT", "name": "Aeroporto Internacional Afonso Pena", "reference_code": "4E", "category": "6C", "city": "São José dos Pinhais", "state": "PR", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBFL", "name": "Aeroporto Internacional Hercílio Luz", "reference_code": "4C", "category": "5C", "city": "Florianópolis", "state": "SC", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBNT", "name": "Aeroporto Internacional Augusto Severo", "reference_code": "4C", "category": "5C", "city": "Natal", "state": "RN", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBKP", "name": "Aeroporto Internacional de Campinas/Viracopos", "reference_code": "4E", "category": "7C", "city": "Campinas", "state": "SP", "usage_class": "IV", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBEG", "name": "Aeroporto Internacional de Manaus", "reference_code": "4E", "category": "5C", "city": "Manaus", "state": "AM", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    # Aeroportos adicionais
    {"code": "SBRF", "name": "Aeroporto Internacional dos Guararapes", "reference_code": "4E", "category": "6C", "city": "Recife", "state": "PE", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBPV", "name": "Aeroporto Eurico de Aguiar Salles", "reference_code": "4C", "category": "5C", "city": "Vitória", "state": "ES", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBAR", "name": "Aeroporto Internacional Santa Maria", "reference_code": "4C", "category": "5C", "city": "Aracaju", "state": "SE", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBMO", "name": "Aeroporto Internacional Zumbi dos Palmares", "reference_code": "4C", "category": "5C", "city": "Maceió", "state": "AL", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBCY", "name": "Aeroporto Internacional de Cuiabá", "reference_code": "4E", "category": "5C", "city": "Cuiabá", "state": "MT", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBLO", "name": "Aeroporto Governador José Richa", "reference_code": "4C", "category": "5C", "city": "Londrina", "state": "PR", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBRP", "name": "Aeroporto Leite Lopes", "reference_code": "4C", "category": "4C", "city": "Ribeirão Preto", "state": "SP", "usage_class": "II", "avsec_classification": "AP-1", "number_of_runways": 1},
    {"code": "SBMA", "name": "Aeroporto de Marabá", "reference_code": "4C", "category": "4C", "city": "Marabá", "state": "PA", "usage_class": "II", "avsec_classification": "AP-1", "number_of_runways": 1},
    {"code": "SBBE", "name": "Aeroporto Internacional de Belém", "reference_code": "4E", "category": "6C", "city": "Belém", "state": "PA", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBPB", "name": "Aeroporto Internacional Presidente Castro Pinto", "reference_code": "4C", "category": "5C", "city": "João Pessoa", "state": "PB", "usage_class": "III", "avsec_classification": "AP-2", "number_of_runways": 1},
    {"code": "SBUL", "name": "Aeroporto de Uberlândia", "reference_code": "4C", "category": "4C", "city": "Uberlândia", "state": "MG", "usage_class": "II", "avsec_classification": "AP-1", "number_of_runways": 1},
    {"code": "SBCN", "name": "Aeroporto de Corumbá", "reference_code": "3C", "category": "3C", "city": "Corumbá", "state": "MS", "usage_class": "I", "avsec_classification": "AP-1", "number_of_runways": 1},
]


def seed_regulations(update_existing=False):
    """Seed initial ANAC regulations based on airport variables.

    Args:
        update_existing: Se True, atualiza regulações existentes com os dados do seed.
    """
    db = SessionLocal()

    try:
        existing_codes = {r.code for r in db.query(Regulation.code).all()}
        
        regulations = [
            # Operational Safety - applies to all airports
            {
                "code": "RBAC-154-01",
                "title": "Sistema de Gerenciamento de Segurança Operacional (SMS)",
                "description": "Estabelece requisitos para implementação de Sistema de Gerenciamento de Segurança Operacional",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Implementar SMS completo com política de segurança, gestão de riscos, garantia de segurança e promoção da segurança. Realizar auditorias anuais.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 154.301",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "SMS implementado e auditado anualmente"
            },
            {
                "code": "RBAC-154-02",
                "title": "Requisitos Básicos de Segurança Operacional",
                "description": "Requisitos mínimos de segurança operacional para todos os aeroportos",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Manter registro de incidentes, treinamento básico de pessoal, inspeções regulares de pistas e áreas de movimento.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 154.323(a)",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Registro de incidentes atualizado, pessoal treinado, inspeções realizadas"
            },
            
            # Fire Safety
            {
                "code": "RBAC-154-10",
                "title": "Serviço de Combate a Incêndio e Resgate (SCIR)",
                "description": "Requisitos para serviço de combate a incêndio baseado na categoria do aeroporto",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "min_passengers": None,
                "requirements": "Manter equipe de SCIR com equipamentos adequados à categoria do aeroporto. Tempo de resposta máximo de 3 minutos para aeroportos comerciais."
            },
            {
                "code": "RBAC-154-11",
                "title": "Equipamentos de Combate a Incêndio",
                "description": "Especificações de equipamentos de combate a incêndio",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Manter veículos de combate a incêndio certificados, extintores em todas as áreas, sistema de hidrantes operacional."
            },
            
            # Security (AVSEC)
            {
                "code": "RBAC-154-20",
                "title": "Programa de Segurança da Aviação Civil (AVSEC)",
                "description": "Requisitos de segurança da aviação civil",
                "safety_category": SafetyCategory.SECURITY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "requires_international": False,
                "min_passengers": 200000,
                "requirements": "Implementar programa AVSEC, controle de acesso, inspeção de bagagens, treinamento de pessoal de segurança."
            },
            {
                "code": "RBAC-154-21",
                "title": "Segurança para Operações Internacionais",
                "description": "Requisitos adicionais de segurança para aeroportos com operações internacionais",
                "safety_category": SafetyCategory.SECURITY,
                "requires_international": True,
                "requirements": "Controle alfandegário, inspeção de imigração, área de quarentena, sistema de rastreamento de bagagens."
            },
            
            # Infrastructure
            {
                "code": "RBAC-154-30",
                "title": "Manutenção de Pistas e Pátios",
                "description": "Requisitos de manutenção de infraestrutura aeroportuária",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Inspeções diárias de pistas, manutenção preventiva de pátios, sinalização adequada, iluminação operacional."
            },
            {
                "code": "RBAC-154-31",
                "title": "Infraestrutura para Aeronaves de Grande Porte",
                "description": "Requisitos para aeroportos que recebem aeronaves de grande porte",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "min_aircraft_weight": 100,
                "requirements": "Pistas com largura mínima de 45m, pátios com capacidade adequada, equipamentos de movimentação de aeronaves."
            },
            
            # Emergency Response
            {
                "code": "RBAC-154-40",
                "title": "Plano de Emergência Aeroportuária",
                "description": "Requisitos para plano de emergência e resposta a acidentes",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Plano de emergência documentado, exercícios simulados anuais, coordenação com órgãos externos (bombeiros, polícia, saúde)."
            },
            {
                "code": "RBAC-154-41",
                "title": "Equipamentos de Resgate",
                "description": "Equipamentos necessários para resposta a emergências",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["large", "international"]),
                "min_passengers": 1000000,
                "requirements": "Ambulâncias, equipamentos de resgate, área médica no terminal, comunicação de emergência."
            },
            
            # Environmental
            {
                "code": "RBAC-154-50",
                "title": "Gestão Ambiental",
                "description": "Requisitos ambientais para operação aeroportuária",
                "safety_category": SafetyCategory.ENVIRONMENTAL,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Plano de gestão ambiental, monitoramento de ruído, gestão de resíduos, controle de emissões."
            },
            
            # Wildlife Management
            {
                "code": "RBAC-154-60",
                "title": "Gerenciamento de Fauna",
                "description": "Programa de gerenciamento de fauna para prevenção de colisões",
                "safety_category": SafetyCategory.WILDLIFE_MANAGEMENT,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Programa de gerenciamento de fauna, inspeções regulares, registro de ocorrências, medidas preventivas."
            },
            
            # Maintenance
            {
                "code": "RBAC-154-70",
                "title": "Manutenção de Equipamentos",
                "description": "Requisitos para manutenção de equipamentos aeroportuários",
                "safety_category": SafetyCategory.MAINTENANCE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Programa de manutenção preventiva, registro de manutenções, calibração de equipamentos críticos."
            },
            {
                "code": "RBAC-154-71",
                "title": "Facilidades de Manutenção Aeronáutica",
                "description": "Requisitos para aeroportos com facilidades de manutenção",
                "safety_category": SafetyCategory.MAINTENANCE,
                "requires_maintenance": True,
                "requirements": "Hangares certificados, equipamentos de manutenção certificados, pessoal qualificado, controle de ferramentas."
            },
            
            # Personnel Certification
            {
                "code": "RBAC-154-80",
                "title": "Certificação de Pessoal",
                "description": "Requisitos de certificação e treinamento de pessoal",
                "safety_category": SafetyCategory.PERSONNEL_CERTIFICATION,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Pessoal certificado pela ANAC quando aplicável, treinamentos regulares, registro de qualificações."
            },
            
            # Air Traffic Services
            {
                "code": "RBAC-154-90",
                "title": "Serviços de Tráfego Aéreo",
                "description": "Requisitos para aeroportos com serviços de tráfego aéreo",
                "safety_category": SafetyCategory.AIR_TRAFFIC_SERVICES,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Torre de controle certificada, equipamentos de comunicação e navegação, pessoal ATC certificado."
            },
            
            # Additional Operational Safety regulations
            {
                "code": "RBAC-154-03",
                "title": "Investigação de Incidentes e Acidentes",
                "description": "Requisitos para investigação e registro de incidentes",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Sistema de registro e investigação de incidentes, notificação à ANAC dentro de 24 horas para incidentes graves, relatórios anuais."
            },
            {
                "code": "RBAC-154-04",
                "title": "Treinamento de Pessoal Operacional",
                "description": "Requisitos de treinamento para pessoal operacional",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Programa de treinamento inicial e reciclagem anual, certificação de instrutores, registro de treinamentos realizados."
            },
            {
                "code": "RBAC-154-05",
                "title": "Gestão de Riscos Operacionais",
                "description": "Sistema de gestão de riscos para aeroportos médios e grandes",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Identificação de perigos, avaliação de riscos, implementação de medidas de mitigação, revisão periódica."
            },
            
            # Additional Fire Safety regulations
            {
                "code": "RBAC-154-12",
                "title": "Categoria de SCIR por Tamanho de Aeronave",
                "description": "Categorização do serviço de combate a incêndio baseado no maior aeronave",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Categoria SCIR determinada pela maior aeronave que opera regularmente. Pequenos: Categoria 1-2, Médios: Categoria 3-4, Grandes: Categoria 5-7, Internacionais: Categoria 7-9."
            },
            {
                "code": "RBAC-154-13",
                "title": "Sistema de Detecção e Alarme de Incêndio",
                "description": "Requisitos para sistemas de detecção de incêndio",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Sistema de detecção automática de incêndio em terminais, hangares e áreas críticas, alarmes sonoros e visuais, integração com central de monitoramento."
            },
            
            # Additional Security regulations
            {
                "code": "RBAC-154-22",
                "title": "Controle de Acesso a Áreas Restritas",
                "description": "Requisitos para controle de acesso",
                "safety_category": SafetyCategory.SECURITY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Sistema de controle de acesso com credenciais, registro de entrada/saída, vigilância de áreas restritas, treinamento de pessoal de segurança."
            },
            {
                "code": "RBAC-154-23",
                "title": "Inspeção de Bagagens e Passageiros",
                "description": "Requisitos para inspeção de segurança",
                "safety_category": SafetyCategory.SECURITY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Equipamentos de raio-X para bagagens, detectores de metais, inspeção manual quando necessário, pessoal treinado e certificado."
            },
            {
                "code": "RBAC-154-24",
                "title": "Proteção Perimétrica",
                "description": "Requisitos para proteção do perímetro aeroportuário",
                "safety_category": SafetyCategory.SECURITY,
                "applies_to_sizes": json.dumps(["large", "international"]),
                "min_passengers": 1000000,
                "requirements": "Cerca perimétrica adequada, iluminação noturna, sistema de vigilância (câmeras), patrulhamento regular."
            },
            
            # Additional Infrastructure regulations
            {
                "code": "RBAC-154-32",
                "title": "Sinalização de Pistas e Pátios",
                "description": "Requisitos de sinalização aeronáutica",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Sinalização conforme padrões ICAO, marcações de pista visíveis, sinalização de pátio, placas de identificação, manutenção regular."
            },
            {
                "code": "RBAC-154-33",
                "title": "Iluminação de Pistas e Pátios",
                "description": "Requisitos de iluminação para operações noturnas",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Sistema de iluminação de pista operacional, iluminação de pátio adequada, sistema de backup para emergências, manutenção preventiva."
            },
            {
                "code": "RBAC-154-34",
                "title": "Drenagem e Controle de Água",
                "description": "Requisitos para drenagem aeroportuária",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Sistema de drenagem adequado, inspeções após chuvas, manutenção de canais e bueiros, prevenção de alagamentos."
            },
            {
                "code": "RBAC-154-35",
                "title": "Infraestrutura para Operações de Carga",
                "description": "Requisitos para aeroportos com operações de carga",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "requires_cargo": True,
                "requirements": "Área de carga coberta, equipamentos de movimentação de carga, armazenamento adequado, controle de temperatura quando necessário."
            },
            
            # Additional Emergency Response regulations
            {
                "code": "RBAC-154-42",
                "title": "Comunicação de Emergência",
                "description": "Sistemas de comunicação para emergências",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Sistema de comunicação de emergência, rádios para equipes de resposta, coordenação com serviços externos, testes mensais."
            },
            {
                "code": "RBAC-154-43",
                "title": "Exercícios Simulados de Emergência (ESEA)",
                "description": "Requisitos para exercícios simulados de emergência aeroportuária conforme RBAC 153.331",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Aferir todos os módulos do ESEA num ciclo não superior a 3 anos, em diferentes áreas do aeródromo e adjacências, com diferentes horários e tipos de emergências simuladas. Realizar ao menos 4 módulos por ano (1 por trimestre ou até 2 agrupados por semestre), elaborando relatório final de avaliação. Preceder exercícios com recursos externos de reuniões de planejamento com atas formais. Estabelecer procedimentos padronizados para execução e avaliação do ESEA.",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.331",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "ESEA executado conforme ciclo, módulos trimestrais, relatórios de avaliação"
            },
            
            # Additional Environmental regulations
            {
                "code": "RBAC-154-51",
                "title": "Monitoramento de Ruído",
                "description": "Requisitos para monitoramento de ruído aeronáutico",
                "safety_category": SafetyCategory.ENVIRONMENTAL,
                "applies_to_sizes": json.dumps(["large", "international"]),
                "min_passengers": 1000000,
                "requirements": "Sistema de monitoramento de ruído, relatórios trimestrais, medidas de mitigação quando necessário, comunicação com comunidades vizinhas."
            },
            {
                "code": "RBAC-154-52",
                "title": "Gestão de Resíduos",
                "description": "Requisitos para gestão de resíduos aeroportuários",
                "safety_category": SafetyCategory.ENVIRONMENTAL,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Plano de gestão de resíduos, separação de resíduos, destinação adequada, registro de resíduos perigosos."
            },
            {
                "code": "RBAC-154-53",
                "title": "Controle de Emissões",
                "description": "Requisitos para controle de emissões atmosféricas",
                "safety_category": SafetyCategory.ENVIRONMENTAL,
                "applies_to_sizes": json.dumps(["large", "international"]),
                "min_passengers": 1000000,
                "requirements": "Monitoramento de qualidade do ar, medidas de redução de emissões, uso de equipamentos elétricos quando possível, relatórios anuais."
            },
            
            # Additional Wildlife Management regulations
            {
                "code": "RBAC-154-61",
                "title": "Inspeções de Fauna",
                "description": "Requisitos para inspeções regulares de fauna",
                "safety_category": SafetyCategory.WILDLIFE_MANAGEMENT,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Inspeções diárias antes das primeiras operações, registro de avistamentos, medidas de dispersão, relatórios mensais à ANAC."
            },
            {
                "code": "RBAC-154-62",
                "title": "Medidas Preventivas de Fauna",
                "description": "Requisitos para medidas preventivas contra fauna",
                "safety_category": SafetyCategory.WILDLIFE_MANAGEMENT,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Controle de vegetação, remoção de fontes de alimento, uso de equipamentos de dispersão, coordenação com órgãos ambientais."
            },
            
            # Additional Maintenance regulations
            {
                "code": "RBAC-154-72",
                "title": "Calibração de Equipamentos Críticos",
                "description": "Requisitos para calibração de equipamentos",
                "safety_category": SafetyCategory.MAINTENANCE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Calibração anual de equipamentos críticos (balanças, medidores, etc.), certificados de calibração, registro de histórico."
            },
            {
                "code": "RBAC-154-73",
                "title": "Manutenção de Equipamentos de Segurança",
                "description": "Requisitos específicos para equipamentos de segurança",
                "safety_category": SafetyCategory.MAINTENANCE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Manutenção preventiva de equipamentos de segurança (detectores, câmeras, etc.), testes semanais, registro de manutenções."
            },
            
            # Additional Personnel Certification regulations
            {
                "code": "RBAC-154-81",
                "title": "Certificação de Supervisores de Operação",
                "description": "Requisitos para supervisores operacionais",
                "safety_category": SafetyCategory.PERSONNEL_CERTIFICATION,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Supervisores certificados pela ANAC, reciclagem a cada 2 anos, registro de certificações, experiência mínima de 3 anos."
            },
            {
                "code": "RBAC-154-82",
                "title": "Treinamento de Segurança para Funcionários",
                "description": "Requisitos de treinamento de segurança para todos os funcionários",
                "safety_category": SafetyCategory.PERSONNEL_CERTIFICATION,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "requirements": "Treinamento inicial de segurança para todos os funcionários, reciclagem anual, certificação de conclusão, registro de treinamentos."
            },
            
            # Additional Air Traffic Services regulations
            {
                "code": "RBAC-154-91",
                "title": "Equipamentos de Navegação",
                "description": "Requisitos para equipamentos de navegação aérea",
                "safety_category": SafetyCategory.AIR_TRAFFIC_SERVICES,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Equipamentos de navegação certificados (ILS, VOR, NDB quando aplicável), calibração regular, sistema de backup."
            },
            {
                "code": "RBAC-154-92",
                "title": "Comunicações Aéreas",
                "description": "Requisitos para sistemas de comunicação aérea",
                "safety_category": SafetyCategory.AIR_TRAFFIC_SERVICES,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Sistema de comunicação VHF operacional, frequências certificadas, sistema de backup, testes diários."
            },
            
            # ============================================
            # RBAC-153: SESCINC (Serviço de Salvamento e Combate a Incêndio)
            # ============================================
            
            # D - Essenciais
            {
                "code": "RBAC-153-01",
                "title": "Determinação da CAT (Categoria Contraincêndio) do Aeródromo",
                "description": "Requisitos para determinação da categoria contraincêndio baseada na maior aeronave que opera regularmente",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Determinar a CAT do aeródromo baseada na maior aeronave que opera regularmente (conforme tabela 153.403-1). Categorias de 1 a 9. Documentar e notificar à ANAC mudanças de CAT. Quando redução estrutural de recursos forçar queda de CAT, comunicar imediatamente à ANAC (gtre.sia@anac.gov.br) e às companhias aéreas operadoras.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.403",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "CAT determinada e documentada, notificação à ANAC quando houver mudança"
            },
            {
                "code": "RBAC-153-04",
                "title": "Carro Contraincêndio de Aeródromo (CCI)",
                "description": "Requisitos para veículos de combate a incêndio conforme categoria do aeródromo",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter CCI adequado à categoria do aeródromo conforme tabela 153.407-1. Requisitos técnicos obrigatórios (FC): tração fora-de-estrada; mangueiras de incêndio conforme ABNT NBR 11861; assento para bombeiro (BA) com suporte para EPR. Desempenho mínimo: aceleração de 0 a 80 km/h em ≤30s (tanque <2000L), ≤25s (tanque 2000-6000L), ≤35s (tanque >6000L); velocidade máxima ≥110 km/h. Capacidade de água e espuma conforme categoria. Manutenção e certificação regulares.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.407",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "CCI certificado e operacional, adequado à categoria, manutenção em dia"
            },
            {
                "code": "RBAC-153-06",
                "title": "Equipe de Serviço do SESCINC",
                "description": "Requisitos para composição e disponibilidade da equipe de serviço do SESCINC",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter equipe de serviço do SESCINC com composição mínima conforme categoria. Composição por CAT: CAT 1-2: mínimo 2 BA; CAT 3-4: mínimo 3 BA; CAT 5-6: mínimo 4 BA; CAT 7-8: mínimo 5 BA; CAT 9: mínimo 6 BA. Funções obrigatórias: BA-CE (Chefe de Equipe), BA-LR (Líder de Resgate), BA-MC (Motorista/Operador de CCI), BA-RE (Resgatista). Todas as funções operacionais devem ser desempenhadas exclusivamente por profissionais aprovados conforme cursos do 153.417(a). Disponibilidade 24/7 para aeroportos comerciais.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.417",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Equipe completa e disponível 24/7, pessoal certificado, composição adequada à categoria"
            },
            {
                "code": "RBAC-153-07",
                "title": "Tempo-Resposta do SESCINC",
                "description": "Requisitos para tempo de resposta do serviço de combate a incêndio",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Tempo de resposta máximo de 3 minutos a qualquer ponto das pistas, em condições ótimas de visibilidade e superfície (RBAC 153.409(a)). Medição: da ativação inicial do SESCINC até estabilização do jato de água no ponto mais distante das pistas. Aferições trimestrais obrigatórias [FC 153.409(c)]. Registro obrigatório deve conter: data/hora, equipe, veículos utilizados e hora de chegada de cada veículo ao ponto mais distante. Objetivo recomendado: 2 minutos.",
                "requirement_classification": RequirementClassification.D,
                "weight": 10,
                "anac_reference": "RBAC 153.409",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Tempo-resposta ≤ 3min, aferições realizadas regularmente, registros documentados"
            },
            {
                "code": "RBAC-153-08",
                "title": "Capacitação de Recursos Humanos para o SESCINC",
                "description": "Requisitos obrigatórios de capacitação para bombeiros de aeródromo",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Todo profissional operacional do SESCINC deve possuir CAP-BA (Certificado de Aptidão Profissional para Bombeiro de Aeródromo), comprovante de aprovação no curso de atualização/habilitação [FC 153.417(b)]. GS (Gerente da Seção Contraincêndio) está isento dos cursos de atualização. Condutores dos veículos devem possuir CNH compatível com veículos de emergência (recomendação). Manter registro atualizado de todas as certificações.",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.417",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "100% do pessoal certificado, certificações válidas, registro atualizado"
            },
            {
                "code": "RBAC-153-11",
                "title": "Plano Contraincêndio de Aeródromo (PCINC)",
                "description": "Requisitos para elaboração e manutenção do PCINC",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
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
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Estabelecer e controlar operações compatíveis com a CAT usando janela móvel de 3 meses consecutivos. Limites de compatibilidade [153.413(c)]: Classe II/III: até 900 movimentos/trimestre de aeronaves com CAT-AV 1 nível acima da CAT; até 26 movimentos/trimestre com CAT-AV 2 níveis acima. Classe IV: até 26 movimentos/trimestre com CAT-AV 1 nível acima da CAT. Notificar ANAC quando aeronave operar acima dos limites. Operações de carga: usar tabela de equivalência de CAT-AV.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.413",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Procedimentos documentados, notificações realizadas quando aplicável"
            },
            {
                "code": "RBAC-153-03",
                "title": "Agentes Extintores para Combate a Incêndio",
                "description": "Requisitos para agentes extintores (espuma, pó químico, CO2)",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Manter LGE (Líquido Gerador de Espuma) como agente extintor principal, com eficácia nível B ou C (classe AV), em soluções de 1%, 3% ou 6%. PQ (Pó Químico BC — bicarbonato de sódio) como agente complementar, conforme ABNT NBR 9695. Quantidades mínimas conforme tabela 153.405-1 da CAT. Recomendação: manter reserva de 100% das quantidades do CCI para testes/treinamentos; uniformizar tipo de LGE no mesmo SESCINC (evitar mistura com outros LGE de miscibilidade desconhecida). Agentes devem estar certificados, com validade em dia e armazenados adequadamente.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.405",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Estoque adequado, agentes certificados, validade em dia"
            },
            {
                "code": "RBAC-153-05",
                "title": "Veículos de Apoio ao SESCINC",
                "description": "Requisitos para veículos de apoio (CACE, CRS)",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Manter veículos de apoio conforme necessidade: CACE (Carro de Apoio ao Chefe de Equipe) — recomendado para Classe IV e Classe III com CAT 8 ou superior; CRS (Carro de Resgate e Salvamento) — recomendado para transporte da equipe de resgate. Todos os veículos devem possuir equipamentos e certificação adequados. Manutenção preventiva conforme cronograma.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.407",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Veículos de apoio disponíveis e operacionais quando necessário"
            },
            {
                "code": "RBAC-153-09",
                "title": "Equipamentos de Uso do SESCINC",
                "description": "Requisitos para EPI, EPR, trajes de proteção e equipamentos de resgate",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "TP (Traje de Proteção): todos os componentes devem possuir CA (Certificado de Aprovação) do Ministério do Trabalho [FC 153.421(a)]. EPR (Equipamento de Proteção Respiratória): tipo pressão positiva obrigatório; seguir ABNT NBR 13716; estabelecer procedimento de recarga de cilindros; reserva de cilindros recomendada. Equipamentos de resgate conforme tabela 153.423-1 por CAT. Torre de iluminação: obrigatória para Classe III e IV com CAT 6 ou superior [FC 153.423]. Sensor de inércia 'homem-morto' recomendado para operações de resgate.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.421/153.423",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Equipamentos disponíveis, certificados e em bom estado de conservação"
            },
            {
                "code": "RBAC-153-10",
                "title": "Programa de Treinamento Recorrente para Bombeiro de Aeródromo (PTR-BA)",
                "description": "Requisitos para programa de treinamento recorrente",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
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
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Manter SCI que abrigue todos os recursos do SESCINC. Requisitos obrigatórios: fornecimento de energia secundário para sistemas críticos [FC 153.219(c)(1)(ii)]; Sala de Observação exclusiva para OC com visão direta ou por câmeras de toda a área de movimento de aeronaves; reservatório de água (reservatório elevado preferencial [FC]) com válvula de abertura em 1/4 de giro e reabastecimento em ≤10 minutos; sistema de recarga contínua de baterias; sistema de recarga de ar comprimido. Localização deve permitir acesso rápido a todas as áreas críticas do aeródromo.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.425",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "SCI adequada, localização estratégica, facilidades operacionais"
            },
            {
                "code": "RBAC-153-14",
                "title": "Informações ao Órgão Regulador (ANAC)",
                "description": "Requisitos para comunicação com a ANAC sobre SESCINC",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Acionamentos do SESCINC envolvendo aeronaves: reportar à ANAC em até 5 dias úteis via sistema SACI ou e-mail gtre.sia@anac.gov.br [FC 153.431(a)]. Relatório semestral com resumo de todos os acionamentos: enviar em janeiro e julho [FC 153.431(a)(1)]. Relatório deve incluir: dados da aeronave, fase da operação, condições meteorológicas, ocupantes/vítimas, tempos (ativação, jato de água, última vítima), equipamentos e agentes utilizados. Notificar ANAC também sobre mudanças de CAT e alterações no PCINC.",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.431",
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
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 1000000,
                "requirements": "Estabelecer PACI (posto satélite da SCI) quando a localização da SCI inviabilizar o tempo-resposta de 3 minutos a alguma área do aeródromo. O PACI deve atender aos mesmos requisitos de infraestrutura da SCI (153.425). Comunicação com SCI garantida. Equipamentos básicos do SESCINC disponíveis no PACI.",
                "requirement_classification": RequirementClassification.B,
                "weight": 4,
                "anac_reference": "RBAC 153.425",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "PACI estabelecido em pontos estratégicos, equipamentos disponíveis"
            },
            
            # ============================================
            # RBAC-153: SME, COE, PCM (Classe II, III, IV - CEF 153.309, 153.301, 153.313)
            # ============================================
            {
                "code": "RBAC-153-15",
                "title": "Ambulâncias (Serviço Médico de Emergência - SME)",
                "description": "Requisitos para ambulâncias conforme RBAC 153.309 - quantidade mínima, tripulação ANVISA/MS",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Prover quantidade mínima de ambulâncias fixada em normativo, devidamente tripuladas conforme ANVISA e Ministério da Saúde, com motorista habilitado. Classe II/III: mínimo 1 ambulância; Classe IV: mínimo 2 (sendo uma tipo D). Características técnicas e operacionais conforme MS e ANVISA.",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.309",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Ambulâncias disponíveis, tripuladas e certificadas conforme normativo"
            },
            {
                "code": "RBAC-153-16",
                "title": "Centro de Operações de Emergências (COE)",
                "description": "Requisitos para COE - existência, ativação, composição e coordenação conforme RBAC 153.301/153.303",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Estabelecer e manter operacional Centro de Operações de Emergências (COE) adequado ao SREA. Garantir que todos os elementos do SREA tenham acesso às informações, procedimentos e responsabilidades. Composição conforme planejamento do SREA, testes MGI, PRAI, PLEM.",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.301/153.303",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "COE estabelecido, ativável e integrado ao SREA"
            },
            {
                "code": "RBAC-153-17",
                "title": "Posto de Comando Móvel (PCM)",
                "description": "Requisitos para PCM - locomoção, comunicação com COE, iluminação conforme RBAC 153.313",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Manter PCM interno ao aeródromo, em local de fácil acesso e rápida locomoção até o local da emergência. Sistema de comunicação imediata e segura com o COE e recursos envolvidos. Iluminação para suporte às atividades. Definir responsável pela operação no planejamento do SREA.",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.313",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "PCM disponível, comunicável com COE e operacional"
            },

            # ============================================
            # RBAC-153: Comunicação/Alarme e SESAQ
            # ============================================
            {
                "code": "RBAC-153-18",
                "title": "Sistemas de Comunicação e Alarme do SESCINC",
                "description": "Requisitos para sistemas de rádio, comunicação e alarme do SESCINC conforme RBAC 153.427",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter sistema de rádio para cada profissional operacional com cobertura mínima em toda a área operacional [FC 153.427(a)(1)]. Tipos por função: BA-CE e BA-LR: estação portátil [FC]; BA-MC no CCI: estação móvel veicular [Rec]; OC na Sala de Observação: estação fixa [Rec]; COE: estação fixa [Rec]; PCM: estação móvel veicular [Rec]. Linha telefônica exclusiva entre TWR e operador da SCI [FC 153.427(a)(2)]. Sistema de alarme audível em toda a SCI, acionável também pelo TWR [FC 153.427(b)(1)]. Avaliar extensão do alarme ao COE e demais participantes do SREA (recomendação).",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.427",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Sistemas de rádio e alarme operacionais, cobertura total da área operacional"
            },
            {
                "code": "RBAC-153-19",
                "title": "Serviço Especializado de Salvamento Aquático (SESAQ)",
                "description": "Requisitos para SESAQ em aeroportos com corpos d'água ou terrenos de difícil acesso próximos às pistas",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter SESAQ quando existirem superfícies aquáticas ou terrenos de difícil acesso dentro de 1000m dos limiares de qualquer pista (RBAC 153.301(d)(2), 153.325(a)(1), 153.325(a)(4)). O serviço pode ser provido pelo operador do aeródromo, por agências externas ou por ambos. Recursos recomendados: salva-vidas flutuantes, veículos para acomodação de vítimas, equipamentos de iluminação para operações noturnas. Treinamento deve incluir: familiarização com PLEM, familiarização com aeronaves, equipamentos de resgate, EPR, comunicações e técnicas de salvamento aquático. SESAQ é distinto do SAR (Busca e Salvamento, Anexo 12 OACI).",
                "requirement_classification": RequirementClassification.C,
                "weight": 6,
                "anac_reference": "RBAC 153.433",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "SESAQ operacional quando aplicável (corpo d'água ou terreno difícil dentro de 1000m das pistas)"
            },

            # ============================================
            # RBAC-153: Subparte B — Responsáveis e Treinamentos
            # ============================================
            {
                "code": "RBAC-153-20",
                "title": "Responsáveis pelas Atividades Operacionais",
                "description": "Designação de profissionais responsáveis conforme RBAC 153.15",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Designar profissionais responsáveis pelas atividades operacionais: gestor responsável pelo aeródromo, responsável pela segurança operacional, responsável pelas operações aeroportuárias, responsável pela manutenção, responsável pela resposta a emergências [153.15(a)]. Definir estrutura organizacional no MOPS. Enviar formulário cadastral à ANAC em até 30 dias. Acumulação de funções permitida conforme 153.15(b).",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.15",
                "evaluation_type": EvaluationType.DOCS,
                "expected_performance": "Responsáveis designados, cadastrados na ANAC, estrutura no MOPS"
            },
            {
                "code": "RBAC-153-21",
                "title": "Responsabilidades do Gestor Responsável",
                "description": "Prerrogativas e responsabilidades do gestor do aeródromo conforme RBAC 153.23",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Gestor deve: garantir cumprimento de todos os requisitos do RBAC 153; manter condições operacionais/infraestrutura; alocar recursos para objetivos de segurança; conduzir análises críticas de segurança; revisar desempenho de segurança regularmente; assegurar comunicação clara de segurança em toda organização; garantir qualificação do pessoal; assegurar integridade da segurança durante mudanças [153.23(a)].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.23",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Gestor cumprindo suas responsabilidades, análises críticas documentadas"
            },
            {
                "code": "RBAC-153-22",
                "title": "Habilitação dos Responsáveis",
                "description": "Requisitos de qualificação profissional conforme RBAC 153.35",
                "safety_category": SafetyCategory.PERSONNEL_CERTIFICATION,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Profissionais responsáveis devem ser habilitados conforme 153.35. Engenharia/manutenção com registro em conselho profissional. Condutores de veículos com CNH válida para categoria do veículo. Profissionais de manejo de fauna com formação na área ambiental.",
                "requirement_classification": RequirementClassification.D,
                "weight": 7,
                "anac_reference": "RBAC 153.35",
                "evaluation_type": EvaluationType.DOCS,
                "expected_performance": "Todos os responsáveis habilitados e com documentação em dia"
            },
            {
                "code": "RBAC-153-23",
                "title": "Programa Integrado de Segurança Operacional em Aeródromo (PISOA)",
                "description": "Programa de treinamentos obrigatórios conforme RBAC 153.37",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Implementar PISOA com 9 treinamentos obrigatórios: (1) Treinamento Geral de conscientização para pessoal da área operacional; (2) Treinamento básico de segurança operacional; (3) Condução de veículos na área operacional; (4) Acesso/permanência na área de manobras; (5) Operações em baixa visibilidade; (6) PTR-BA (bombeiros — ver RBAC-153-10); (7) Treinamento básico de operações; (8) Risco fauna; (9) Condição de pista (avaliação/reporte). Vincular credenciamento à conclusão dos treinamentos. Realizar avaliação periódica das necessidades de treinamento [153.37(f)].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.37",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "PISOA implementado, 9 treinamentos ativos, credenciamento vinculado"
            },
            {
                "code": "RBAC-153-24",
                "title": "Documentação e Informações à ANAC",
                "description": "Requisitos de documentação e controle de versões conforme RBAC 153.39",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Enviar documentos à ANAC em formato eletrônico extraível. Manter controle de versão para revisões/atualizações/emendas. Manter informações cadastrais atualizadas junto à ANAC [153.39].",
                "requirement_classification": RequirementClassification.C,
                "weight": 5,
                "anac_reference": "RBAC 153.39",
                "evaluation_type": EvaluationType.DOCS,
                "expected_performance": "Documentação em dia, controle de versões, cadastro ANAC atualizado"
            },

            # ============================================
            # RBAC-153: Subparte C — SGSO (Sistema de Gerenciamento de Segurança Operacional)
            # ============================================
            {
                "code": "RBAC-153-30",
                "title": "SGSO — Política e Objetivos de Segurança",
                "description": "Política de segurança, CSO e MGSO conforme RBAC 153.53",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Estabelecer e manter SGSO compatível com porte do aeródromo [153.51]. Definir política de segurança operacional aprovada pelo gestor. Criar Comissão de Segurança Operacional (CSO). Elaborar MGSO (Manual de Gerenciamento de Segurança Operacional) com política, objetivos mensuráveis, estrutura organizacional, responsabilidades e processos [153.53].",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.53",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "SGSO implementado, CSO ativa, MGSO aprovado e publicado"
            },
            {
                "code": "RBAC-153-31",
                "title": "SGSO — Gestão de Riscos",
                "description": "Processos de identificação de perigos e gestão de riscos conforme RBAC 153.55",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Implementar processo formal de identificação de perigos. Realizar avaliação de riscos (probabilidade × severidade). Definir e implantar controles/mitigações. Manter sistema de reporte de segurança da aviação civil. Manter biblioteca de perigos atualizada [153.55].",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.55",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Processo de gestão de riscos ativo, biblioteca de perigos mantida"
            },
            {
                "code": "RBAC-153-32",
                "title": "SGSO — Garantia de Segurança",
                "description": "Monitoramento, indicadores, auditorias e relatórios à ANAC conforme RBAC 153.57",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Manter monitoramento contínuo da segurança operacional. Definir e acompanhar indicadores de desempenho de segurança. Realizar auditorias internas do SGSO. Enviar relatórios quadrimestrais à ANAC. Implementar ações corretivas. Gerenciar mudanças (change management). Promover melhoria contínua [153.57].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.57",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Indicadores monitorados, auditorias realizadas, relatórios quadrimestrais enviados"
            },
            {
                "code": "RBAC-153-33",
                "title": "SGSO — Promoção da Segurança",
                "description": "Treinamento e comunicação de segurança conforme RBAC 153.59",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Implementar programa de treinamento em segurança operacional para todo pessoal. Estabelecer canais de comunicação de segurança. Disseminar lições aprendidas de incidentes/acidentes. Promover cultura de reporte não-punitiva [153.59].",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.59",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Cultura de segurança promovida, comunicação ativa, treinamentos realizados"
            },

            # ============================================
            # RBAC-153: Subparte D — Operação do Aeródromo
            # ============================================
            {
                "code": "RBAC-153-40",
                "title": "Proteção da Área Operacional e Credenciamento",
                "description": "Proteção, cercamento, controle de acesso e credenciamento conforme RBAC 153.107/153.109",
                "safety_category": SafetyCategory.SECURITY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter sistema de proteção da área operacional com cercamento adequado e controle de acesso. Implementar sistema de credenciamento vinculado aos treinamentos do PISOA. Monitorar integridade do sistema de proteção perimetral [153.107/153.109].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.107/153.109",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Proteção operacional ativa, credenciamento vinculado ao PISOA"
            },
            {
                "code": "RBAC-153-41",
                "title": "Movimentação de Veículos e Pessoas na Área Operacional",
                "description": "Regras para veículos e pessoal na área de movimento conforme RBAC 153.111-153.117",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Estabelecer regras de movimentação na área operacional: acesso à área de manobras (com radiocomunicação e fraseologia padrão), proibições de entrada, velocidades máximas, prioridade de aeronaves, prevenção de incursão em pista. Implementar SOCMS (Sistema de Orientação e Controle do Movimento de Superfície) quando aplicável [153.111-153.117].",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.111/153.117",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Regras de movimentação implementadas, prevenção de incursão ativa"
            },
            {
                "code": "RBAC-153-42",
                "title": "Gestão de Pátios de Aeronaves",
                "description": "Supervisão, alocação de posições e procedimentos de pátio conforme RBAC 153.119/153.121",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Supervisionar operações de pátio. Definir alocação de posições de estacionamento de aeronaves. Implementar procedimentos de aproximação e pushback. Coordenar operações com empresas aéreas e prestadores de serviço [153.119/153.121].",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.119/153.121",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Operações de pátio supervisionadas, procedimentos documentados"
            },
            {
                "code": "RBAC-153-43",
                "title": "Abastecimento de Aeronaves",
                "description": "Requisitos de segurança para abastecimento de combustível conforme RBAC 153.125",
                "safety_category": SafetyCategory.FIRE_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Assegurar que operações de abastecimento atendem aos requisitos de segurança. Procedimentos para abastecimento com passageiros a bordo. Posicionamento de equipamentos de combate a incêndio. Coordenação entre equipe de solo e tripulação [153.125].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.125",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Abastecimento seguro conforme procedimentos aprovados"
            },
            {
                "code": "RBAC-153-44",
                "title": "Operações em Baixa Visibilidade",
                "description": "Procedimentos para operação em condições de baixa visibilidade conforme RBAC 153.131",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "min_passengers": 200000,
                "requirements": "Implementar procedimentos específicos para operações em baixa visibilidade (LVO). Definir critérios de ativação e desativação do LVO. Aplicar SOCMS conforme 153.131. Treinar pessoal para operações em LVO (vincular ao PISOA). Verificar auxílios visuais e iluminação operacional.",
                "requirement_classification": RequirementClassification.C,
                "weight": 7,
                "anac_reference": "RBAC 153.131",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Procedimentos LVO implementados, pessoal treinado, auxílios visuais verificados"
            },
            {
                "code": "RBAC-153-45",
                "title": "Monitoramento e Inspeções Operacionais",
                "description": "Inspeções diárias e monitoramento contínuo conforme RBAC 153.133",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Realizar monitoramento contínuo e inspeções diárias da área de movimento: obstáculos, fauna, sistema de proteção, estacionamento, veículos, obras. Avaliar e reportar condição de pista. Inspecionar antes das primeiras operações diárias. Documentar achados e ações corretivas [153.133].",
                "requirement_classification": RequirementClassification.D,
                "weight": 9,
                "anac_reference": "RBAC 153.133",
                "evaluation_type": EvaluationType.TOPS,
                "expected_performance": "Inspeções diárias realizadas, condição de pista avaliada e reportada"
            },
            {
                "code": "RBAC-153-46",
                "title": "Informações Aeronáuticas e Auxílios Visuais",
                "description": "Manutenção de informações AIS e auxílios visuais conforme RBAC 153.105",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter informações aeronáuticas atualizadas no AIS (AIP, NOTAM). Assegurar funcionamento de auxílios visuais (sinalização, iluminação de pista, balizamento). Reportar indisponibilidade de auxílios. Manter equipamentos e posicionamento conforme norma [153.105].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.105",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Informações AIS atualizadas, auxílios visuais operacionais"
            },
            {
                "code": "RBAC-153-47",
                "title": "Gestão de Obstáculos e Faixa de Pista",
                "description": "Controle de obstáculos e preservação de superfícies conforme RBAC 153.101/153.103",
                "safety_category": SafetyCategory.INFRASTRUCTURE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Controlar posicionamento de objetos na área operacional (faixa de pista, RESA, taxiway, clearway). Monitorar e gerenciar obstáculos. Manter superfícies limitadoras. Garantir condições do pavimento dentro dos limites ACN/PCN [153.101/153.103].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.101/153.103",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Obstáculos controlados, superfícies preservadas, ACN/PCN compatíveis"
            },

            # ============================================
            # RBAC-153: Subparte E — Manutenção do Aeródromo
            # ============================================
            {
                "code": "RBAC-153-50",
                "title": "Programa de Manutenção do Aeródromo",
                "description": "Programas de manutenção para áreas pavimentadas, não-pavimentadas, drenagem e sistemas conforme RBAC 153.201-153.221",
                "safety_category": SafetyCategory.MAINTENANCE,
                "applies_to_sizes": json.dumps(["small", "medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed", "general_aviation"]),
                "requirements": "Manter programas de manutenção para: áreas pavimentadas (estrutural e funcional), áreas não-pavimentadas, drenagem, áreas verdes, auxílios visuais, sistemas elétricos, perímetro operacional, veículos e equipamentos. Responsável técnico com registro em conselho profissional. Gerenciar defeitos de pavimento e desníveis. Documentar todas as manutenções [153.201-153.221].",
                "requirement_classification": RequirementClassification.D,
                "weight": 8,
                "anac_reference": "RBAC 153.201/153.221",
                "evaluation_type": EvaluationType.BOTH,
                "expected_performance": "Programas de manutenção ativos, responsável técnico designado, registros em dia"
            },
        ]
        
        to_add = [r for r in regulations if r["code"] not in existing_codes]
        for reg_data in to_add:
            regulation = Regulation(**reg_data)
            db.add(regulation)

        updated_count = 0
        if update_existing:
            to_update = [r for r in regulations if r["code"] in existing_codes]
            for reg_data in to_update:
                existing = db.query(Regulation).filter(Regulation.code == reg_data["code"]).first()
                if existing:
                    for key, value in reg_data.items():
                        if key != "code" and hasattr(existing, key):
                            setattr(existing, key, value)
                    updated_count += 1

        if to_add or updated_count:
            db.commit()
            parts = []
            if to_add:
                parts.append(f"{len(to_add)} adicionada(s)")
            if updated_count:
                parts.append(f"{updated_count} atualizada(s)")
            print(f"Seed regulações: {', '.join(parts)}. Total: {len(existing_codes) + len(to_add)}")
        else:
            print(f"All {len(regulations)} regulations already exist. Nothing to add.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding regulations: {e}")
        raise
    finally:
        db.close()


def seed_sample_airports():
    """Seed sample airports for testing."""
    db = SessionLocal()
    
    try:
        existing_codes = {r.code for r in db.query(Airport.code).all()}
        airports = [
            {
                "name": "Aeroporto Internacional de São Paulo - Guarulhos",
                "code": "SBGR",
                "size": AirportSize.INTERNATIONAL,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 40000000,
                "has_international_operations": True,
                "has_cargo_operations": True,
                "has_maintenance_facility": True,
                "number_of_runways": 2,
                "max_aircraft_weight": 400
            },
            {
                "name": "Aeroporto Santos Dumont",
                "code": "SBRJ",
                "size": AirportSize.MEDIUM,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 3000000,
                "has_international_operations": False,
                "has_cargo_operations": False,
                "has_maintenance_facility": False,
                "number_of_runways": 2,
                "max_aircraft_weight": 150
            },
            {
                "name": "Aeroporto Internacional de Belo Horizonte/Confins",
                "code": "SBCF",
                "size": AirportSize.MEDIUM,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 800000,
                "has_international_operations": False,
                "has_cargo_operations": True,
                "has_maintenance_facility": False,
                "number_of_runways": 1,
                "max_aircraft_weight": 150
            },
            {
                "name": "Aeroporto Internacional de Brasília",
                "code": "SBBR",
                "size": AirportSize.INTERNATIONAL,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 15000000,
                "has_international_operations": True,
                "has_cargo_operations": True,
                "has_maintenance_facility": True,
                "number_of_runways": 2,
                "max_aircraft_weight": 400
            },
            {
                "name": "Aeroporto Internacional Salgado Filho",
                "code": "SBPA",
                "size": AirportSize.MEDIUM,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 5000000,
                "has_international_operations": True,
                "has_cargo_operations": True,
                "has_maintenance_facility": False,
                "number_of_runways": 1,
                "max_aircraft_weight": 200
            },
            {
                "name": "Aeroporto Internacional de Recife",
                "code": "SBRF",
                "size": AirportSize.MEDIUM,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 3500000,
                "has_international_operations": True,
                "has_cargo_operations": True,
                "has_maintenance_facility": False,
                "number_of_runways": 1,
                "max_aircraft_weight": 200
            },
            {
                "name": "Aeroporto Municipal de Uberlândia",
                "code": "SBUL",
                "size": AirportSize.SMALL,
                "airport_type": AirportType.COMMERCIAL,
                "annual_passengers": 150000,
                "has_international_operations": False,
                "has_cargo_operations": False,
                "has_maintenance_facility": False,
                "number_of_runways": 1,
                "max_aircraft_weight": 50
            }
        ]
        to_add = [a for a in airports if a["code"] not in existing_codes]
        if not to_add:
            print("Sample airports já existem. Nenhum novo a adicionar.")
            return
        for airport_data in to_add:
            airport = Airport(**airport_data)
            db.add(airport)
        db.commit()
        print(f"Seeded {len(to_add)} sample airports successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding airports: {e}")
        raise
    finally:
        db.close()


def seed_anac_airports_bootstrap():
    """Popula anac_airports com principais aeroportos para lookup imediato (upsert por código)."""
    db = SessionLocal()
    try:
        existing_codes = {r.code for r in db.query(ANACAirport.code).all()}
        to_add = [a for a in ANAC_AIRPORTS_BOOTSTRAP if a["code"] not in existing_codes]
        if not to_add:
            print("anac_airports já contém todos os aeroportos do bootstrap.")
            return db.query(ANACAirport).count()
        for a in to_add:
            db.add(ANACAirport(**a))
        db.commit()
        print(f"Bootstrap: {len(to_add)} aeroportos adicionados a anac_airports")
        return db.query(ANACAirport).count()
    except Exception as e:
        db.rollback()
        print(f"Erro no bootstrap anac_airports: {e}")
        return 0
    finally:
        db.close()


def seed_anac_airports_full() -> int:
    """
    Popula anac_airports com a lista COMPLETA da ANAC (Características Gerais ~6800 aeródromos).
    Quando a pessoa selecionar o aeroporto para cadastro, todos os dados já estarão no banco.
    Se ANAC indisponível, usa bootstrap (27 principais).
    """
    from app.services.anac_sync import ANACSyncService
    db = SessionLocal()
    try:
        sync = ANACSyncService(db=db)
        data = sync.download_anac_data()
        if data:
            count = len(data)
            print(f"anac_airports: {count} aeródromos carregados da ANAC (Características Gerais)")
            return count
        print("ANAC indisponível. Usando bootstrap...")
        return seed_anac_airports_bootstrap()
    except Exception as e:
        print(f"Erro ao carregar anac_airports: {e}")
        return seed_anac_airports_bootstrap()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    try:
        from sqlalchemy import text
        from app.database import engine
        for col_name, col_type in [("usage_class", "VARCHAR(20)"), ("avsec_classification", "VARCHAR(10)"),
                                   ("aircraft_size_category", "VARCHAR(5)"), ("number_of_runways", "INTEGER DEFAULT 1")]:
            try:
                with engine.connect() as c:
                    c.execute(text(f"ALTER TABLE anac_airports ADD COLUMN {col_name} {col_type}"))
                    c.commit()
            except Exception:
                pass
    except Exception:
        pass
    
    print("Seeding regulations...")
    seed_regulations()
    
    print("Seeding sample airports...")
    seed_sample_airports()
    
    print("Seeding anac_airports bootstrap...")
    seed_anac_airports_bootstrap()
    
    print("Seed completed successfully!")

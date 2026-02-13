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


def seed_regulations():
    """Seed initial ANAC regulations based on airport variables."""
    db = SessionLocal()
    
    try:
        # Check if regulations already exist
        if db.query(Regulation).count() > 0:
            print("Regulations already seeded. Skipping...")
            return
        
        regulations = [
            # Operational Safety - applies to all airports
            {
                "code": "RBAC-154-01",
                "title": "Sistema de Gerenciamento de Segurança Operacional (SMS)",
                "description": "Estabelece requisitos para implementação de Sistema de Gerenciamento de Segurança Operacional",
                "safety_category": SafetyCategory.OPERATIONAL_SAFETY,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "applies_to_types": json.dumps(["commercial", "mixed"]),
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
                "title": "Exercícios de Emergência",
                "description": "Requisitos para exercícios simulados de emergência",
                "safety_category": SafetyCategory.EMERGENCY_RESPONSE,
                "applies_to_sizes": json.dumps(["medium", "large", "international"]),
                "min_passengers": 200000,
                "requirements": "Exercício completo a cada 2 anos, exercícios parciais anuais, participação de órgãos externos, relatórios de exercícios."
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
        
        for reg_data in regulations:
            regulation = Regulation(**reg_data)
            db.add(regulation)
        
        db.commit()
        print(f"Seeded {len(regulations)} regulations successfully!")
        
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
            return
        for a in to_add:
            db.add(ANACAirport(**a))
        db.commit()
        print(f"Bootstrap: {len(to_add)} aeroportos adicionados a anac_airports")
    except Exception as e:
        db.rollback()
        print(f"Erro no bootstrap anac_airports: {e}")
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

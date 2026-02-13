"""
Data models for the airport compliance system.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Enum as SQLEnum, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class AirportSize(enum.Enum):
    """Airport size classifications according to ANAC standards"""
    SMALL = "small"  # Pequeno - up to 200k passengers/year
    MEDIUM = "medium"  # Médio - 200k to 1M passengers/year
    LARGE = "large"  # Grande - 1M to 10M passengers/year
    INTERNATIONAL = "international"  # Internacional - over 10M passengers/year


class AirportCategory(enum.Enum):
    """ANAC airport categories based on annual passenger volume"""
    CAT_1C = "1C"  # Até 50.000 passageiros/ano
    CAT_2C = "2C"  # 50.001 a 200.000 passageiros/ano
    CAT_3C = "3C"  # 200.001 a 500.000 passageiros/ano
    CAT_4C = "4C"  # 500.001 a 1.000.000 passageiros/ano
    CAT_5C = "5C"  # 1.000.001 a 5.000.000 passageiros/ano
    CAT_6C = "6C"  # 5.000.001 a 10.000.000 passageiros/ano
    CAT_7C = "7C"  # 10.000.001 a 20.000.000 passageiros/ano
    CAT_8C = "8C"  # 20.000.001 a 40.000.000 passageiros/ano
    CAT_9C = "9C"  # Acima de 40.000.000 passageiros/ano


class AirportType(enum.Enum):
    """Type of airport operations"""
    COMMERCIAL = "commercial"
    GENERAL_AVIATION = "general_aviation"
    MILITARY = "military"
    MIXED = "mixed"


class SafetyCategory(enum.Enum):
    """ANAC safety categories"""
    OPERATIONAL_SAFETY = "operational_safety"
    FIRE_SAFETY = "fire_safety"
    SECURITY = "security"
    ENVIRONMENTAL = "environmental"
    INFRASTRUCTURE = "infrastructure"
    EMERGENCY_RESPONSE = "emergency_response"
    WILDLIFE_MANAGEMENT = "wildlife_management"
    MAINTENANCE = "maintenance"
    PERSONNEL_CERTIFICATION = "personnel_certification"
    AIR_TRAFFIC_SERVICES = "air_traffic_services"


class RequirementClassification(enum.Enum):
    """ANAC requirement classification according to checklist guidelines"""
    D = "D"  # Requisitos essenciais (85% mínimo para ACOP)
    C = "C"  # Requisitos complementares
    B = "B"  # Práticas recomendadas
    A = "A"  # Melhores práticas


class EvaluationType(enum.Enum):
    """Type of evaluation according to ANAC guidelines"""
    DOCS = "DOCS"  # Documental (remote verification)
    TOPS = "TOPS"  # Operacional (on-site verification)
    BOTH = "BOTH"  # Both types required


class ComplianceStatus(enum.Enum):
    """Compliance status for a regulation"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    PENDING_REVIEW = "pending_review"


class AirportUsageClass(enum.Enum):
    """ANAC airport usage classification (RBAC 153)"""
    I = "I"  # Público: < 200 mil passageiros/ano
    II = "II"  # Público: 200 mil - 1 milhão passageiros/ano
    III = "III"  # Público: 1 milhão - 5 milhões passageiros/ano
    IV = "IV"  # Público: > 5 milhões passageiros/ano
    PRIVADO = "PRIVADO"  # Uso restrito ao proprietário


class AVSECClassification(enum.Enum):
    """ANAC AVSEC classification (Security against unlawful interference)"""
    AP_0 = "AP-0"  # Aviação geral/táxi aéreo/fretamento
    AP_1 = "AP-1"  # Comercial regular/charter, < 600 mil pass./ano
    AP_2 = "AP-2"  # Comercial regular/charter, 600 mil - 5 milhões pass./ano
    AP_3 = "AP-3"  # Comercial regular/charter, > 5 milhões pass./ano


class AircraftSizeCategory(enum.Enum):
    """ANAC aircraft size category (Runway evaluation)"""
    AB = "A/B"  # Aeronaves até 5.700 kg
    C = "C"  # Aeronaves entre 5.700 kg e 136.000 kg
    D = "D"  # Aeronaves acima de 136.000 kg


class ANACAirport(Base):
    """
    Cache da lista oficial de aeródromos da ANAC.
    Usado para lookup rápido sem depender do site da ANAC.
    Atualizado quando sincronização com ANAC tem sucesso.
    """
    __tablename__ = "anac_airports"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # ICAO
    name = Column(String(200), nullable=False)
    reference_code = Column(String(10), nullable=True)  # Ex: 3C, 4C, 4E
    category = Column(String(10), nullable=True)  # 1C-9C
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    iata_code = Column(String(3), nullable=True)
    status = Column(String(50), nullable=True)
    usage_class = Column(String(20), nullable=True)  # I, II, III, IV (RBAC 153)
    avsec_classification = Column(String(10), nullable=True)  # AP-0, AP-1, AP-2, AP-3
    aircraft_size_category = Column(String(5), nullable=True)  # A/B, C, D
    number_of_runways = Column(Integer, default=1, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Airport(Base):
    """Airport profile with variables that determine compliance requirements"""
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)  # ICAO code
    size = Column(SQLEnum(AirportSize), nullable=False)
    airport_type = Column(SQLEnum(AirportType), nullable=False)
    annual_passengers = Column(Integer, nullable=True)  # Mantido para compatibilidade e cálculo de categoria
    category = Column(SQLEnum(AirportCategory), nullable=True)  # Categoria ANAC (1C-9C) baseada em passageiros
    reference_code = Column(String(10), nullable=True)  # Código de referência das aeronaves (ex: 3C, 4C, 4E) - configuração máxima permitida
    
    # Campos de sincronização com ANAC
    data_sincronizacao_anac = Column(DateTime, nullable=True)  # Última sincronização com ANAC
    origem_dados = Column(String(20), default="manual")  # "manual" ou "anac"
    versao_dados_anac = Column(String(50), nullable=True)  # Versão do dataset ANAC
    
    # Campos adicionais da ANAC
    codigo_iata = Column(String(3), nullable=True)  # Código IATA (3 letras)
    latitude = Column(Float, nullable=True)  # Coordenadas geográficas
    longitude = Column(Float, nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)  # UF
    status_operacional = Column(String(50), nullable=True)  # Status oficial ANAC
    
    has_international_operations = Column(Boolean, default=False)
    has_cargo_operations = Column(Boolean, default=False)
    has_maintenance_facility = Column(Boolean, default=False)
    number_of_runways = Column(Integer, default=1)
    max_aircraft_weight = Column(Integer, nullable=True)  # in tons
    
    # Novas classificações ANAC (usando String para compatibilidade com valores existentes no banco)
    usage_class = Column(String(20), nullable=True)  # Classe por Uso (RBAC 153): I, II, III, IV, PRIVADO
    avsec_classification = Column(String(10), nullable=True)  # Classificação AVSEC: AP-0, AP-1, AP-2, AP-3
    aircraft_size_category = Column(String(5), nullable=True)  # Categoria de Porte da Aeronave: A/B, C, D
    
    # Relationships
    compliance_records = relationship("ComplianceRecord", back_populates="airport", cascade="all, delete-orphan")


class Regulation(Base):
    """ANAC regulations and norms"""
    __tablename__ = "regulations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)  # e.g., RBAC-154
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    safety_category = Column(SQLEnum(SafetyCategory), nullable=False)
    
    # ANAC Classification System (D/C/B/A)
    requirement_classification = Column(SQLEnum(RequirementClassification), nullable=True)  # D, C, B, or A
    evaluation_type = Column(SQLEnum(EvaluationType), nullable=True, default=EvaluationType.BOTH)  # DOCS, TOPS, or BOTH
    weight = Column(Integer, nullable=True)  # Peso do item (1-10 typically)
    anac_reference = Column(String(200), nullable=True)  # Referência normativa (e.g., 153.323(e))
    
    # Conditions that determine if this regulation applies
    applies_to_sizes = Column(String(200), nullable=True)  # JSON array of sizes
    applies_to_types = Column(String(200), nullable=True)  # JSON array of types
    min_passengers = Column(Integer, nullable=True)
    requires_international = Column(Boolean, default=False)
    requires_cargo = Column(Boolean, default=False)
    requires_maintenance = Column(Boolean, default=False)
    min_runways = Column(Integer, nullable=True)
    min_aircraft_weight = Column(Integer, nullable=True)
    
    # Requirements description
    requirements = Column(Text, nullable=False)  # What needs to be done
    expected_performance = Column(Text, nullable=True)  # Desempenho esperado/Verificação
    
    # Relationships
    compliance_records = relationship("ComplianceRecord", back_populates="regulation")


class ComplianceRecord(Base):
    """Record of compliance status for an airport-regulation pair"""
    __tablename__ = "compliance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False)
    status = Column(SQLEnum(ComplianceStatus), nullable=False, default=ComplianceStatus.PENDING_REVIEW)
    notes = Column(Text, nullable=True)
    last_verified = Column(String(50), nullable=True)  # ISO date string
    verified_by = Column(String(100), nullable=True)
    
    # ANAC Evaluation System
    docs_score = Column(Integer, nullable=True)  # Score for DOCS evaluation (0-100)
    tops_score = Column(Integer, nullable=True)  # Score for TOPS evaluation (0-100)
    weighted_score = Column(Integer, nullable=True)  # Weighted score considering classification and weight
    is_essential_compliant = Column(Boolean, nullable=True)  # True if D items meet 85% threshold
    
    # Action items
    action_items = Column(Text, nullable=True)  # JSON array of action items
    completed_action_items = Column(Text, nullable=True)  # JSON array of indices of completed action items
    action_item_due_dates = Column(Text, nullable=True)  # JSON object: {item_index: "YYYY-MM-DD", ...}
    
    # Custom fields for SESCINC-specific data (JSON)
    custom_fields = Column(Text, nullable=True)  # JSON object with custom fields based on regulation code
    
    # Relationships
    airport = relationship("Airport", back_populates="compliance_records")
    regulation = relationship("Regulation", back_populates="compliance_records")
    documents = relationship("DocumentAttachment", back_populates="compliance_record", cascade="all, delete-orphan")


class DocumentAttachment(Base):
    """Document attachments for compliance records"""
    __tablename__ = "document_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    compliance_record_id = Column(Integer, ForeignKey("compliance_records.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to stored file
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=True)  # MIME type
    document_type = Column(String(50), nullable=True)  # Certificado, Relatório, Foto, Outro
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    compliance_record = relationship("ComplianceRecord", back_populates="documents")
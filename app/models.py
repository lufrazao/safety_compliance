"""
Data models for the airport compliance system.
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class AirportSize(enum.Enum):
    """Airport size classifications according to ANAC standards"""
    SMALL = "small"  # Pequeno - up to 200k passengers/year
    MEDIUM = "medium"  # Médio - 200k to 1M passengers/year
    LARGE = "large"  # Grande - 1M to 10M passengers/year
    INTERNATIONAL = "international"  # Internacional - over 10M passengers/year


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


class Airport(Base):
    """Airport profile with variables that determine compliance requirements"""
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(10), unique=True, nullable=False)  # ICAO code
    size = Column(SQLEnum(AirportSize), nullable=False)
    airport_type = Column(SQLEnum(AirportType), nullable=False)
    annual_passengers = Column(Integer, nullable=True)
    has_international_operations = Column(Boolean, default=False)
    has_cargo_operations = Column(Boolean, default=False)
    has_maintenance_facility = Column(Boolean, default=False)
    number_of_runways = Column(Integer, default=1)
    max_aircraft_weight = Column(Integer, nullable=True)  # in tons
    
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
    
    # Relationships
    airport = relationship("Airport", back_populates="compliance_records")
    regulation = relationship("Regulation", back_populates="compliance_records")

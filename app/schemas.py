"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import (
    AirportSize, AirportType, SafetyCategory, ComplianceStatus,
    RequirementClassification, EvaluationType
)


class AirportBase(BaseModel):
    name: str
    code: str
    size: AirportSize
    airport_type: AirportType
    annual_passengers: Optional[int] = None
    has_international_operations: bool = False
    has_cargo_operations: bool = False
    has_maintenance_facility: bool = False
    number_of_runways: int = 1
    max_aircraft_weight: Optional[int] = None


class AirportCreate(AirportBase):
    pass


class AirportResponse(AirportBase):
    id: int
    
    model_config = {"from_attributes": True}


class RegulationBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    safety_category: SafetyCategory
    requirement_classification: Optional[RequirementClassification] = None  # D, C, B, A
    evaluation_type: Optional[EvaluationType] = EvaluationType.BOTH  # DOCS, TOPS, BOTH
    weight: Optional[int] = None  # Peso do item (1-10)
    anac_reference: Optional[str] = None  # Referência normativa
    applies_to_sizes: Optional[List[str]] = None
    applies_to_types: Optional[List[str]] = None
    min_passengers: Optional[int] = None
    requires_international: bool = False
    requires_cargo: bool = False
    requires_maintenance: bool = False
    min_runways: Optional[int] = None
    min_aircraft_weight: Optional[int] = None
    requirements: str
    expected_performance: Optional[str] = None  # Desempenho esperado/Verificação


class RegulationCreate(RegulationBase):
    pass


class RegulationResponse(RegulationBase):
    id: int
    
    model_config = {"from_attributes": True}


class ComplianceRecordBase(BaseModel):
    airport_id: int
    regulation_id: int
    status: ComplianceStatus = ComplianceStatus.PENDING_REVIEW
    notes: Optional[str] = None
    docs_score: Optional[int] = None  # Score for DOCS evaluation (0-100)
    tops_score: Optional[int] = None  # Score for TOPS evaluation (0-100)
    weighted_score: Optional[int] = None  # Weighted score
    is_essential_compliant: Optional[bool] = None  # True if D items meet 85% threshold
    action_items: Optional[List[str]] = None
    completed_action_items: Optional[List[int]] = None  # Indices of completed action items
    action_item_due_dates: Optional[dict] = None  # {item_index: "YYYY-MM-DD", ...}


class ComplianceRecordCreate(ComplianceRecordBase):
    pass


class ComplianceRecordUpdate(BaseModel):
    status: Optional[ComplianceStatus] = None
    notes: Optional[str] = None
    docs_score: Optional[int] = None  # Score for DOCS evaluation (0-100)
    tops_score: Optional[int] = None  # Score for TOPS evaluation (0-100)
    action_items: Optional[List[str]] = None
    completed_action_items: Optional[List[int]] = None  # Indices of completed action items
    action_item_due_dates: Optional[dict] = None  # {item_index: "YYYY-MM-DD", ...}
    verified_by: Optional[str] = None


class ComplianceRecordResponse(ComplianceRecordBase):
    id: int
    last_verified: Optional[str] = None
    verified_by: Optional[str] = None
    regulation: Optional[RegulationResponse] = None
    
    model_config = {"from_attributes": True}


class ComplianceCheckRequest(BaseModel):
    airport_id: int


class ComplianceCheckResponse(BaseModel):
    airport_id: int
    total_regulations: int
    applicable_regulations: int
    compliant_count: int
    non_compliant_count: int
    partial_count: int
    pending_count: int
    compliance_records: List[ComplianceRecordResponse]
    recommendations: List[str] = []
    anac_scores: Optional[dict] = None  # ANAC compliance scores
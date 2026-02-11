"""
FastAPI application for airport compliance management.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import os
import json

from app.database import get_db, init_db
from app import schemas
from app.compliance_engine import ComplianceEngine
from app.models import Airport, Regulation, ComplianceRecord

app = FastAPI(
    title="ANAC Airport Compliance System",
    description="Compliance management system for Brazilian airports",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Serve the main web interface."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "ANAC Airport Compliance System API",
        "version": "1.0.0",
        "endpoints": {
            "airports": "/api/airports",
            "regulations": "/api/regulations",
            "compliance": "/api/compliance"
        },
        "note": "Interface web disponível em /static/index.html ou abra http://localhost:8000 no navegador"
    }


# Airport endpoints
@app.post("/api/airports", response_model=schemas.AirportResponse, status_code=status.HTTP_201_CREATED)
async def create_airport(airport: schemas.AirportCreate, db: Session = Depends(get_db)):
    """Create a new airport profile."""
    # Check if code already exists
    existing = db.query(Airport).filter(Airport.code == airport.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Airport with code {airport.code} already exists"
        )
    
    db_airport = Airport(**airport.dict())
    db.add(db_airport)
    db.commit()
    db.refresh(db_airport)
    return db_airport


@app.get("/api/airports", response_model=List[schemas.AirportResponse])
async def list_airports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all airports."""
    airports = db.query(Airport).offset(skip).limit(limit).all()
    return airports


@app.get("/api/airports/{airport_id}", response_model=schemas.AirportResponse)
async def get_airport(airport_id: int, db: Session = Depends(get_db)):
    """Get a specific airport by ID."""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with id {airport_id} not found"
        )
    return airport


@app.put("/api/airports/{airport_id}", response_model=schemas.AirportResponse)
async def update_airport(
    airport_id: int,
    airport_update: schemas.AirportCreate,
    db: Session = Depends(get_db)
):
    """Update an existing airport profile."""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with id {airport_id} not found"
        )
    
    # Check if code is being changed and if new code already exists
    if airport_update.code != airport.code:
        existing = db.query(Airport).filter(Airport.code == airport_update.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Airport with code {airport_update.code} already exists"
            )
    
    # Update all fields
    for key, value in airport_update.dict().items():
        setattr(airport, key, value)
    
    db.commit()
    db.refresh(airport)
    return airport


@app.delete("/api/airports/{airport_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_airport(airport_id: int, db: Session = Depends(get_db)):
    """Delete an airport profile."""
    airport = db.query(Airport).filter(Airport.id == airport_id).first()
    if not airport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with id {airport_id} not found"
        )
    
    db.delete(airport)
    db.commit()
    return None


# Regulation endpoints
@app.post("/api/regulations", response_model=schemas.RegulationResponse, status_code=status.HTTP_201_CREATED)
async def create_regulation(regulation: schemas.RegulationCreate, db: Session = Depends(get_db)):
    """Create a new regulation."""
    existing = db.query(Regulation).filter(Regulation.code == regulation.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Regulation with code {regulation.code} already exists"
        )
    
    db_regulation = Regulation(**regulation.dict())
    db.add(db_regulation)
    db.commit()
    db.refresh(db_regulation)
    return db_regulation


@app.get("/api/regulations", response_model=List[schemas.RegulationResponse])
async def list_regulations(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db)
):
    """List all regulations, optionally filtered by safety category."""
    query = db.query(Regulation)
    if category:
        query = query.filter(Regulation.safety_category == category)
    regulations = query.offset(skip).limit(limit).all()
    return regulations


@app.get("/api/regulations/{regulation_id}", response_model=schemas.RegulationResponse)
async def get_regulation(regulation_id: int, db: Session = Depends(get_db)):
    """Get a specific regulation by ID."""
    regulation = db.query(Regulation).filter(Regulation.id == regulation_id).first()
    if not regulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regulation with id {regulation_id} not found"
        )
    return regulation


# Compliance endpoints
@app.post("/api/compliance/check", response_model=schemas.ComplianceCheckResponse)
async def check_compliance(
    request: schemas.ComplianceCheckRequest,
    db: Session = Depends(get_db)
):
    """Perform a compliance check for an airport."""
    engine = ComplianceEngine(db)
    result = engine.check_compliance(request.airport_id)
    
    # Convert compliance records to response format
    records_response = []
    for record in result["compliance_records"]:
        regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
        
        # Parse action_items if it's a JSON string
        action_items = None
        if record.action_items:
            try:
                if isinstance(record.action_items, str):
                    action_items = json.loads(record.action_items)
                else:
                    action_items = record.action_items
            except (json.JSONDecodeError, TypeError):
                action_items = None
        
        # Parse completed_action_items if it's a JSON string
        completed_action_items = None
        if record.completed_action_items:
            try:
                if isinstance(record.completed_action_items, str):
                    completed_action_items = json.loads(record.completed_action_items)
                else:
                    completed_action_items = record.completed_action_items
            except (json.JSONDecodeError, TypeError):
                completed_action_items = None
        
        # Parse action_item_due_dates if it's a JSON string
        action_item_due_dates = None
        if record.action_item_due_dates:
            try:
                if isinstance(record.action_item_due_dates, str):
                    action_item_due_dates = json.loads(record.action_item_due_dates)
                else:
                    action_item_due_dates = record.action_item_due_dates
            except (json.JSONDecodeError, TypeError):
                action_item_due_dates = None
        
        # Parse regulation JSON fields before validation
        regulation_dict = None
        if regulation:
            # Parse JSON strings for applies_to_sizes and applies_to_types
            applies_to_sizes = None
            if regulation.applies_to_sizes:
                try:
                    applies_to_sizes = json.loads(regulation.applies_to_sizes)
                except (json.JSONDecodeError, TypeError):
                    applies_to_sizes = None
            
            applies_to_types = None
            if regulation.applies_to_types:
                try:
                    applies_to_types = json.loads(regulation.applies_to_types)
                except (json.JSONDecodeError, TypeError):
                    applies_to_types = None
            
            regulation_dict = {
                "id": regulation.id,
                "code": regulation.code,
                "title": regulation.title,
                "description": regulation.description,
                "safety_category": regulation.safety_category,
                "requirement_classification": regulation.requirement_classification,
                "evaluation_type": regulation.evaluation_type,
                "weight": regulation.weight,
                "anac_reference": regulation.anac_reference,
                "applies_to_sizes": applies_to_sizes,
                "applies_to_types": applies_to_types,
                "min_passengers": regulation.min_passengers,
                "requires_international": regulation.requires_international,
                "requires_cargo": regulation.requires_cargo,
                "requires_maintenance": regulation.requires_maintenance,
                "min_runways": regulation.min_runways,
                "min_aircraft_weight": regulation.min_aircraft_weight,
                "requirements": regulation.requirements,
                "expected_performance": regulation.expected_performance
            }
        
        record_dict = {
            "id": record.id,
            "airport_id": record.airport_id,
            "regulation_id": record.regulation_id,
            "status": record.status,
            "notes": record.notes,
            "docs_score": record.docs_score,
            "tops_score": record.tops_score,
            "weighted_score": record.weighted_score,
            "is_essential_compliant": record.is_essential_compliant,
            "action_items": action_items,
            "completed_action_items": completed_action_items,
            "action_item_due_dates": action_item_due_dates,
            "last_verified": record.last_verified,
            "verified_by": record.verified_by,
            "regulation": schemas.RegulationResponse(**regulation_dict) if regulation_dict else None
        }
        records_response.append(schemas.ComplianceRecordResponse(**record_dict))
    
    return schemas.ComplianceCheckResponse(
        airport_id=result["airport_id"],
        total_regulations=result["total_regulations"],
        applicable_regulations=result["applicable_regulations"],
        compliant_count=result["compliant_count"],
        non_compliant_count=result["non_compliant_count"],
        partial_count=result["partial_count"],
        pending_count=result["pending_count"],
        compliance_records=records_response,
        recommendations=result["recommendations"],
        anac_scores=result.get("anac_scores")
    )


@app.get("/api/compliance/airport/{airport_id}", response_model=List[schemas.ComplianceRecordResponse])
async def get_airport_compliance(airport_id: int, db: Session = Depends(get_db)):
    """Get all compliance records for an airport."""
    records = db.query(ComplianceRecord).filter(
        ComplianceRecord.airport_id == airport_id
    ).all()
    
    records_response = []
    for record in records:
        regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
        
        # Parse action_items if it's a JSON string
        action_items = None
        if record.action_items:
            try:
                if isinstance(record.action_items, str):
                    action_items = json.loads(record.action_items)
                else:
                    action_items = record.action_items
            except (json.JSONDecodeError, TypeError):
                action_items = None
        
        # Parse completed_action_items if it's a JSON string
        completed_action_items = None
        if record.completed_action_items:
            try:
                if isinstance(record.completed_action_items, str):
                    completed_action_items = json.loads(record.completed_action_items)
                else:
                    completed_action_items = record.completed_action_items
            except (json.JSONDecodeError, TypeError):
                completed_action_items = None
        
        # Parse action_item_due_dates if it's a JSON string
        action_item_due_dates = None
        if record.action_item_due_dates:
            try:
                if isinstance(record.action_item_due_dates, str):
                    action_item_due_dates = json.loads(record.action_item_due_dates)
                else:
                    action_item_due_dates = record.action_item_due_dates
            except (json.JSONDecodeError, TypeError):
                action_item_due_dates = None
        
        # Parse regulation JSON fields before validation
        regulation_dict = None
        if regulation:
            # Parse JSON strings for applies_to_sizes and applies_to_types
            applies_to_sizes = None
            if regulation.applies_to_sizes:
                try:
                    applies_to_sizes = json.loads(regulation.applies_to_sizes)
                except (json.JSONDecodeError, TypeError):
                    applies_to_sizes = None
            
            applies_to_types = None
            if regulation.applies_to_types:
                try:
                    applies_to_types = json.loads(regulation.applies_to_types)
                except (json.JSONDecodeError, TypeError):
                    applies_to_types = None
            
            regulation_dict = {
                "id": regulation.id,
                "code": regulation.code,
                "title": regulation.title,
                "description": regulation.description,
                "safety_category": regulation.safety_category,
                "requirement_classification": regulation.requirement_classification,
                "evaluation_type": regulation.evaluation_type,
                "weight": regulation.weight,
                "anac_reference": regulation.anac_reference,
                "applies_to_sizes": applies_to_sizes,
                "applies_to_types": applies_to_types,
                "min_passengers": regulation.min_passengers,
                "requires_international": regulation.requires_international,
                "requires_cargo": regulation.requires_cargo,
                "requires_maintenance": regulation.requires_maintenance,
                "min_runways": regulation.min_runways,
                "min_aircraft_weight": regulation.min_aircraft_weight,
                "requirements": regulation.requirements,
                "expected_performance": regulation.expected_performance
            }
        
        record_dict = {
            "id": record.id,
            "airport_id": record.airport_id,
            "regulation_id": record.regulation_id,
            "status": record.status,
            "notes": record.notes,
            "docs_score": record.docs_score,
            "tops_score": record.tops_score,
            "weighted_score": record.weighted_score,
            "is_essential_compliant": record.is_essential_compliant,
            "action_items": action_items,
            "completed_action_items": completed_action_items,
            "action_item_due_dates": action_item_due_dates,
            "last_verified": record.last_verified,
            "verified_by": record.verified_by,
            "regulation": schemas.RegulationResponse(**regulation_dict) if regulation_dict else None
        }
        records_response.append(schemas.ComplianceRecordResponse(**record_dict))
    
    return records_response


@app.put("/api/compliance/records/{record_id}", response_model=schemas.ComplianceRecordResponse)
async def update_compliance_record(
    record_id: int,
    update: schemas.ComplianceRecordUpdate,
    db: Session = Depends(get_db)
):
    """Update a compliance record."""
    from app.models import ComplianceStatus
    
    # Validate and convert status if provided
    status_value = update.status
    if status_value is not None:
        # Pydantic should handle the conversion, but we'll validate it
        if isinstance(status_value, str):
            try:
                status_value = ComplianceStatus(status_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status value: {status_value}. Must be one of: {[e.value for e in ComplianceStatus]}"
                )
        elif not isinstance(status_value, ComplianceStatus):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status must be a ComplianceStatus enum or valid string value"
            )
    
    engine = ComplianceEngine(db)
    try:
        record = engine.update_compliance_status(
            record_id=record_id,
            status=status_value,
            notes=update.notes,
            action_items=update.action_items,
            completed_action_items=update.completed_action_items,
            action_item_due_dates=update.action_item_due_dates,
            verified_by=update.verified_by
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    regulation = db.query(Regulation).filter(Regulation.id == record.regulation_id).first()
    
    # Parse regulation JSON fields before validation
    regulation_dict = None
    if regulation:
        # Parse JSON strings for applies_to_sizes and applies_to_types
        applies_to_sizes = None
        if regulation.applies_to_sizes:
            try:
                applies_to_sizes = json.loads(regulation.applies_to_sizes)
            except (json.JSONDecodeError, TypeError):
                applies_to_sizes = None
        
        applies_to_types = None
        if regulation.applies_to_types:
            try:
                applies_to_types = json.loads(regulation.applies_to_types)
            except (json.JSONDecodeError, TypeError):
                applies_to_types = None
        
        regulation_dict = {
            "id": regulation.id,
            "code": regulation.code,
            "title": regulation.title,
            "description": regulation.description,
            "safety_category": regulation.safety_category,
            "applies_to_sizes": applies_to_sizes,
            "applies_to_types": applies_to_types,
            "min_passengers": regulation.min_passengers,
            "requires_international": regulation.requires_international,
            "requires_cargo": regulation.requires_cargo,
            "requires_maintenance": regulation.requires_maintenance,
            "min_runways": regulation.min_runways,
            "min_aircraft_weight": regulation.min_aircraft_weight,
            "requirements": regulation.requirements
        }
    
    # Parse action_items if it's a JSON string
    action_items = None
    if record.action_items:
        try:
            if isinstance(record.action_items, str):
                action_items = json.loads(record.action_items)
            else:
                action_items = record.action_items
        except (json.JSONDecodeError, TypeError):
            action_items = None
    
    record_dict = {
        "id": record.id,
        "airport_id": record.airport_id,
        "regulation_id": record.regulation_id,
        "status": record.status,
        "notes": record.notes,
        "action_items": action_items,
        "last_verified": record.last_verified,
        "verified_by": record.verified_by,
        "regulation": schemas.RegulationResponse(**regulation_dict) if regulation_dict else None
    }
    
    return schemas.ComplianceRecordResponse(**record_dict)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

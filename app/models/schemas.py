from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class LeaderProfile(BaseModel):
    id: UUID
    name: str
    aggression: int = Field(ge=0, le=10)
    diplomacy: int = Field(ge=0, le=10)
    risk_tolerance: int = Field(ge=0, le=10)
    domestic_pressure: int = Field(ge=0, le=10)
    escalation_threshold: int = Field(ge=0, le=10)

class SimulationRequest(BaseModel):
    text: str = Field(min_length = 10, max_length=2000)

class LeaderResult(BaseModel):
    leader: str
    escalation_score: float = Field(ge = 0, le=10)
    reaction: str
    rationale: str
    similar_events: list[str] = []

class SimulationResponse(BaseModel):
    simulation_id: UUID
    event_text: str
    created_at: datetime
    results: list[LeaderResult]

class SimulationSummary(BaseModel):
    simulation_id: UUID
    event_text: str
    created_at: datetime
    avg_escalation: float

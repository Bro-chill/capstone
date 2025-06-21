from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import json

# Enums
class BudgetCategory(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"

class LocationType(str, Enum):
    INTERIOR = "interior"
    EXTERIOR = "exterior"

class TimeOfDay(str, Enum):
    DAY = "day"
    NIGHT = "night"
    DAWN = "dawn"
    DUSK = "dusk"

class WorkflowStatus(str, Enum):
    INITIALIZING = "initializing"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"

class DramaticWeight(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ContentType(str, Enum):
    DIALOGUE_HEAVY = "dialogue_heavy"
    ACTION_HEAVY = "action_heavy"
    BALANCED = "balanced"

class CrewSize(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    LARGE = "large"

class Complexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

# Base Models
class BaseModel(BaseModel):
    """Base model with JSON encoder configuration"""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Meta Information
class MetaInfo(BaseModel):
    success: bool = Field(description="Request success status")
    version: str = Field(default="1.0", description="API version")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    processing_time_ms: Optional[int] = Field(description="Processing time in milliseconds")

class WorkflowProgress(BaseModel):
    completed_analyses: int = Field(description="Number of completed analyses")
    total_analyses: int = Field(description="Total number of analyses")
    percentage: int = Field(description="Completion percentage")

class WorkflowInfo(BaseModel):
    thread_id: str = Field(description="Unique workflow identifier")
    status: WorkflowStatus = Field(description="Current workflow status")
    current_phase: str = Field(description="Current processing phase")
    requires_review: bool = Field(description="Whether human review is needed")
    progress: WorkflowProgress = Field(description="Progress information")

class SourceInfo(BaseModel):
    filename: Optional[str] = Field(description="Original filename")
    file_type: Optional[str] = Field(description="File type (pdf, txt, fountain)")
    language: str = Field(description="Detected language")
    total_pages: float = Field(description="Total estimated pages")
    extraction_method: Optional[str] = Field(description="Method used for text extraction")

# Content Models
class LocationInfo(BaseModel):
    name: str = Field(description="Location name")
    type: LocationType = Field(description="Interior or exterior")
    time_of_day: TimeOfDay = Field(description="Time of day")

class SceneContent(BaseModel):
    estimated_pages: float = Field(description="Estimated page count")
    dialogue_lines: List[str] = Field(description="Sample dialogue lines")
    action_lines: List[str] = Field(description="Action/description lines")
    special_requirements: List[str] = Field(description="Special requirements")

class NarrativeAnalysis(BaseModel):
    purpose: str = Field(description="Narrative purpose of scene")
    dramatic_weight: DramaticWeight = Field(description="Dramatic importance")
    emotional_tone: str = Field(description="Emotional tone")
    content_type: ContentType = Field(description="Content type classification")

class ProductionAnalysis(BaseModel):
    complexity: Complexity = Field(description="Production complexity")
    estimated_shoot_hours: int = Field(description="Estimated shooting hours")
    setup_hours: int = Field(description="Setup time in hours")
    crew_size: CrewSize = Field(description="Required crew size")
    equipment_needs: List[str] = Field(description="Equipment requirements")

class CostAnalysis(BaseModel):
    category: BudgetCategory = Field(description="Cost category")
    factors: List[str] = Field(description="Cost factors")

class SceneAnalysisData(BaseModel):
    narrative: NarrativeAnalysis = Field(description="Narrative analysis")
    production: ProductionAnalysis = Field(description="Production analysis")
    cost: CostAnalysis = Field(description="Cost analysis")

# Scene Model
class Scene(BaseModel):
    id: int = Field(description="Scene identifier")
    header: str = Field(description="Complete scene header")
    location: LocationInfo = Field(description="Location information")
    content: SceneContent = Field(description="Scene content")
    characters: List[str] = Field(description="Characters in scene")
    props: List[str] = Field(description="Props mentioned in scene")
    analysis: SceneAnalysisData = Field(description="Scene analysis")

# Character Models
class Character(BaseModel):
    name: str = Field(description="Character name")
    scenes: List[int] = Field(description="Scene IDs where character appears")
    scene_count: int = Field(description="Number of scenes")
    role_type: str = Field(description="Role type (protagonist, antagonist, supporting)")
    casting_notes: str = Field(description="Casting requirements")

class CharacterInteraction(BaseModel):
    scene_id: int = Field(description="Scene ID")
    characters: List[str] = Field(description="Characters involved")
    relationship: str = Field(description="Relationship type")
    dialogue_complexity: Complexity = Field(description="Dialogue complexity")

class CharactersData(BaseModel):
    main: List[Character] = Field(description="Main characters")
    supporting: List[Character] = Field(description="Supporting characters")
    interactions: List[CharacterInteraction] = Field(description="Character interactions")

# Location Models
class LocationDetail(BaseModel):
    name: str = Field(description="Location name")
    scenes: List[int] = Field(description="Scene IDs at this location")
    setup_complexity: Complexity = Field(description="Setup complexity")
    permit_required: bool = Field(description="Whether permit is required")
    equipment_access: str = Field(description="Equipment access level")

class ShootingGroup(BaseModel):
    location: str = Field(description="Location name")
    scenes: List[int] = Field(description="Scene IDs")
    estimated_days: int = Field(description="Estimated shooting days")

class LocationsData(BaseModel):
    interior: List[LocationDetail] = Field(description="Interior locations")
    exterior: List[LocationDetail] = Field(description="Exterior locations")
    shooting_groups: List[ShootingGroup] = Field(description="Shooting groups by location")

# Props and Wardrobe Models
class SceneProps(BaseModel):
    scene_id: int = Field(description="Scene ID")
    required: List[str] = Field(description="Required props")
    complexity: Complexity = Field(description="Props complexity")

class CharacterWardrobe(BaseModel):
    scenes: List[int] = Field(description="Scene IDs")
    requirements: List[str] = Field(description="Wardrobe requirements")
    changes: int = Field(description="Number of costume changes")

class SetDecoration(BaseModel):
    location: str = Field(description="Location name")
    requirements: List[str] = Field(description="Set decoration requirements")

class PropsData(BaseModel):
    by_category: Dict[str, List[str]] = Field(description="Props organized by category")
    by_scene: List[SceneProps] = Field(description="Props by scene")

class WardrobeData(BaseModel):
    by_character: Dict[str, CharacterWardrobe] = Field(description="Wardrobe by character")

class PropsAndWardrobeData(BaseModel):
    props: PropsData = Field(description="Props data")
    wardrobe: WardrobeData = Field(description="Wardrobe data")
    set_decoration: List[SetDecoration] = Field(description="Set decoration requirements")

# Production Planning Models
class LocationSchedule(BaseModel):
    location: str = Field(description="Location name")
    scenes: List[int] = Field(description="Scene IDs")
    estimated_days: int = Field(description="Estimated days")
    priority: str = Field(description="Scheduling priority")

class CastSchedule(BaseModel):
    scenes: List[int] = Field(description="Scene IDs")
    total_days: int = Field(description="Total shooting days")
    consecutive: bool = Field(description="Whether days are consecutive")

class ScheduleData(BaseModel):
    total_shoot_days: int = Field(description="Total shooting days")
    by_location: List[LocationSchedule] = Field(description="Schedule by location")
    cast_schedule: Dict[str, CastSchedule] = Field(description="Cast scheduling")

class SceneBudget(BaseModel):
    scene_id: int = Field(description="Scene ID")
    category: BudgetCategory = Field(description="Budget category")
    factors: List[str] = Field(description="Cost factors")

class BudgetData(BaseModel):
    overall_category: BudgetCategory = Field(description="Overall budget category")
    major_cost_drivers: List[str] = Field(description="Major cost drivers")
    optimization_opportunities: List[str] = Field(description="Cost optimization opportunities")
    scene_breakdown: List[SceneBudget] = Field(description="Budget by scene")

class SceneCrew(BaseModel):
    scene_id: int = Field(description="Scene ID")
    crew_size: CrewSize = Field(description="Required crew size")
    specialists: List[str] = Field(description="Specialist crew members")

class CrewRequirements(BaseModel):
    core_crew: List[str] = Field(description="Core crew positions")
    by_scene: List[SceneCrew] = Field(description="Crew requirements by scene")

class ProductionPlanning(BaseModel):
    schedule: ScheduleData = Field(description="Production schedule")
    budget: BudgetData = Field(description="Budget information")
    crew_requirements: CrewRequirements = Field(description="Crew requirements")

# Aggregate Models
class ScriptSummary(BaseModel):
    total_scenes: int = Field(description="Total number of scenes")
    total_characters: int = Field(description="Total number of characters")
    total_locations: int = Field(description="Total number of locations")
    estimated_shoot_days: int = Field(description="Estimated shooting days")
    budget_category: BudgetCategory = Field(description="Overall budget category")

class ScriptBreakdown(BaseModel):
    summary: ScriptSummary = Field(description="Script summary")
    scenes: List[Scene] = Field(description="All scenes")
    characters: CharactersData = Field(description="Character data")
    locations: LocationsData = Field(description="Location data")
    props_and_wardrobe: PropsAndWardrobeData = Field(description="Props and wardrobe data")

class ValidationData(BaseModel):
    data_complete: bool = Field(description="Whether all data is complete")
    json_valid: bool = Field(description="Whether JSON structure is valid")
    analysis_errors: List[str] = Field(description="Analysis errors encountered")

class HumanReviewData(BaseModel):
    completed: bool = Field(description="Whether human review is completed")
    feedback_incorporated: bool = Field(description="Whether feedback was incorporated")
    revisions_needed: Dict[str, bool] = Field(description="Revisions needed by section")

class QualityControl(BaseModel):
    validation: ValidationData = Field(description="Data validation results")
    human_review: HumanReviewData = Field(description="Human review status")

# Main Response Model
class EnhancedScriptAnalysisResponse(BaseModel):
    meta: MetaInfo = Field(description="Response metadata")
    workflow: WorkflowInfo = Field(description="Workflow information")
    source: SourceInfo = Field(description="Source file information")
    script_breakdown: ScriptBreakdown = Field(description="Script breakdown data")
    production_planning: ProductionPlanning = Field(description="Production planning data")
    quality_control: QualityControl = Field(description="Quality control information")
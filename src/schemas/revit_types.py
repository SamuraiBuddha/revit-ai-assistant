"""Pydantic models representing Revit types"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
from datetime import datetime

class RevitElement(BaseModel):
    """Base Revit element representation"""
    id: str = Field(description="Element ID")
    category: str = Field(description="Element category")
    family: Optional[str] = Field(None, description="Family name if applicable")
    type: Optional[str] = Field(None, description="Type name")
    level: Optional[str] = Field(None, description="Associated level")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
class RevitPhase(BaseModel):
    """Project phase information"""
    id: str
    name: str
    sequence_number: int
    description: Optional[str] = None
    
class RevitView(BaseModel):
    """View information"""
    id: str
    name: str
    view_type: str  # FloorPlan, Section, 3D, etc.
    level: Optional[str] = None
    phase: Optional[str] = None
    scale: Optional[int] = None
    
class ElementVisibility(BaseModel):
    """Element visibility settings"""
    element_id: str
    view_id: str
    is_visible: bool
    is_hidden_by_category: bool = False
    is_hidden_by_filter: bool = False
    override_settings: Dict[str, Any] = Field(default_factory=dict)
    
class CoordinateSystem(BaseModel):
    """Project coordinate information"""
    survey_point: tuple[float, float, float]
    project_base_point: tuple[float, float, float]
    true_north_rotation: float
    shared_coordinates_acquired: bool = False
    
class ExportSettings(BaseModel):
    """Export configuration"""
    format: str = Field(description="DWG, IFC, NWC, FBX, etc.")
    view_ids: List[str] = Field(description="Views to export")
    settings: Dict[str, Any] = Field(default_factory=dict)
    output_path: str
    
@dataclass
class RevitContext:
    """Shared context for all agents"""
    project_path: str
    project_name: str
    active_view_id: str
    active_phase_id: Optional[str]
    selected_element_ids: List[str]
    user_preferences: Dict[str, Any]
    standards_db: Any  # Vector database connection
    api_docs_index: Any  # API documentation index
    revit_api: Any  # Revit API wrapper
    
    def __post_init__(self):
        """Initialize empty collections if None"""
        if self.selected_element_ids is None:
            self.selected_element_ids = []
        if self.user_preferences is None:
            self.user_preferences = {}
            
    @property
    def has_selection(self) -> bool:
        """Check if elements are selected"""
        return len(self.selected_element_ids) > 0
        
    @property
    def selection_count(self) -> int:
        """Number of selected elements"""
        return len(self.selected_element_ids)
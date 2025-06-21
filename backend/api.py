from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
import uuid
import json
import traceback
import tempfile
import os

from graph.workflow import run_analyze_script_workflow, resume_workflow, get_workflow_state
from graph.workflow import run_analyze_script_workflow_from_file
from services.data_transformer import DataTransformer
from models.models import EnhancedScriptAnalysisResponse

# Constants
ALLOWED_FILE_TYPES = ['.pdf', '.txt', '.fountain']
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
API_VERSION = "2.0.0"
MIN_CONTENT_LENGTH = 10

# Initialize FastAPI app
app = FastAPI(title="Enhanced Script Analysis API", version=API_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"]
)

# Request Models
class ScriptRequest(BaseModel):
    script_content: str

class FeedbackRequest(BaseModel):
    thread_id: str
    feedback: Dict[str, str]
    needs_revision: Dict[str, bool]

# Initialize data transformer
transformer = DataTransformer()

# Response Helpers
def create_success_response(data: dict, message: str = "Success") -> JSONResponse:
    """Create standardized success JSON response with datetime handling"""
    try:
        serializable_data = json.loads(json.dumps(data, default=str))
        return JSONResponse(
            content=serializable_data,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        print(f"⚠️ JSON serialization error: {e}")
        return JSONResponse(
            content=_convert_datetime_to_string(data),
            headers={"Content-Type": "application/json"}
        )

def create_error_response(message: str, status_code: int = 500, details: str = None) -> JSONResponse:
    """Create standardized error JSON response"""
    response_data = {
        "meta": {
            "success": False,
            "version": API_VERSION,
            "timestamp": datetime.now().isoformat()
        },
        "error": {
            "message": message,
            "details": details
        }
    }
    
    return JSONResponse(
        content=response_data,
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )

def _convert_datetime_to_string(obj):
    """Recursively convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: _convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetime_to_string(item) for item in obj]
    elif hasattr(obj, 'dict'):
        return _convert_datetime_to_string(obj.dict())
    elif hasattr(obj, '__dict__'):
        return _convert_datetime_to_string(obj.__dict__)
    else:
        return obj

# File Processing Helpers
def _validate_file_type(filename: str) -> bool:
    """Validate uploaded file type"""
    if not filename:
        return False
    
    file_suffix = Path(filename).suffix.lower()
    return file_suffix in ALLOWED_FILE_TYPES

async def _process_uploaded_file(file: UploadFile) -> str:
    """Process uploaded file and return temporary file path"""
    if not _validate_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
        )
    
    file_suffix = Path(file.filename).suffix.lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        return temp_file.name

def _cleanup_temp_file(file_path: str):
    """Clean up temporary file safely"""
    try:
        os.unlink(file_path)
    except OSError:
        pass  # File might already be deleted

def _generate_thread_id() -> str:
    """Generate unique thread ID"""
    return f"script_{uuid.uuid4().hex[:8]}"

def _validate_script_content(content: str):
    """Validate script content"""
    if not content or len(content.strip()) < MIN_CONTENT_LENGTH:
        raise ValueError("Script content is too short or empty")

# API Endpoints
@app.post("/analyze-script-file")
async def analyze_script_file(file: UploadFile = File(...)):
    """Analyze script from uploaded PDF or text file"""
    temp_file_path = None
    
    try:
        temp_file_path = await _process_uploaded_file(file)
        thread_id = _generate_thread_id()
        
        print(f"🚀 Starting analysis for uploaded file: {file.filename}")
        
        result = await run_analyze_script_workflow_from_file(
            temp_file_path, 
            thread_id=thread_id
        )
        
        enhanced_response = transformer.transform_to_enhanced_structure(
            result, 
            thread_id, 
            file.filename
        )
        
        return create_success_response(
            enhanced_response.dict(),
            f"Analysis completed for {file.filename}"
        )
        
    except ValueError as e:
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        print(f"❌ File analysis failed: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return create_error_response("File analysis failed", details=str(e))
    finally:
        if temp_file_path:
            _cleanup_temp_file(temp_file_path)

@app.post("/analyze-script")
async def analyze_script(request: ScriptRequest):
    """Initial script analysis from text content"""
    try:
        _validate_script_content(request.script_content)
        
        thread_id = _generate_thread_id()
        print(f"🚀 Starting analysis for thread: {thread_id}")
        
        result = await run_analyze_script_workflow(
            request.script_content, 
            thread_id=thread_id
        )
        
        enhanced_response = transformer.transform_to_enhanced_structure(
            result,
            thread_id
        )
        
        return create_success_response(
            enhanced_response.dict(),
            "Initial analysis completed"
        )
        
    except ValueError as e:
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return create_error_response("Analysis failed", details=str(e))

@app.post("/submit-feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit human feedback and trigger revisions"""
    try:
        print(f"📝 Processing feedback for thread: {request.thread_id}")
        
        revisions_requested = [k for k, v in request.needs_revision.items() if v]
        print(f"Revisions requested: {revisions_requested}")
        
        if not any(request.needs_revision.values()):
            return await _handle_no_revisions_needed(request.thread_id)
        
        return await _handle_revisions_needed(request)
        
    except ValueError as e:
        return create_error_response(str(e), status_code=404)
    except Exception as e:
        print(f"❌ Feedback processing failed: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return create_error_response("Feedback processing failed", details=str(e))

async def _handle_no_revisions_needed(thread_id: str):
    """Handle case where no revisions are needed"""
    current_state = await get_workflow_state(thread_id)
    if current_state:
        current_state.human_review_complete = True
        current_state.task_complete = True
        
        enhanced_response = transformer.transform_to_enhanced_structure(
            current_state, 
            thread_id
        )
        
        return create_success_response(
            enhanced_response.dict(),
            "All analyses approved. Analysis complete!"
        )
    else:
        raise ValueError("Workflow not found")

async def _handle_revisions_needed(request: FeedbackRequest):
    """Handle case where revisions are needed"""
    human_feedback = {
        "feedback": request.feedback,
        "needs_revision": request.needs_revision
    }
    
    result = await resume_workflow(request.thread_id, human_feedback)
    
    enhanced_response = transformer.transform_to_enhanced_structure(
        result, 
        request.thread_id
    )
    
    message = ("Revisions processed. Please review the updated results." 
              if not result.task_complete else "All revisions complete!")
    
    return create_success_response(
        enhanced_response.dict(),
        message
    )

@app.get("/workflow-status/{thread_id}")
async def get_workflow_status(thread_id: str):
    """Get current workflow status"""
    try:
        state = await get_workflow_state(thread_id)
        if not state:
            return create_error_response("Workflow not found", status_code=404)
        
        enhanced_response = transformer.transform_to_enhanced_structure(
            state, 
            thread_id
        )
        
        return create_success_response(
            enhanced_response.dict(),
            "Status retrieved successfully"
        )
        
    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        return create_error_response("Failed to get workflow status", details=str(e))

@app.get("/scenes/{thread_id}/{scene_id}")
async def get_scene_data(thread_id: str, scene_id: int):
    """Get specific scene data"""
    try:
        state = await get_workflow_state(thread_id)
        if not state:
            return create_error_response("Workflow not found", status_code=404)
        
        enhanced_response = transformer.transform_to_enhanced_structure(
            state, 
            thread_id
        )
        
        scene_data = _find_scene_by_id(enhanced_response.script_breakdown.scenes, scene_id)
        if not scene_data:
            return create_error_response(f"Scene {scene_id} not found", status_code=404)
        
        return create_success_response(
            scene_data.dict(),
            f"Scene {scene_id} data retrieved"
        )
        
    except Exception as e:
        print(f"❌ Scene data retrieval failed: {str(e)}")
        return create_error_response("Failed to get scene data", details=str(e))

def _find_scene_by_id(scenes, scene_id: int):
    """Find scene by ID"""
    for scene in scenes:
        if scene.id == scene_id:
            return scene
    return None

@app.get("/departments/{thread_id}/{department}")
async def get_department_data(thread_id: str, department: str):
    """Get department-specific data"""
    try:
        state = await get_workflow_state(thread_id)
        if not state:
            return create_error_response("Workflow not found", status_code=404)
        
        enhanced_response = transformer.transform_to_enhanced_structure(
            state, 
            thread_id
        )
        
        department_data = _extract_department_data(enhanced_response, department)
        if department_data is None:
            return create_error_response(f"Unknown department: {department}", status_code=400)
        
        return create_success_response(
            department_data,
            f"{department.title()} data retrieved"
        )
        
    except Exception as e:
        print(f"❌ Department data retrieval failed: {str(e)}")
        return create_error_response("Failed to get department data", details=str(e))

def _extract_department_data(enhanced_response, department: str) -> Optional[dict]:
    """Extract department-specific data"""
    department_mapping = {
        "props": lambda r: r.script_breakdown.props_and_wardrobe.dict(),
        "locations": lambda r: r.script_breakdown.locations.dict(),
        "casting": lambda r: r.script_breakdown.characters.dict(),
        "budget": lambda r: r.production_planning.budget.dict(),
        "schedule": lambda r: r.production_planning.schedule.dict()
    }
    
    extractor = department_mapping.get(department)
    return extractor(enhanced_response) if extractor else None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return create_success_response(
        {
            "meta": {
                "success": True,
                "version": API_VERSION,
                "timestamp": datetime.now().isoformat()
            },
            "status": "healthy",
            "message": "Enhanced Script Analysis API is running"
        },
        "API is healthy"
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler to ensure JSON responses"""
    print(f"❌ Unhandled exception: {str(exc)}")
    print(f"Full traceback: {traceback.format_exc()}")
    
    return create_error_response(
        "Internal server error",
        status_code=500,
        details=str(exc)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
from typing import Any, List, Dict
import asyncio
import inspect
import json
from graph.state import ScriptAnalysisState

# Constants
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2
JSON_SERIALIZABLE_TYPES = (str, int, float, bool, type(None))

def extract_result(result: Any) -> Any:
    """Extract actual result from agent response and ensure JSON serializable"""
    try:
        # Extract result from different response formats
        for attr in ['output', 'data', 'content']:
            if hasattr(result, attr):
                extracted = getattr(result, attr)
                return ensure_json_serializable(extracted)
        
        return ensure_json_serializable(result)
    except Exception as e:
        print(f"⚠️ Error extracting result: {e}")
        return {"error": f"Result extraction failed: {str(e)}"}

def ensure_json_serializable(data: Any) -> Any:
    """Ensure data is JSON serializable"""
    try:
        json.dumps(data, default=str)
        return data
    except (TypeError, ValueError) as e:
        print(f"⚠️ Data not JSON serializable, converting: {e}")
        return convert_to_json_serializable(data)

def convert_to_json_serializable(obj: Any) -> Any:
    """Convert objects to JSON serializable format"""
    if isinstance(obj, JSON_SERIALIZABLE_TYPES):
        return obj
    
    if hasattr(obj, 'dict'):
        try:
            return obj.dict()
        except Exception:
            pass
    
    if hasattr(obj, '__dict__'):
        try:
            return {k: convert_to_json_serializable(v) for k, v in obj.__dict__.items()}
        except Exception:
            pass
    
    if isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    
    return str(obj)

async def safe_call_agent(agent_func, *args, **kwargs):
    """Safely call an agent function with error handling and JSON validation"""
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔄 Calling {_get_function_name(agent_func)} (attempt {attempt + 1})")
            
            result = await _execute_agent_function(agent_func, *args, **kwargs)
            
            if result is None:
                raise ValueError("Agent returned None result")
            
            json_result = ensure_json_serializable(result)
            print(f"✅ Agent call successful: {_get_function_name(agent_func)}")
            return json_result
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt == MAX_RETRIES - 1:
                print(f"❌ All attempts failed for {_get_function_name(agent_func)}")
                return create_fallback_result(_get_function_name(agent_func))
            
            await asyncio.sleep(RETRY_DELAY_BASE ** attempt)

async def _execute_agent_function(agent_func, *args, **kwargs):
    """Execute agent function handling both sync and async"""
    if inspect.iscoroutinefunction(agent_func):
        return await agent_func(*args, **kwargs)
    else:
        result = agent_func(*args, **kwargs)
        if inspect.iscoroutine(result):
            return await result
        return result

def _get_function_name(func) -> str:
    """Get function name safely"""
    return getattr(func, '__name__', 'unknown')

def create_fallback_result(agent_name: str) -> Dict[str, Any]:
    """Create JSON-serializable fallback result when agent fails"""
    print(f"🔧 Creating JSON fallback result for {agent_name}")
    
    fallback_templates = {
        'analyze_costs': _create_cost_fallback,
        'analyze_props': _create_props_fallback,
        'analyze_locations': _create_location_fallback,
        'analyze_characters': _create_character_fallback,
        'analyze_scenes': _create_scene_fallback,
        'analyze_timeline': _create_timeline_fallback,
    }
    
    fallback_func = fallback_templates.get(agent_name, _create_generic_fallback)
    return fallback_func(agent_name)

def _create_cost_fallback(agent_name: str) -> Dict[str, Any]:
    """Create cost analysis fallback"""
    return {
        'scene_costs': [],
        'total_budget_range': "Unable to estimate - API Error",
        'estimated_total_days': 0,
        'major_cost_drivers': ["API Error - Unable to analyze"],
        'cost_optimization_tips': ["Please retry analysis"]
    }

def _create_props_fallback(agent_name: str) -> Dict[str, Any]:
    """Create props analysis fallback"""
    return {
        'scene_props': [],
        'master_props_list': ["Unable to analyze - API Error"],
        'props_by_category': {"error": ["API Error"]},
        'costume_by_character': {},
        'prop_budget_estimate': "Unknown - API Error"
    }

def _create_location_fallback(agent_name: str) -> Dict[str, Any]:
    """Create location analysis fallback"""
    return {
        'scene_locations': [],
        'unique_locations': ["Unable to analyze - API Error"],
        'locations_by_type': {"error": ["API Error"]},
        'location_shooting_groups': ["Unable to group - API Error"],
        'permit_requirements': ["Unable to determine - API Error"]
    }

def _create_character_fallback(agent_name: str) -> Dict[str, Any]:
    """Create character analysis fallback"""
    return {
        'scene_characters': [],
        'main_characters': ["Unable to analyze - API Error"],
        'supporting_characters': [],
        'character_scene_count': {},
        'casting_requirements': ["Unable to determine - API Error"]
    }

def _create_scene_fallback(agent_name: str) -> Dict[str, Any]:
    """Create scene analysis fallback"""
    return {
        'detailed_scenes': [],
        'three_act_structure': ["Unable to analyze - API Error"],
        'pacing_analysis': "Unable to analyze - API Error",
        'key_dramatic_scenes': [],
        'action_heavy_scenes': [],
        'dialogue_heavy_scenes': []
    }

def _create_timeline_fallback(agent_name: str) -> Dict[str, Any]:
    """Create timeline analysis fallback"""
    return {
        'scene_timelines': [],
        'total_shooting_days': 0,
        'shooting_schedule_by_location': ["Unable to estimate - API Error"],
        'cast_scheduling': {},
        'pre_production_timeline': ["Unable to plan - API Error"],
        'post_production_timeline': ["Unable to plan - API Error"]
    }

def _create_generic_fallback(agent_name: str) -> Dict[str, Any]:
    """Create generic fallback"""
    return {
        "error": f"Unable to process {agent_name} - API Error",
        "message": "Please retry the analysis"
    }

def should_revise(state: ScriptAnalysisState) -> List[str]:
    """Determine which nodes need revision"""
    node_mapping = {
        "cost": "cost_node",
        "props": "props_node", 
        "location": "location_node",
        "character": "character_node",
        "scene": "scene_node",
        "timeline": "timeline_node"
    }
    
    if not state.needs_revision:
        return []
    
    return [node_mapping[analysis_type] 
            for analysis_type, needs_revision in state.needs_revision.items() 
            if needs_revision and analysis_type in node_mapping]

def validate_json_structure(data: Any, expected_fields: List[str] = None) -> bool:
    """Validate that data has expected JSON structure"""
    try:
        json.dumps(data, default=str)
        
        if expected_fields and isinstance(data, dict):
            missing_fields = [field for field in expected_fields if field not in data]
            if missing_fields:
                print(f"⚠️ Missing expected fields: {missing_fields}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False

def sanitize_for_json(data: Any) -> Any:
    """Sanitize data to ensure JSON compatibility"""
    if isinstance(data, JSON_SERIALIZABLE_TYPES):
        return data
    
    if isinstance(data, (list, tuple)):
        return [sanitize_for_json(item) for item in data]
    
    if isinstance(data, dict):
        return {str(k): sanitize_for_json(v) for k, v in data.items()}
    
    if hasattr(data, 'dict'):
        try:
            return sanitize_for_json(data.dict())
        except Exception:
            pass
    
    if hasattr(data, '__dict__'):
        try:
            return sanitize_for_json(data.__dict__)
        except Exception:
            pass
    
    return str(data)
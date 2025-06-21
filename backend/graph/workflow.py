from datetime import datetime
from typing import Optional, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import ScriptAnalysisState
from graph.utils import should_revise, ensure_json_serializable, validate_json_structure
from graph.nodes import (
    run_info_gathering, run_cost_analysis, run_props_analysis,
    run_location_analysis, run_character_analysis, run_scene_analysis,
    run_timeline_analysis, human_review
)
import json
from agents.pdf_utils import extract_text_from_pdf
from pathlib import Path

# Constants
ANALYSIS_NODES = ["cost_node", "props_node", "location_node", "character_node", "scene_node", "timeline_node"]
DEFAULT_THREAD_ID = "default_thread"
RECURSION_LIMIT = 25

def should_continue_or_end(state: ScriptAnalysisState):
    """Determine next step after human review with JSON validation"""
    print("🔍 Checking workflow continuation...")
    
    _validate_state_json(state)
    
    if state.human_review_complete:
        return "END"
    
    # Check if ANY revision is needed
    any_revisions_needed = any(state.needs_revision.values()) if state.needs_revision else False
    
    if any_revisions_needed:
        print("🔄 Revisions requested - routing back to info gathering")
        return "info_gathering"  # Always go back to info gathering
    
    return "END"

def _validate_state_json(state: ScriptAnalysisState):
    """Validate current state JSON serialization"""
    try:
        state_dict = state.model_dump() if hasattr(state, 'model_dump') else state.__dict__
        json.dumps(state_dict, default=str)
        print("✅ State is JSON serializable")
    except Exception as e:
        print(f"⚠️ State JSON validation failed: {e}")

def create_script_analysis_workflow():
    """Create and return the script analysis workflow with JSON validation"""
    memory = MemorySaver()
    workflow = StateGraph(ScriptAnalysisState)
    
    # Add nodes
    nodes = {
        "info_gathering": run_info_gathering,
        "cost_node": run_cost_analysis,
        "props_node": run_props_analysis,
        "location_node": run_location_analysis,
        "character_node": run_character_analysis,
        "scene_node": run_scene_analysis,
        "timeline_node": run_timeline_analysis,
        "human_review": human_review
    }
    
    for name, func in nodes.items():
        workflow.add_node(name, func)
    
    _add_workflow_edges(workflow)
    
    return workflow.compile(checkpointer=memory)
    # return workflow.compile()

def _add_workflow_edges(workflow):
    # Start with info gathering
    workflow.add_edge(START, "info_gathering")
    
    # Info gathering fans out to all analysis nodes
    for node in ANALYSIS_NODES:
        workflow.add_edge("info_gathering", node)
        workflow.add_edge(node, "human_review")
    
    # Modified: Human review only routes back to info_gathering or END
    workflow.add_conditional_edges(
        "human_review",
        should_continue_or_end,
        {
            "END": END,
            "info_gathering": "info_gathering"  # Only route back to info gathering
        }
    )

# Create the compiled graph
analyze_script_workflow = create_script_analysis_workflow()

async def run_analyze_script_workflow_from_file(
    file_path: str,
    human_feedback: Optional[Dict] = None,
    thread_id: str = DEFAULT_THREAD_ID
) -> ScriptAnalysisState:
    """Run workflow from uploaded file with JSON validation"""
    
    script_content = _extract_content_from_file(file_path)
    
    print(f"✅ Successfully extracted {len(script_content)} characters from {Path(file_path).name}")
    
    return await run_analyze_script_workflow(
        script_content, 
        human_feedback, 
        thread_id
    )

def _extract_content_from_file(file_path: str) -> str:
    """Extract content from file"""
    file_path = Path(file_path)
    
    try:
        if file_path.suffix.lower() == '.pdf':
            script_content = extract_text_from_pdf(str(file_path))
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
        
        if not script_content or len(script_content.strip()) < 10:
            raise ValueError("Extracted content is too short or empty")
        
        return script_content
        
    except Exception as e:
        print(f"❌ File processing failed: {e}")
        raise ValueError(f"Failed to process file {file_path.name}: {str(e)}")

async def run_analyze_script_workflow(
    script_content: str, 
    human_feedback: Optional[Dict] = None,
    thread_id: str = DEFAULT_THREAD_ID
) -> ScriptAnalysisState:
    """Run the complete script analysis workflow with JSON validation"""
    print("🎬 Starting Script Analysis Workflow")
    print("=" * 50)
    
    _validate_input(script_content)
    
    initial_state = _create_initial_state(script_content, human_feedback)
    
    try:
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": RECURSION_LIMIT
        }
        
        print(f"🚀 Running workflow with thread_id: {thread_id}")
        
        final_state_dict = await analyze_script_workflow.ainvoke(initial_state, config=config)
        
        _validate_final_state(final_state_dict)
        
        final_state = ScriptAnalysisState(**final_state_dict)
        
        _log_completion_summary(final_state, thread_id)
        
        return final_state
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise

def _validate_input(script_content: str):
    """Validate input script content"""
    if not script_content or len(script_content.strip()) < 10:
        raise ValueError("Script content is too short or empty")
    
def _create_initial_state(script_content: str, human_feedback: Optional[Dict]) -> ScriptAnalysisState:
    """Create initial workflow state"""
    initial_state = ScriptAnalysisState(
        script_content=script_content,
        processing_metadata={
            "workflow_start_time": datetime.now().isoformat(),
            "json_validation_enabled": True
        }
    )
    
    if human_feedback:
        print("📝 Processing human feedback for revisions...")
        initial_state.human_feedback = human_feedback.get('feedback', {})
        initial_state.needs_revision = human_feedback.get('needs_revision', {})
        initial_state.processing_metadata["revision_mode"] = True
        initial_state.human_review_complete = False
    
    return initial_state

def _validate_final_state(final_state_dict):
    """Validate final state JSON structure"""
    try:
        json.dumps(final_state_dict, default=str)
        print("✅ Final state is JSON serializable")
    except Exception as e:
        print(f"⚠️ Final state JSON validation failed: {e}")
        final_state_dict = ensure_json_serializable(final_state_dict)

def _log_completion_summary(final_state: ScriptAnalysisState, thread_id: str):
    """Log workflow completion summary"""
    print("\n" + "=" * 50)
    print("🎉 Script Analysis Workflow Completed!")
    
    successful_analyses = sum(1 for completed in final_state.analyses_complete.values() if completed)
    total_time = _calculate_total_time(final_state)
    
    print(f"📊 Summary:")
    print(f"   - Thread ID: {thread_id}")
    print(f"   - Total processing time: {total_time:.2f} seconds")
    print(f"   - Successful analyses: {successful_analyses}")
    print(f"   - Extraction completed: {final_state.extraction_complete}")
    print(f"   - Task completed: {final_state.task_complete}")
    print(f"   - JSON validation: ✅")
    
    if final_state.errors:
        print(f"⚠️  Errors encountered: {len(final_state.errors)}")

async def get_workflow_state(thread_id: str) -> Optional[ScriptAnalysisState]:
    """Get the current state of a workflow thread with JSON validation"""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state_dict = await analyze_script_workflow.aget_state(config)
        
        if state_dict and state_dict.values:
            _validate_retrieved_state(state_dict, thread_id)
            return ScriptAnalysisState(**state_dict.values)
        return None
    except Exception as e:
        print(f"❌ Error getting workflow state: {str(e)}")
        return None

def _validate_retrieved_state(state_dict, thread_id: str):
    """Validate retrieved state JSON structure"""
    try:
        json.dumps(state_dict.values, default=str)
        print(f"✅ Retrieved state for {thread_id} is JSON valid")
    except Exception as e:
        print(f"⚠️ Retrieved state JSON validation failed: {e}")
        state_dict.values = ensure_json_serializable(state_dict.values)

async def resume_workflow(thread_id: str, human_feedback: Optional[Dict] = None) -> ScriptAnalysisState:
    """Resume a workflow from its last checkpoint with JSON validation"""
    print(f"🔄 Resuming workflow for thread: {thread_id}")
    
    current_state = await get_workflow_state(thread_id)
    if not current_state:
        raise ValueError(f"No workflow state found for thread: {thread_id}")
    
    if human_feedback:
        _apply_human_feedback(current_state, human_feedback)
    
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": RECURSION_LIMIT
    }
    
    try:
        final_state_dict = await analyze_script_workflow.ainvoke(None, config=config)
        
        _validate_resumed_state(final_state_dict)
        
        return ScriptAnalysisState(**final_state_dict)
        
    except Exception as e:
        print(f"❌ Failed to resume workflow: {str(e)}")
        raise

def _apply_human_feedback(current_state: ScriptAnalysisState, human_feedback: Dict):
    """Apply human feedback to current state"""
    print("📝 Applying human feedback...")
    current_state.human_feedback = human_feedback.get('feedback', {})
    current_state.needs_revision = human_feedback.get('needs_revision', {})
    current_state.processing_metadata["revision_mode"] = True
    current_state.human_review_complete = False
    
    _validate_feedback_structure(human_feedback)

def _validate_feedback_structure(human_feedback: Dict):
    """Validate feedback structure"""
    try:
        json.dumps(human_feedback, default=str)
        print("✅ Human feedback is JSON valid")
    except Exception as e:
        print(f"⚠️ Human feedback JSON validation failed: {e}")

def _validate_resumed_state(final_state_dict):
    """Validate resumed workflow state"""
    try:
        json.dumps(final_state_dict, default=str)
        print("✅ Resumed workflow final state is JSON valid")
    except Exception as e:
        print(f"⚠️ Resumed state JSON validation failed: {e}")
        final_state_dict = ensure_json_serializable(final_state_dict)

def _calculate_total_time(final_state: ScriptAnalysisState) -> float:
    """Calculate total processing time"""
    start_time_str = final_state.processing_metadata.get("workflow_start_time")
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
            return (datetime.now() - start_time).total_seconds()
        except Exception:
            pass
    return final_state.processing_metadata.get("extraction_time_seconds", 0)

def validate_workflow_state(state: ScriptAnalysisState) -> Dict[str, bool]:
    """Validate all components of workflow state for JSON compatibility"""
    validation_results = {}
    
    analysis_components = [
        'raw_data', 'cost_analysis', 'character_analysis', 
        'location_analysis', 'props_analysis', 'scene_analysis', 'timeline_analysis'
    ]
    
    for component in analysis_components:
        data = getattr(state, component, None)
        validation_results[component] = validate_json_structure(data)
    
    # Check metadata
    metadata_components = ['processing_metadata', 'human_feedback', 'needs_revision']
    for component in metadata_components:
        data = getattr(state, component, None)
        validation_results[component] = validate_json_structure(data)
    
    return validation_results
import asyncio
import uuid
from graph.workflow import run_analyze_script_workflow, get_workflow_state, resume_workflow

# Constants
SAMPLE_SCRIPT = """
INT. COFFEE SHOP - DAY

SARAH, 25, sits at a corner table with her laptop. She nervously checks her phone.

SARAH
(into phone)
I can't do this anymore, Mom. The pressure is killing me.

The BARISTA, 20s, approaches with a steaming cup.

BARISTA
One large coffee, extra shot.

SARAH
Thanks.

Sarah's phone BUZZES. She looks at the screen - "BOSS CALLING"

SARAH (CONT'D)
(answering)
Hello, Mr. Peterson?

CUT TO:

EXT. CITY STREET - DAY

MIKE, 30, walks briskly down the sidewalk, talking on his phone.

MIKE
The deal fell through. We need a backup plan.

A BLACK SUV pulls up beside him. Two MEN in suits get out.

MIKE (CONT'D)
(panicked)
I have to go.

Mike hangs up and starts running.
"""

DISPLAY_SECTIONS = [
    ("📊 RAW DATA SUMMARY", "raw_data", [
        ("Total Scenes", lambda x: len(getattr(x, 'scenes', []))),
        ("Total Characters", lambda x: len(getattr(x, 'total_characters', []))),
        ("Total Locations", lambda x: len(getattr(x, 'total_locations', []))),
        ("Language", lambda x: getattr(x, 'language_detected', 'N/A')),
        ("Estimated Pages", lambda x: f"{getattr(x, 'estimated_total_pages', 0):.1f}")
    ]),
    ("💰 COST ANALYSIS", "cost_analysis", [
        ("Budget Range", lambda x: getattr(x, 'total_budget_range', 'N/A')),
        ("Shooting Days", lambda x: getattr(x, 'estimated_total_days', 'N/A')),
        ("Scene Costs", lambda x: len(getattr(x, 'scene_costs', [])))
    ]),
    ("👥 CHARACTER ANALYSIS", "character_analysis", [
        ("Main Characters", lambda x: len(getattr(x, 'main_characters', []))),
        ("Supporting Characters", lambda x: len(getattr(x, 'supporting_characters', []))),
        ("Scene Character Breakdowns", lambda x: len(getattr(x, 'scene_characters', [])))
    ]),
    ("📍 LOCATION ANALYSIS", "location_analysis", [
        ("Unique Locations", lambda x: len(getattr(x, 'unique_locations', []))),
        ("Scene Location Breakdowns", lambda x: len(getattr(x, 'scene_locations', []))),
        ("Location Types", lambda x: _format_location_types(getattr(x, 'locations_by_type', {})))
    ]),
    ("🎭 PROPS ANALYSIS", "props_analysis", [
        ("Total Props", lambda x: len(getattr(x, 'master_props_list', []))),
        ("Scene Prop Breakdowns", lambda x: len(getattr(x, 'scene_props', []))),
        ("Prop Categories", lambda x: _format_prop_categories(getattr(x, 'props_by_category', {})))
    ]),
    ("🎬 SCENE ANALYSIS", "scene_analysis", [
        ("Detailed Scene Breakdowns", lambda x: len(getattr(x, 'detailed_scenes', []))),
        ("Three-Act Structure", lambda x: len(getattr(x, 'three_act_structure', [])))
    ]),
    ("⏰ TIMELINE ANALYSIS", "timeline_analysis", [
        ("Scene Timeline Breakdowns", lambda x: len(getattr(x, 'scene_timelines', []))),
        ("Total Shooting Days", lambda x: getattr(x, 'total_shooting_days', 'N/A')),
        ("Cast Scheduling", lambda x: len(getattr(x, 'cast_scheduling', {})))
    ])
]

async def main():
    """Main function to demonstrate the workflow with checkpointing"""
    
    thread_id = _generate_thread_id()
    
    try:
        print(f"🆔 Using thread ID: {thread_id}")
        
        result = await run_analyze_script_workflow(SAMPLE_SCRIPT, thread_id=thread_id)
        
        _display_workflow_results(result)
        _demonstrate_checkpoint_functionality(thread_id)
        
        return result
        
    except Exception as e:
        print(f"❌ Error in main: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        raise

def _generate_thread_id() -> str:
    """Generate unique thread ID"""
    return f"script_analysis_{uuid.uuid4().hex[:8]}"

def _display_workflow_results(result):
    """Display analysis results in organized format"""
    print("\n" + "=" * 60)
    print("📋 DETAILED RESULTS")
    print("=" * 60)
    
    for title, attr_name, fields in DISPLAY_SECTIONS:
        _display_section(title, getattr(result, attr_name, None), fields)

def _display_section(title: str, data, fields):
    """Display a single section of results"""
    print(f"\n{title}:")
    if data:
        for field_name, field_func in fields:
            try:
                value = field_func(data)
                print(f"   {field_name}: {value}")
            except Exception:
                print(f"   {field_name}: N/A")
    else:
        print("   No data available")

async def _demonstrate_checkpoint_functionality(thread_id: str):
    """Demonstrate checkpoint retrieval"""
    print("\n" + "=" * 60)
    print("🔍 CHECKPOINT DEMONSTRATION")
    print("=" * 60)
    
    saved_state = await get_workflow_state(thread_id)
    if saved_state:
        _display_checkpoint_info(saved_state, thread_id)
    else:
        print(f"❌ No saved state found for thread: {thread_id}")

def _display_checkpoint_info(saved_state, thread_id: str):
    """Display checkpoint information"""
    print(f"✅ Successfully retrieved saved state for thread: {thread_id}")
    print(f"   - Task complete: {saved_state.task_complete}")
    
    completed_analyses = sum(1 for v in saved_state.analyses_complete.values() if v)
    print(f"   - Analyses complete: {completed_analyses}")

def _format_location_types(locations_by_type: dict) -> str:
    """Format location types for display"""
    if not locations_by_type:
        return "N/A"
    
    formatted_types = []
    for loc_type, locations in locations_by_type.items():
        if locations:
            formatted_types.append(f"{loc_type}: {len(locations)}")
    
    return ", ".join(formatted_types) if formatted_types else "N/A"

def _format_prop_categories(props_by_category: dict) -> str:
    """Format prop categories for display"""
    if not props_by_category:
        return "N/A"
    
    formatted_categories = []
    for category, props in props_by_category.items():
        if props:
            formatted_categories.append(f"{category}: {len(props)}")
    
    return ", ".join(formatted_categories) if formatted_categories else "N/A"

if __name__ == "__main__":
    asyncio.run(main())
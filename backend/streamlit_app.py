# streamlit_app.py
import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, List

# Configuration
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/analyze-script-file"
TEXT_ENDPOINT = f"{API_BASE_URL}/analyze-script"
FEEDBACK_ENDPOINT = f"{API_BASE_URL}/submit-feedback"
STATUS_ENDPOINT = f"{API_BASE_URL}/workflow-status"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Page configuration
st.set_page_config(
    page_title="Script Analysis Tool",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Utility Functions
def check_api_health() -> bool:
    """Check if the API is running"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        return response.status_code == 200
    except:
        return False

def safe_get(data: Dict, *keys, default=None):
    """Safely get nested dictionary values"""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data

def format_list_display(items: List[str], max_items: int = 5) -> str:
    """Format list for display with truncation"""
    if not items:
        return "None"
    
    displayed_items = items[:max_items]
    result = "\n".join([f"• {item}" for item in displayed_items])
    
    if len(items) > max_items:
        result += f"\n• ... and {len(items) - max_items} more"
    
    return result

# API Functions
def upload_file_analysis(uploaded_file):
    """Send file to API for analysis"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        with st.spinner("🔍 Analyzing script... This may take a few minutes."):
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=300)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            return None, safe_get(error_data, 'error', 'message', default=f"API Error: {response.status_code}")
    
    except requests.exceptions.Timeout:
        return None, "Analysis timed out. Please try with a shorter script."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Make sure the backend is running on localhost:8000"
    except Exception as e:
        return None, f"Error: {str(e)}"

def text_analysis(script_text: str):
    """Send text to API for analysis"""
    try:
        payload = {"script_content": script_text}
        
        with st.spinner("🔍 Analyzing script... This may take a few minutes."):
            response = requests.post(TEXT_ENDPOINT, json=payload, timeout=300)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            return None, safe_get(error_data, 'error', 'message', default=f"API Error: {response.status_code}")
    
    except requests.exceptions.Timeout:
        return None, "Analysis timed out. Please try with a shorter script."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Make sure the backend is running on localhost:8000"
    except Exception as e:
        return None, f"Error: {str(e)}"

def submit_feedback(thread_id: str, feedback: Dict[str, str], needs_revision: Dict[str, bool]):
    """Submit feedback to API"""
    try:
        payload = {
            "thread_id": thread_id,
            "feedback": feedback,
            "needs_revision": needs_revision
        }
        
        with st.spinner("📝 Processing feedback..."):
            response = requests.post(FEEDBACK_ENDPOINT, json=payload, timeout=120)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
            return None, safe_get(error_data, 'error', 'message', default=f"API Error: {response.status_code}")
    
    except Exception as e:
        return None, f"Error submitting feedback: {str(e)}"

# Display Functions
def display_script_summary(data: Dict[str, Any]):
    """Display script summary metrics"""
    try:
        summary = safe_get(data, 'script_breakdown', 'summary', default={})
        source = safe_get(data, 'source', default={})
        
        st.markdown("### 📊 Script Overview")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Scenes", safe_get(summary, 'total_scenes', default=0))
        with col2:
            st.metric("Total Characters", safe_get(summary, 'total_characters', default=0))
        with col3:
            st.metric("Total Locations", safe_get(summary, 'total_locations', default=0))
        with col4:
            st.metric("Estimated Shoot Days", safe_get(summary, 'estimated_shoot_days', default=0))
        
        # Additional info
        col1, col2, col3 = st.columns(3)
        with col1:
            budget = safe_get(summary, 'budget_category', default='unknown').title()
            st.metric("Budget Category", budget)
        with col2:
            pages = safe_get(source, 'total_pages', default=0)
            st.metric("Script Pages", f"{pages:.1f}")
        with col3:
            language = safe_get(source, 'language', default='Unknown')
            st.metric("Language", language)
    
    except Exception as e:
        st.error(f"Error displaying summary: {str(e)}")

def display_scenes_analysis(data: Dict[str, Any]):
    """Display scenes analysis"""
    try:
        scenes = safe_get(data, 'script_breakdown', 'scenes', default=[])
        
        if not scenes:
            st.warning("No scene data available")
            return
        
        st.markdown("### 🎬 Scene Breakdown")
        
        # Create scenes dataframe
        scene_data = []
        for scene in scenes:
            location_info = safe_get(scene, 'location', default={})
            content_info = safe_get(scene, 'content', default={})
            analysis_info = safe_get(scene, 'analysis', 'production', default={})
            
            scene_data.append({
                "Scene": safe_get(scene, 'id', default=0),
                "Header": safe_get(scene, 'header', default='Unknown'),
                "Location": safe_get(location_info, 'name', default='Unknown'),
                "Type": safe_get(location_info, 'type', default='unknown').title(),
                "Time": safe_get(location_info, 'time_of_day', default='unknown').title(),
                "Characters": len(safe_get(scene, 'characters', default=[])),
                "Props": len(safe_get(scene, 'props', default=[])),
                "Pages": f"{safe_get(content_info, 'estimated_pages', default=0):.1f}",
                "Complexity": safe_get(analysis_info, 'complexity', default='unknown').title(),
                "Shoot Hours": safe_get(analysis_info, 'estimated_shoot_hours', default=0)
            })
        
        df = pd.DataFrame(scene_data)
        st.dataframe(df, use_container_width=True)
        
        # Scene details expander
        with st.expander("📋 Detailed Scene Information"):
            if scenes:
                scene_options = [f"Scene {scene.get('id', i+1)}: {scene.get('header', 'Unknown')[:50]}..." 
                               for i, scene in enumerate(scenes)]
                selected_idx = st.selectbox("Select Scene", range(len(scene_options)), 
                                          format_func=lambda x: scene_options[x])
                
                if selected_idx is not None and selected_idx < len(scenes):
                    scene = scenes[selected_idx]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Characters:**")
                        characters = safe_get(scene, 'characters', default=[])
                        st.text(format_list_display(characters))
                        
                        st.markdown("**Props:**")
                        props = safe_get(scene, 'props', default=[])
                        st.text(format_list_display(props))
                    
                    with col2:
                        content = safe_get(scene, 'content', default={})
                        st.markdown("**Special Requirements:**")
                        special_reqs = safe_get(content, 'special_requirements', default=[])
                        st.text(format_list_display(special_reqs))
                        
                        narrative = safe_get(scene, 'analysis', 'narrative', default={})
                        st.markdown("**Analysis:**")
                        st.text(f"Purpose: {safe_get(narrative, 'purpose', default='Unknown')}")
                        st.text(f"Emotional Tone: {safe_get(narrative, 'emotional_tone', default='Unknown')}")
                        st.text(f"Content Type: {safe_get(narrative, 'content_type', default='Unknown')}")
    
    except Exception as e:
        st.error(f"Error displaying scenes: {str(e)}")

def display_characters_analysis(data: Dict[str, Any]):
    """Display character analysis"""
    try:
        characters_data = safe_get(data, 'script_breakdown', 'characters', default={})
        
        st.markdown("### 👥 Character Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Main Characters:**")
            main_chars = safe_get(characters_data, 'main', default=[])
            if main_chars:
                for char in main_chars:
                    name = safe_get(char, 'name', default='Unknown')
                    scene_count = safe_get(char, 'scene_count', default=0)
                    role_type = safe_get(char, 'role_type', default='unknown')
                    st.write(f"• **{name}** - {scene_count} scenes ({role_type})")
            else:
                st.write("No main characters identified")
        
        with col2:
            st.markdown("**Supporting Characters:**")
            supporting_chars = safe_get(characters_data, 'supporting', default=[])
            if supporting_chars:
                for char in supporting_chars:
                    name = safe_get(char, 'name', default='Unknown')
                    scene_count = safe_get(char, 'scene_count', default=0)
                    role_type = safe_get(char, 'role_type', default='unknown')
                    st.write(f"• **{name}** - {scene_count} scenes ({role_type})")
            else:
                st.write("No supporting characters identified")
        
        # Character interactions
        interactions = safe_get(characters_data, 'interactions', default=[])
        if interactions:
            st.markdown("**Character Interactions:**")
            for interaction in interactions[:5]:  # Show first 5
                scene_id = safe_get(interaction, 'scene_id', default=0)
                chars = ', '.join(safe_get(interaction, 'characters', default=[]))
                relationship = safe_get(interaction, 'relationship', default='Unknown')
                complexity = safe_get(interaction, 'dialogue_complexity', default='unknown')
                st.write(f"• Scene {scene_id}: {chars} - {relationship} ({complexity})")
    
    except Exception as e:
        st.error(f"Error displaying characters: {str(e)}")

def display_locations_analysis(data: Dict[str, Any]):
    """Display location analysis"""
    try:
        locations_data = safe_get(data, 'script_breakdown', 'locations', default={})
        
        st.markdown("### 📍 Location Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Interior Locations:**")
            interior_locs = safe_get(locations_data, 'interior', default=[])
            if interior_locs:
                for loc in interior_locs:
                    name = safe_get(loc, 'name', default='Unknown')
                    scenes = safe_get(loc, 'scenes', default=[])
                    complexity = safe_get(loc, 'setup_complexity', default='unknown').title()
                    st.write(f"• **{name}** - {len(scenes)} scenes ({complexity})")
            else:
                st.write("No interior locations identified")
        
        with col2:
            st.markdown("**Exterior Locations:**")
            exterior_locs = safe_get(locations_data, 'exterior', default=[])
            if exterior_locs:
                for loc in exterior_locs:
                    name = safe_get(loc, 'name', default='Unknown')
                    scenes = safe_get(loc, 'scenes', default=[])
                    permit = "🔒 Permit Required" if safe_get(loc, 'permit_required', default=False) else "✅ No Permit"
                    st.write(f"• **{name}** - {len(scenes)} scenes ({permit})")
            else:
                st.write("No exterior locations identified")
        
        # Shooting groups
        shooting_groups = safe_get(locations_data, 'shooting_groups', default=[])
        if shooting_groups:
            st.markdown("**Recommended Shooting Groups:**")
            for group in shooting_groups:
                location = safe_get(group, 'location', default='Unknown')
                scenes = safe_get(group, 'scenes', default=[])
                days = safe_get(group, 'estimated_days', default=0)
                st.write(f"• **{location}**: Scenes {', '.join(map(str, scenes))} ({days} days)")
        else:
            st.write("No shooting groups identified")
    
    except Exception as e:
        st.error(f"Error displaying locations: {str(e)}")

def display_props_and_wardrobe(data: Dict[str, Any]):
    """Display props and wardrobe analysis"""
    try:
        props_data = safe_get(data, 'script_breakdown', 'props_and_wardrobe', default={})
        
        st.markdown("### 🎭 Props & Wardrobe")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Props by Category:**")
            props_info = safe_get(props_data, 'props', default={})
            by_category = safe_get(props_info, 'by_category', default={})
            
            if by_category:
                for category, items in by_category.items():
                    if items:
                        st.write(f"**{category}:**")
                        st.text(format_list_display(items))
                        st.write("")
            else:
                st.write("No props categorized")
            
            # Set decoration
            st.markdown("**Set Decoration:**")
            set_decoration = safe_get(props_data, 'set_decoration', default=[])
            if set_decoration:
                for decoration in set_decoration:
                    location = safe_get(decoration, 'location', default='Unknown')
                    requirements = safe_get(decoration, 'requirements', default=[])
                    st.write(f"**{location}:**")
                    st.text(format_list_display(requirements))
            else:
                st.write("No set decoration requirements identified")
        
        with col2:
            st.markdown("**Wardrobe by Character:**")
            wardrobe_info = safe_get(props_data, 'wardrobe', default={})
            by_character = safe_get(wardrobe_info, 'by_character', default={})
            
            if by_character:
                for character, wardrobe_data in by_character.items():
                    requirements = safe_get(wardrobe_data, 'requirements', default=[])
                    changes = safe_get(wardrobe_data, 'changes', default=0)
                    scenes = safe_get(wardrobe_data, 'scenes', default=[])
                    
                    st.write(f"**{character}:**")
                    st.text(f"Scenes: {len(scenes)}")
                    st.text(f"Costume Changes: {changes}")
                    st.text("Requirements:")
                    st.text(format_list_display(requirements))
                    st.write("")
            else:
                st.write("No wardrobe requirements identified")
        
        # Props by scene
        st.markdown("**Props by Scene:**")
        by_scene = safe_get(props_info, 'by_scene', default=[])
        if by_scene:
            scene_props_data = []
            for scene_prop in by_scene:
                scene_props_data.append({
                    "Scene": safe_get(scene_prop, 'scene_id', default=0),
                    "Props Required": len(safe_get(scene_prop, 'required', default=[])),
                    "Complexity": safe_get(scene_prop, 'complexity', default='unknown').title(),
                    "Props List": ', '.join(safe_get(scene_prop, 'required', default=[])[:3]) + 
                                 ('...' if len(safe_get(scene_prop, 'required', default=[])) > 3 else '')
                })
            
            df_props = pd.DataFrame(scene_props_data)
            st.dataframe(df_props, use_container_width=True)
        else:
            st.write("No scene-specific props identified")
    
    except Exception as e:
        st.error(f"Error displaying props and wardrobe: {str(e)}")

def display_schedule_analysis(data: Dict[str, Any]):
    """Display schedule analysis"""
    try:
        schedule_data = safe_get(data, 'production_planning', 'schedule', default={})
        
        st.markdown("### 📅 Production Schedule")
        
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_days = safe_get(schedule_data, 'total_shoot_days', default=0)
            st.metric("Total Shooting Days", total_days)
        
        with col2:
            by_location = safe_get(schedule_data, 'by_location', default=[])
            st.metric("Locations to Schedule", len(by_location))
        
        with col3:
            cast_schedule = safe_get(schedule_data, 'cast_schedule', default={})
            st.metric("Cast Members", len(cast_schedule))
        
        # Schedule by location
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Schedule by Location:**")
            if by_location:
                location_schedule_data = []
                for loc_schedule in by_location:
                    location_schedule_data.append({
                        "Location": safe_get(loc_schedule, 'location', default='Unknown'),
                        "Scenes": ', '.join(map(str, safe_get(loc_schedule, 'scenes', default=[]))),
                        "Days": safe_get(loc_schedule, 'estimated_days', default=0),
                        "Priority": safe_get(loc_schedule, 'priority', default='medium').title()
                    })
                
                df_schedule = pd.DataFrame(location_schedule_data)
                st.dataframe(df_schedule, use_container_width=True)
            else:
                st.write("No location schedule available")
        
        with col2:
            st.markdown("**Cast Schedule:**")
            if cast_schedule:
                cast_schedule_data = []
                for character, schedule_info in cast_schedule.items():
                    scenes = safe_get(schedule_info, 'scenes', default=[])
                    total_days = safe_get(schedule_info, 'total_days', default=0)
                    consecutive = safe_get(schedule_info, 'consecutive', default=False)
                    
                    cast_schedule_data.append({
                        "Character": character,
                        "Scenes": len(scenes),
                        "Days": total_days,
                        "Consecutive": "Yes" if consecutive else "No"
                    })
                
                df_cast = pd.DataFrame(cast_schedule_data)
                st.dataframe(df_cast, use_container_width=True)
            else:
                st.write("No cast schedule available")
    
    except Exception as e:
        st.error(f"Error displaying schedule: {str(e)}")

def display_budget_analysis(data: Dict[str, Any]):
    """Display budget analysis"""
    try:
        budget_data = safe_get(data, 'production_planning', 'budget', default={})
        
        st.markdown("### 💰 Budget Analysis")
        
        # Overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Budget Overview:**")
            category = safe_get(budget_data, 'overall_category', default='unknown').title()
            st.metric("Budget Category", category)
            
            # Major cost drivers
            cost_drivers = safe_get(budget_data, 'major_cost_drivers', default=[])
            if cost_drivers:
                st.markdown("**Major Cost Drivers:**")
                st.text(format_list_display(cost_drivers))
            else:
                st.write("No cost drivers identified")
        
        with col2:
            # Optimization opportunities
            optimization = safe_get(budget_data, 'optimization_opportunities', default=[])
            if optimization:
                st.markdown("**💡 Cost Optimization Tips:**")
                st.text(format_list_display(optimization))
            else:
                st.write("No optimization tips available")
        
        # Scene budget breakdown
        st.markdown("**Budget by Scene:**")
        scene_breakdown = safe_get(budget_data, 'scene_breakdown', default=[])
        if scene_breakdown:
            budget_scene_data = []
            for scene_budget in scene_breakdown:
                factors = safe_get(scene_budget, 'factors', default=[])
                budget_scene_data.append({
                    "Scene": safe_get(scene_budget, 'scene_id', default=0),
                    "Budget Category": safe_get(scene_budget, 'category', default='unknown').title(),
                    "Cost Factors": ', '.join(factors[:2]) + ('...' if len(factors) > 2 else '')
                })
            
            df_budget = pd.DataFrame(budget_scene_data)
            st.dataframe(df_budget, use_container_width=True)
        else:
            st.write("No scene budget breakdown available")
    
    except Exception as e:
        st.error(f"Error displaying budget: {str(e)}")

def display_crew_requirements(data: Dict[str, Any]):
    """Display crew requirements"""
    try:
        crew_data = safe_get(data, 'production_planning', 'crew_requirements', default={})
        
        st.markdown("### 👷 Crew Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Core Crew Positions:**")
            core_crew = safe_get(crew_data, 'core_crew', default=[])
            if core_crew:
                st.text(format_list_display(core_crew))
            else:
                st.write("No core crew positions identified")
        
        with col2:
            st.markdown("**Crew Statistics:**")
            by_scene = safe_get(crew_data, 'by_scene', default=[])
            if by_scene:
                crew_sizes = [safe_get(scene_crew, 'crew_size', default='standard') for scene_crew in by_scene]
                crew_size_counts = {size: crew_sizes.count(size) for size in set(crew_sizes)}
                
                for size, count in crew_size_counts.items():
                    st.write(f"• {size.title()} crew: {count} scenes")
            else:
                st.write("No crew statistics available")
        
        # Crew by scene
        st.markdown("**Crew Requirements by Scene:**")
        if by_scene:
            crew_scene_data = []
            for scene_crew in by_scene:
                specialists = safe_get(scene_crew, 'specialists', default=[])
                crew_scene_data.append({
                    "Scene": safe_get(scene_crew, 'scene_id', default=0),
                    "Crew Size": safe_get(scene_crew, 'crew_size', default='standard').title(),
                    "Specialists": ', '.join(specialists) if specialists else 'None'
                })
            
            df_crew = pd.DataFrame(crew_scene_data)
            st.dataframe(df_crew, use_container_width=True)
        else:
            st.write("No scene crew requirements available")
    
    except Exception as e:
        st.error(f"Error displaying crew requirements: {str(e)}")

def display_feedback_section(data: Dict[str, Any]):
    """Display feedback section for revisions"""
    try:
        workflow = safe_get(data, 'workflow', default={})
        thread_id = safe_get(workflow, 'thread_id')
        
        if not thread_id:
            st.warning("No thread ID available for feedback")
            return
        
        st.markdown("### 📝 Feedback & Revisions")
        
        # Analysis sections for feedback
        analysis_sections = {
            "cost": "💰 Cost Analysis",
            "character": "👥 Character Analysis", 
            "location": "📍 Location Analysis",
            "props": "🎭 Props Analysis",
            "scene": "🎬 Scene Analysis",
            "timeline": "⏰ Timeline Analysis"
        }
        
        feedback = {}
        needs_revision = {}
        
        st.markdown("**Select sections that need revision and provide feedback:**")
        
        for section_key, section_name in analysis_sections.items():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                needs_revision[section_key] = st.checkbox(f"Revise {section_name}")
            
            with col2:
                if needs_revision[section_key]:
                    feedback[section_key] = st.text_area(
                        f"Feedback for {section_name}",
                        placeholder=f"What changes do you want for {section_name.lower()}?",
                        key=f"feedback_{section_key}"
                    )
                else:
                    feedback[section_key] = ""
        
        # Submit feedback button
        if st.button("🚀 Submit Feedback & Process Revisions", type="primary"):
            if any(needs_revision.values()):
                result, error = submit_feedback(thread_id, feedback, needs_revision)
                
                if error:
                    st.markdown(f'<div class="error-box">❌ {error}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box">✅ Feedback submitted successfully! Processing revisions...</div>', unsafe_allow_html=True)
                    st.rerun()
            else:
                st.warning("Please select at least one section for revision.")
    
    except Exception as e:
        st.error(f"Error displaying feedback section: {str(e)}")

def display_workflow_status(data: Dict[str, Any]):
    """Display workflow status"""
    try:
        workflow = safe_get(data, 'workflow', default={})
        
        st.markdown("### 📊 Workflow Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status = safe_get(workflow, 'status', default='unknown').title()
            st.metric("Status", status)
        
        with col2:
            progress = safe_get(workflow, 'progress', default={})
            percentage = safe_get(progress, 'percentage', default=0)
            st.metric("Progress", f"{percentage}%")
        
        with col3:
            thread_id = safe_get(workflow, 'thread_id', default='N/A')
            display_id = thread_id[:8] + "..." if len(thread_id) > 8 else thread_id
            st.metric("Thread ID", display_id)
        
        # Progress bar
        progress_data = safe_get(workflow, 'progress', default={})
        completed = safe_get(progress_data, 'completed_analyses', default=0)
        total = safe_get(progress_data, 'total_analyses', default=6)
        
        if total > 0:
            progress_percentage = completed / total
            st.progress(progress_percentage)
            st.caption(f"Completed {completed} of {total} analyses")
        
        # Quality control
        quality = safe_get(data, 'quality_control', default={})
        validation = safe_get(quality, 'validation', default={})
        human_review = safe_get(quality, 'human_review', default={})
        
        col1, col2, col3 = st.columns(3)

        with col1:
            data_complete = safe_get(validation, 'data_complete', default=False)
            st.write(f"Data Complete: {'✅' if data_complete else '❌'}")
        
        with col2:
            json_valid = safe_get(validation, 'json_valid', default=False)
            st.write(f"JSON Valid: {'✅' if json_valid else '❌'}")
        
        with col3:
            review_complete = safe_get(human_review, 'completed', default=False)
            st.write(f"Review Complete: {'✅' if review_complete else '❌'}")
        
        # Analysis errors
        errors = safe_get(validation, 'analysis_errors', default=[])
        if errors:
            st.markdown("**Analysis Errors:**")
            st.text(format_list_display(errors))
    
    except Exception as e:
        st.error(f"Error displaying workflow status: {str(e)}")

def render_input_section():
    """Render the input section for script upload/text"""
    with st.sidebar:
        st.markdown("## 🎯 Analysis Options")
        
        analysis_method = st.radio(
            "Choose input method:",
            ["📁 Upload Script File", "📝 Paste Script Text"]
        )
        
        st.markdown("---")
        st.markdown("### 📋 Supported Formats")
        st.markdown("• PDF files")
        st.markdown("• Text files (.txt)")
        st.markdown("• Fountain files (.fountain)")
        
        st.markdown("---")
        st.markdown("### ℹ️ How it works")
        st.markdown("1. Upload or paste your script")
        st.markdown("2. AI analyzes all aspects")
        st.markdown("3. Review results")
        st.markdown("4. Request revisions if needed")
    
    return analysis_method

def handle_file_upload():
    """Handle file upload analysis"""
    st.markdown("## 📁 Upload Script File")
    
    uploaded_file = st.file_uploader(
        "Choose a script file",
        type=['pdf', 'txt', 'fountain'],
        help="Upload a PDF, TXT, or Fountain script file"
    )
    
    if uploaded_file is not None:
        # File info
        file_size = uploaded_file.size
        st.markdown(f'<div class="info-box">📄 File: {uploaded_file.name} ({file_size:,} bytes)</div>', 
                   unsafe_allow_html=True)
        
        if st.button("🚀 Analyze Script", type="primary"):
            result, error = upload_file_analysis(uploaded_file)
            
            if error:
                st.markdown(f'<div class="error-box">❌ {error}</div>', unsafe_allow_html=True)
            else:
                st.session_state['analysis_result'] = result
                st.markdown('<div class="success-box">✅ Analysis completed successfully!</div>', 
                           unsafe_allow_html=True)
                st.rerun()

def handle_text_input():
    """Handle text input analysis"""
    st.markdown("## 📝 Paste Script Text")
    
    script_text = st.text_area(
        "Paste your script content here:",
        height=200,
        placeholder="INT. COFFEE SHOP - DAY\n\nSARAH sits at a corner table...",
        help="Paste the full script content in standard screenplay format"
    )
    
    if script_text.strip():
        word_count = len(script_text.split())
        st.markdown(f'<div class="info-box">📊 Word count: {word_count:,}</div>', 
                   unsafe_allow_html=True)
        
        if st.button("🚀 Analyze Script", type="primary"):
            if len(script_text.strip()) < 50:
                st.warning("⚠️ Script seems too short. Please provide more content.")
            else:
                result, error = text_analysis(script_text)
                
                if error:
                    st.markdown(f'<div class="error-box">❌ {error}</div>', unsafe_allow_html=True)
                else:
                    st.session_state['analysis_result'] = result
                    st.markdown('<div class="success-box">✅ Analysis completed successfully!</div>', 
                               unsafe_allow_html=True)
                    st.rerun()

def render_results_tabs(data: Dict[str, Any]):
    """Render the results tabs"""
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📊 Summary", "🎬 Scenes", "👥 Characters", "📍 Locations", 
        "🎭 Props & Wardrobe", "📅 Schedule", "💰 Budget", "👷 Crew", "📝 Feedback"
    ])
    
    with tab1:
        st.markdown('<h2 class="section-header">📊 Script Summary</h2>', unsafe_allow_html=True)
        display_script_summary(data)
    
    with tab2:
        display_scenes_analysis(data)
    
    with tab3:
        display_characters_analysis(data)
    
    with tab4:
        display_locations_analysis(data)
    
    with tab5:
        display_props_and_wardrobe(data)
    
    with tab6:
        display_schedule_analysis(data)
    
    with tab7:
        display_budget_analysis(data)
    
    with tab8:
        display_crew_requirements(data)
    
    with tab9:
        display_feedback_section(data)

def render_action_buttons(data: Dict[str, Any]):
    """Render action buttons for download and clear"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col2:
        if st.button("📥 Download Results as JSON", type="secondary"):
            json_str = json.dumps(data, indent=2, default=str)
            st.download_button(
                label="💾 Download JSON",
                data=json_str,
                file_name="script_analysis_results.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📊 View Status", type="secondary"):
            with st.expander("🔧 Workflow Status", expanded=True):
                display_workflow_status(data)
    
    with col4:
        if st.button("🗑️ Clear Results", type="secondary"):
            if 'analysis_result' in st.session_state:
                del st.session_state['analysis_result']
            st.rerun()

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎬 Script Analysis Tool</h1>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.markdown("""
        <div class="error-box">
            ❌ Cannot connect to the API. Please make sure the backend is running on localhost:8000
            <br><br>
            <strong>To start the backend:</strong><br>
            <code>cd backend && python api.py</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown('<div class="success-box">✅ Connected to API</div>', unsafe_allow_html=True)
    
    # Render input section
    analysis_method = render_input_section()
    
    # Handle input based on method
    if analysis_method == "📁 Upload Script File":
        handle_file_upload()
    else:  # Paste text method
        handle_text_input()
    
    # Display results if available
    if 'analysis_result' in st.session_state:
        data = st.session_state['analysis_result']
        
        # Render results tabs
        render_results_tabs(data)
        
        # Render action buttons
        render_action_buttons(data)

if __name__ == "__main__":
    main()

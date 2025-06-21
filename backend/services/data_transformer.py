from typing import Dict, Any, List
from datetime import datetime
import time
import re
from models.models import *
from agents.info_gathering_agent import RawScriptData
from graph.state import ScriptAnalysisState

# Constants
MAIN_CHARACTER_THRESHOLD = 0.3
DEFAULT_ESTIMATED_DAYS = 1
DEFAULT_PRIORITY = "medium"
DEFAULT_EQUIPMENT_ACCESS = "good"
LANGUAGE_DETECTION_MULTIPLIER = 1.3

class DataTransformer:
    """Transforms legacy data structure to enhanced JSON structure"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def transform_to_enhanced_structure(
        self, 
        state: ScriptAnalysisState, 
        thread_id: str,
        filename: str = None
    ) -> EnhancedScriptAnalysisResponse:
        """Transform ScriptAnalysisState to enhanced JSON structure"""
        
        processing_time = int((time.time() - self.start_time) * 1000)
        
        return EnhancedScriptAnalysisResponse(
            meta=self._create_meta_info(state, processing_time),
            workflow=self._create_workflow_info(state, thread_id),
            source=self._create_source_info(state, filename),
            script_breakdown=self._create_script_breakdown(state),
            production_planning=self._create_production_planning(state),
            quality_control=self._create_quality_control(state)
        )
    
    def _create_meta_info(self, state: ScriptAnalysisState, processing_time: int) -> MetaInfo:
        """Create metadata information"""
        return MetaInfo(
            success=len(state.errors) == 0,
            version="1.0",
            timestamp=datetime.now().isoformat(),
            processing_time_ms=processing_time
        )
    
    def _create_workflow_info(self, state: ScriptAnalysisState, thread_id: str) -> WorkflowInfo:
        """Create workflow information"""
        completed = sum(1 for v in state.analyses_complete.values() if v)
        total = len(state.analyses_complete)
        
        status = self._determine_workflow_status(state)
        current_phase = "complete" if state.task_complete else "analyzing"
        
        return WorkflowInfo(
            thread_id=thread_id,
            status=status,
            current_phase=current_phase,
            requires_review=not state.human_review_complete,
            progress=WorkflowProgress(
                completed_analyses=completed,
                total_analyses=total,
                percentage=int((completed / total) * 100) if total > 0 else 0
            )
        )
    
    def _determine_workflow_status(self, state: ScriptAnalysisState) -> WorkflowStatus:
        """Determine workflow status from state"""
        if state.errors:
            return WorkflowStatus.FAILED
        elif state.task_complete:
            return WorkflowStatus.COMPLETED
        else:
            return WorkflowStatus.ANALYZING
    
    def _create_source_info(self, state: ScriptAnalysisState, filename: str) -> SourceInfo:
        """Create source file information"""
        raw_data = state.raw_data
        if not raw_data:
            return self._create_empty_source_info(filename)
        
        raw_dict = self._convert_to_dict(raw_data)
        file_type = self._determine_file_type(filename)
        
        return SourceInfo(
            filename=filename,
            file_type=file_type,
            language=raw_dict.get('language_detected', 'Unknown'),
            total_pages=raw_dict.get('estimated_total_pages', 0),
            extraction_method=state.processing_metadata.get('extraction_method', 'pdfplumber')
        )
    
    def _create_empty_source_info(self, filename: str) -> SourceInfo:
        """Create empty source info for error cases"""
        return SourceInfo(
            filename=filename,
            language="Unknown",
            total_pages=0
        )
    
    def _determine_file_type(self, filename: str) -> Optional[str]:
        """Determine file type from filename"""
        if not filename:
            return None
        
        file_type_map = {
            '.pdf': "pdf",
            '.txt': "txt",
            '.fountain': "fountain"
        }
        
        for ext, file_type in file_type_map.items():
            if filename.endswith(ext):
                return file_type
        
        return None
    
    def _create_script_breakdown(self, state: ScriptAnalysisState) -> ScriptBreakdown:
        """Create script breakdown data"""
        raw_data = state.raw_data
        if not raw_data:
            return self._create_empty_script_breakdown()
        
        raw_dict = self._convert_to_dict(raw_data)
        
        scenes = self._transform_scenes(raw_dict, state)
        characters = self._transform_characters(state)
        locations = self._transform_locations(state)
        props_and_wardrobe = self._transform_props_and_wardrobe(state)
        
        summary = self._create_script_summary(raw_dict, scenes, state)
        
        return ScriptBreakdown(
            summary=summary,
            scenes=scenes,
            characters=characters,
            locations=locations,
            props_and_wardrobe=props_and_wardrobe
        )
    
    def _create_script_summary(self, raw_dict: Dict, scenes: List[Scene], state: ScriptAnalysisState) -> ScriptSummary:
        """Create script summary"""
        return ScriptSummary(
            total_scenes=len(scenes),
            total_characters=len(raw_dict.get('total_characters', [])),
            total_locations=len(raw_dict.get('total_locations', [])),
            estimated_shoot_days=self._get_total_shoot_days(state),
            budget_category=self._get_overall_budget_category(state)
        )
    
    def _transform_scenes(self, raw_dict: Dict, state: ScriptAnalysisState) -> List[Scene]:
        """Transform scenes to enhanced structure"""
        scenes = []
        raw_scenes = raw_dict.get('scenes', [])
        
        for scene_data in raw_scenes:
            scene_dict = self._convert_to_dict(scene_data)
            scene = self._create_scene_from_dict(scene_dict, state)
            scenes.append(scene)
        
        return scenes
    
    def _create_scene_from_dict(self, scene_dict: Dict, state: ScriptAnalysisState) -> Scene:
        """Create Scene object from dictionary"""
        return Scene(
            id=scene_dict.get('scene_number', 0),
            header=scene_dict.get('scene_header', ''),
            location=self._create_location_info(scene_dict),
            content=self._create_scene_content(scene_dict),
            characters=scene_dict.get('characters_present', []),
            props=scene_dict.get('props_mentioned', []),
            analysis=self._create_scene_analysis(scene_dict, state)
        )
    
    def _create_location_info(self, scene_dict: Dict) -> LocationInfo:
        """Create location info from scene dictionary"""
        return LocationInfo(
            name=scene_dict.get('location', 'UNKNOWN'),
            type=self._map_location_type(scene_dict.get('scene_type')),
            time_of_day=self._map_time_of_day(scene_dict.get('time_of_day', 'DAY'))
        )
    
    def _create_scene_content(self, scene_dict: Dict) -> SceneContent:
        """Create scene content from dictionary"""
        return SceneContent(
            estimated_pages=scene_dict.get('estimated_pages', 0),
            dialogue_lines=scene_dict.get('dialogue_lines', []),
            action_lines=scene_dict.get('action_lines', []),
            special_requirements=scene_dict.get('special_requirements', [])
        )
    
    def _create_scene_analysis(self, scene_dict: Dict, state: ScriptAnalysisState) -> SceneAnalysisData:
        """Create scene analysis data"""
        scene_id = scene_dict.get('scene_number', 0)
        
        scene_analysis = self._get_scene_analysis_for_scene(state, scene_id)
        cost_analysis = self._get_cost_analysis_for_scene(state, scene_id)
        timeline_analysis = self._get_timeline_analysis_for_scene(state, scene_id)
        
        return SceneAnalysisData(
            narrative=self._create_narrative_analysis(scene_analysis),
            production=self._create_production_analysis(scene_analysis, cost_analysis, timeline_analysis),
            cost=self._create_cost_analysis_data(cost_analysis)
        )
    
    def _create_narrative_analysis(self, scene_analysis: Dict) -> NarrativeAnalysis:
        """Create narrative analysis"""
        return NarrativeAnalysis(
            purpose=scene_analysis.get('scene_purpose', 'Story progression'),
            dramatic_weight=self._map_dramatic_weight(scene_analysis.get('dramatic_weight', 'Medium')),
            emotional_tone=scene_analysis.get('emotional_tone', 'Neutral'),
            content_type=self._map_content_type(scene_analysis.get('action_vs_dialogue_ratio', 'Balanced'))
        )
    
    def _create_production_analysis(self, scene_analysis: Dict, cost_analysis: Dict, timeline_analysis: Dict) -> ProductionAnalysis:
        """Create production analysis"""
        return ProductionAnalysis(
            complexity=self._map_complexity(scene_analysis.get('production_complexity', 'Simple')),
            estimated_shoot_hours=timeline_analysis.get('estimated_shoot_time', 2),
            setup_hours=timeline_analysis.get('setup_time', 1),
            crew_size=self._map_crew_size(timeline_analysis.get('crew_requirements', [])),
            equipment_needs=cost_analysis.get('equipment_needs', [])
        )
    
    def _create_cost_analysis_data(self, cost_analysis: Dict) -> CostAnalysis:
        """Create cost analysis data"""
        return CostAnalysis(
            category=self._map_budget_category(cost_analysis.get('location_cost_category', 'Medium')),
            factors=cost_analysis.get('complexity_factors', [])
        )
    
    def _transform_characters(self, state: ScriptAnalysisState) -> CharactersData:
        """Transform character data"""
        char_analysis = state.character_analysis
        if not char_analysis:
            return CharactersData(main=[], supporting=[], interactions=[])
        
        char_dict = self._convert_to_dict(char_analysis)
        
        main_chars = self._parse_characters(char_dict.get('main_characters', []), 'main')
        supporting_chars = self._parse_characters(char_dict.get('supporting_characters', []), 'supporting')
        interactions = self._transform_interactions(char_dict.get('scene_characters', []))
        
        return CharactersData(
            main=main_chars,
            supporting=supporting_chars,
            interactions=interactions
        )
    
    def _parse_characters(self, char_strings: List[str], role_type: str) -> List[Character]:
        """Parse character strings into Character objects"""
        characters = []
        for char_str in char_strings:
            char_data = self._parse_character_string(char_str, role_type)
            if char_data:
                characters.append(char_data)
        return characters
    
    def _transform_interactions(self, scene_characters: List) -> List[CharacterInteraction]:
        """Transform scene characters into interactions"""
        interactions = []
        for scene_char in scene_characters:
            scene_dict = self._convert_to_dict(scene_char)
            
            if len(scene_dict.get('characters_in_scene', [])) > 1:
                interaction = self._create_character_interaction(scene_dict)
                interactions.append(interaction)
        
        return interactions
    
    def _create_character_interaction(self, scene_dict: Dict) -> CharacterInteraction:
        """Create character interaction from scene dictionary"""
        interactions = scene_dict.get('character_interactions', ['Unknown interaction'])
        relationship = interactions[0] if interactions else 'Unknown interaction'
        
        return CharacterInteraction(
            scene_id=scene_dict.get('scene_number', 0),
            characters=scene_dict.get('characters_in_scene', []),
            relationship=relationship,
            dialogue_complexity=self._map_complexity(scene_dict.get('dialogue_complexity', 'Moderate'))
        )
    
    def _transform_locations(self, state: ScriptAnalysisState) -> LocationsData:
        """Transform location data"""
        location_analysis = state.location_analysis
        if not location_analysis:
            return LocationsData(interior=[], exterior=[], shooting_groups=[])
        
        loc_dict = self._convert_to_dict(location_analysis)
        
        interior_locations, exterior_locations = self._categorize_locations(loc_dict.get('scene_locations', []))
        shooting_groups = self._transform_shooting_groups(loc_dict.get('location_shooting_groups', []))
        
        return LocationsData(
            interior=interior_locations,
            exterior=exterior_locations,
            shooting_groups=shooting_groups
        )
    
    def _categorize_locations(self, scene_locations: List) -> tuple:
        """Categorize locations into interior and exterior"""
        interior_locations = []
        exterior_locations = []
        
        for scene_loc in scene_locations:
            scene_dict = self._convert_to_dict(scene_loc)
            location_detail = self._create_location_detail(scene_dict)
            
            if 'INT' in scene_dict.get('location_type', ''):
                interior_locations.append(location_detail)
            else:
                exterior_locations.append(location_detail)
        
        return (self._merge_duplicate_locations(interior_locations), 
                self._merge_duplicate_locations(exterior_locations))
    
    def _create_location_detail(self, scene_dict: Dict) -> LocationDetail:
        """Create location detail from scene dictionary"""
        return LocationDetail(
            name=scene_dict.get('location_name', 'UNKNOWN'),
            scenes=[scene_dict.get('scene_number', 0)],
            setup_complexity=self._map_complexity(scene_dict.get('setup_complexity', 'Moderate')),
            permit_required=scene_dict.get('permit_needed', False),
            equipment_access=DEFAULT_EQUIPMENT_ACCESS
        )
    
    def _transform_shooting_groups(self, group_strings: List[str]) -> List[ShootingGroup]:
        """Transform shooting group strings"""
        shooting_groups = []
        for group_str in group_strings:
            group = self._parse_shooting_group(group_str)
            if group:
                shooting_groups.append(group)
        return shooting_groups
    
    def _transform_props_and_wardrobe(self, state: ScriptAnalysisState) -> PropsAndWardrobeData:
        """Transform props and wardrobe data"""
        props_analysis = state.props_analysis
        if not props_analysis:
            return self._create_empty_props_and_wardrobe()
        
        props_dict = self._convert_to_dict(props_analysis)
        
        props_by_scene = self._transform_props_by_scene(props_dict.get('scene_props', []))
        wardrobe_by_character = self._transform_wardrobe_by_character(props_dict.get('costume_by_character', {}))
        set_decoration = []  # Would need to be extracted from scene props or location analysis
        
        return PropsAndWardrobeData(
            props=PropsData(
                by_category=props_dict.get('props_by_category', {}),
                by_scene=props_by_scene
            ),
            wardrobe=WardrobeData(by_character=wardrobe_by_character),
            set_decoration=set_decoration
        )
    
    def _create_empty_props_and_wardrobe(self) -> PropsAndWardrobeData:
        """Create empty props and wardrobe data"""
        return PropsAndWardrobeData(
            props=PropsData(by_category={}, by_scene=[]),
            wardrobe=WardrobeData(by_character={}),
            set_decoration=[]
        )
    
    def _transform_props_by_scene(self, scene_props: List) -> List[SceneProps]:
        """Transform props by scene"""
        props_by_scene = []
        for scene_prop in scene_props:
            scene_dict = self._convert_to_dict(scene_prop)
            
            scene_props_obj = SceneProps(
                scene_id=scene_dict.get('scene_number', 0),
                required=scene_dict.get('props_needed', []),
                complexity=self._map_complexity(scene_dict.get('prop_complexity', 'Moderate'))
            )
            props_by_scene.append(scene_props_obj)
        
        return props_by_scene
    
    def _transform_wardrobe_by_character(self, costume_dict: Dict) -> Dict[str, CharacterWardrobe]:
        """Transform wardrobe by character"""
        wardrobe_by_character = {}
        for char_name, costume_list in costume_dict.items():
            wardrobe_by_character[char_name] = CharacterWardrobe(
                scenes=[],  # Would need to be populated from character analysis
                requirements=costume_list,
                changes=0  # Default value
            )
        return wardrobe_by_character
    
    def _create_production_planning(self, state: ScriptAnalysisState) -> ProductionPlanning:
        """Create production planning data"""
        timeline_analysis = state.timeline_analysis
        cost_analysis = state.cost_analysis
        
        schedule = self._create_schedule_data(timeline_analysis)
        budget = self._create_budget_data(cost_analysis)
        crew_requirements = self._create_crew_requirements(timeline_analysis)
        
        return ProductionPlanning(
            schedule=schedule,
            budget=budget,
            crew_requirements=crew_requirements
        )
    
    def _create_schedule_data(self, timeline_analysis) -> ScheduleData:
        """Create schedule data"""
        if not timeline_analysis:
            return ScheduleData(total_shoot_days=0, by_location=[], cast_schedule={})
        
        timeline_dict = self._convert_to_dict(timeline_analysis)
        
        by_location = self._transform_location_schedule(timeline_dict.get('shooting_schedule_by_location', []))
        cast_schedule = self._transform_cast_schedule(timeline_dict.get('cast_scheduling', {}))
        
        return ScheduleData(
            total_shoot_days=timeline_dict.get('total_shooting_days', 0),
            by_location=by_location,
            cast_schedule=cast_schedule
        )
    
    def _transform_location_schedule(self, schedule_strings: List[str]) -> List[LocationSchedule]:
        """Transform location schedule strings"""
        by_location = []
        for schedule_str in schedule_strings:
            location_schedule = self._parse_location_schedule(schedule_str)
            if location_schedule:
                by_location.append(location_schedule)
        return by_location
    
    def _transform_cast_schedule(self, cast_scheduling: Dict) -> Dict[str, CastSchedule]:
        """Transform cast schedule"""
        cast_schedule = {}
        for char_name, scene_list in cast_scheduling.items():
            cast_schedule[char_name] = CastSchedule(
                scenes=scene_list,
                total_days=len(set(scene_list)),  # Approximate
                consecutive=True  # Default assumption
            )
        return cast_schedule
    
    def _create_budget_data(self, cost_analysis) -> BudgetData:
        """Create budget data"""
        if not cost_analysis:
            return self._create_empty_budget_data()
        
        cost_dict = self._convert_to_dict(cost_analysis)
        scene_breakdown = self._transform_scene_budget(cost_dict.get('scene_costs', []))
        
        return BudgetData(
            overall_category=self._map_budget_category(cost_dict.get('total_budget_range', 'Medium')),
            major_cost_drivers=cost_dict.get('major_cost_drivers', []),
            optimization_opportunities=cost_dict.get('cost_optimization_tips', []),
            scene_breakdown=scene_breakdown
        )
    
    def _create_empty_budget_data(self) -> BudgetData:
        """Create empty budget data"""
        return BudgetData(
            overall_category=BudgetCategory.MEDIUM,
            major_cost_drivers=[],
            optimization_opportunities=[],
            scene_breakdown=[]
        )
    
    def _transform_scene_budget(self, scene_costs: List) -> List[SceneBudget]:
        """Transform scene budget breakdown"""
        scene_breakdown = []
        for scene_cost in scene_costs:
            scene_dict = self._convert_to_dict(scene_cost)
            
            scene_budget = SceneBudget(
                scene_id=scene_dict.get('scene_number', 0),
                category=self._map_budget_category(scene_dict.get('location_cost_category', 'Medium')),
                factors=scene_dict.get('complexity_factors', [])
            )
            scene_breakdown.append(scene_budget)
        
        return scene_breakdown
    
    def _create_crew_requirements(self, timeline_analysis) -> CrewRequirements:
        """Create crew requirements data"""
        if not timeline_analysis:
            return CrewRequirements(core_crew=[], by_scene=[])
        
        timeline_dict = self._convert_to_dict(timeline_analysis)
        
        core_crew = set()
        by_scene = []
        
        for scene_timeline in timeline_dict.get('scene_timelines', []):
            scene_dict = self._convert_to_dict(scene_timeline)
            
            crew_list = scene_dict.get('crew_requirements', [])
            core_crew.update(crew_list)
            
            scene_crew = SceneCrew(
                scene_id=scene_dict.get('scene_number', 0),
                crew_size=self._map_crew_size(crew_list),
                specialists=[]  # Would need to be extracted from special requirements
            )
            by_scene.append(scene_crew)
        
        return CrewRequirements(
            core_crew=list(core_crew),
            by_scene=by_scene
        )
    
    def _create_quality_control(self, state: ScriptAnalysisState) -> QualityControl:
        """Create quality control data"""
        return QualityControl(
            validation=ValidationData(
                data_complete=state.extraction_complete,
                json_valid=True,  # Assume true if we got this far
                analysis_errors=state.errors
            ),
            human_review=HumanReviewData(
                completed=state.human_review_complete,
                feedback_incorporated=bool(state.human_feedback),
                revisions_needed=state.needs_revision or {}
            )
        )
    
    # Helper methods for mapping and parsing
    def _convert_to_dict(self, obj) -> Dict:
        """Convert object to dictionary safely"""
        if hasattr(obj, 'dict'):
            return obj.dict()
        elif isinstance(obj, dict):
            return obj
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return {}
    
    def _map_location_type(self, scene_type: str) -> LocationType:
        """Map scene type to LocationType enum"""
        return LocationType.INTERIOR if scene_type == 'INT' else LocationType.EXTERIOR
    
    def _map_time_of_day(self, time_str: str) -> TimeOfDay:
        """Map time string to TimeOfDay enum"""
        time_mapping = {
            'NIGHT': TimeOfDay.NIGHT,
            'DAWN': TimeOfDay.DAWN,
            'DUSK': TimeOfDay.DUSK
        }
        
        time_str = time_str.upper()
        for key, value in time_mapping.items():
            if key in time_str:
                return value
        
        return TimeOfDay.DAY
    
    def _map_dramatic_weight(self, weight_str: str) -> DramaticWeight:
        """Map dramatic weight string to enum"""
        weight_mapping = {
            'high': DramaticWeight.HIGH,
            'low': DramaticWeight.LOW
        }
        
        weight_str = weight_str.lower()
        for key, value in weight_mapping.items():
            if key in weight_str:
                return value
        
        return DramaticWeight.MEDIUM
    
    def _map_content_type(self, content_str: str) -> ContentType:
        """Map content type string to enum"""
        content_str = content_str.lower()
        if 'dialogue' in content_str:
            return ContentType.DIALOGUE_HEAVY
        elif 'action' in content_str:
            return ContentType.ACTION_HEAVY
        else:
            return ContentType.BALANCED
    
    def _map_complexity(self, complexity_str: str) -> Complexity:
        """Map complexity string to enum"""
        complexity_mapping = {
            'complex': Complexity.COMPLEX,
            'simple': Complexity.SIMPLE
        }
        
        complexity_str = complexity_str.lower()
        for key, value in complexity_mapping.items():
            if key in complexity_str:
                return value
        
        return Complexity.MODERATE
    
    def _map_crew_size(self, crew_list: List[str]) -> CrewSize:
        """Map crew list to crew size enum"""
        crew_count = len(crew_list)
        if crew_count <= 3:
            return CrewSize.MINIMAL
        elif crew_count <= 6:
            return CrewSize.STANDARD
        else:
            return CrewSize.LARGE
    
    def _map_budget_category(self, budget_str: str) -> BudgetCategory:
        """Map budget string to enum"""
        budget_mapping = {
            'high': BudgetCategory.HIGH,
            'premium': BudgetCategory.HIGH,
            'low': BudgetCategory.LOW
        }
        
        budget_str = budget_str.lower()
        for key, value in budget_mapping.items():
            if key in budget_str:
                return value
        
        return BudgetCategory.MEDIUM
    
    def _parse_character_string(self, char_str: str, role_type: str) -> Optional[Character]:
        """Parse character string like 'SARAH - appears in 2 scenes'"""
        parts = char_str.split(' - ')
        if len(parts) >= 2:
            name = parts[0].strip()
            scene_info = parts[1].strip()
            
            scene_count = self._extract_scene_count(scene_info)
            
            return Character(
                name=name,
                scenes=[],  # Would need to be populated from raw data
                scene_count=scene_count,
                role_type=role_type,
                casting_notes=char_str
            )
        return None
    
    def _extract_scene_count(self, scene_info: str) -> int:
        """Extract scene count from scene info string"""
        scene_match = re.search(r'(\d+)', scene_info)
        return int(scene_match.group(1)) if scene_match else 1
    
    def _parse_shooting_group(self, group_str: str) -> Optional[ShootingGroup]:
        """Parse shooting group string like 'Shoot scenes 1,2 at COFFEE SHOP'"""
        scenes = self._extract_scenes_from_string(group_str)
        location = self._extract_location_from_string(group_str)
        
        return ShootingGroup(
            location=location,
            scenes=scenes,
            estimated_days=DEFAULT_ESTIMATED_DAYS
        )
    
    def _extract_scenes_from_string(self, group_str: str) -> List[int]:
        """Extract scene numbers from group string"""
        scene_match = re.search(r'scenes?\s+([\d,\s]+)', group_str)
        if scene_match:
            scene_str = scene_match.group(1)
            return [int(s.strip()) for s in scene_str.split(',') if s.strip().isdigit()]
        return []
    
    def _extract_location_from_string(self, group_str: str) -> str:
        """Extract location from group string"""
        location_match = re.search(r'at\s+(.+)$', group_str)
        return location_match.group(1).strip() if location_match else 'UNKNOWN'
    
    def _parse_location_schedule(self, schedule_str: str) -> Optional[LocationSchedule]:
        """Parse location schedule string"""
        scenes = self._extract_scenes_from_string(schedule_str)
        location = self._extract_location_from_string(schedule_str)
        
        return LocationSchedule(
            location=location,
            scenes=scenes,
            estimated_days=DEFAULT_ESTIMATED_DAYS,
            priority=DEFAULT_PRIORITY
        )
    
    def _merge_duplicate_locations(self, locations: List[LocationDetail]) -> List[LocationDetail]:
        """Merge locations with the same name"""
        location_map = {}
        
        for location in locations:
            if location.name in location_map:
                existing = location_map[location.name]
                existing.scenes.extend(location.scenes)
                existing.scenes = list(set(existing.scenes))  # Remove duplicates
            else:
                location_map[location.name] = location
        
        return list(location_map.values())
    
    def _get_scene_analysis_for_scene(self, state: ScriptAnalysisState, scene_id: int) -> Dict:
        """Get scene analysis data for specific scene"""
        if not state.scene_analysis:
            return {}
        
        scene_dict = self._convert_to_dict(state.scene_analysis)
        
        for scene in scene_dict.get('detailed_scenes', []):
            scene_data = self._convert_to_dict(scene)
            if scene_data.get('scene_number') == scene_id:
                return scene_data
        
        return {}
    
    def _get_cost_analysis_for_scene(self, state: ScriptAnalysisState, scene_id: int) -> Dict:
        """Get cost analysis data for specific scene"""
        if not state.cost_analysis:
            return {}
        
        cost_dict = self._convert_to_dict(state.cost_analysis)
        
        for scene in cost_dict.get('scene_costs', []):
            scene_data = self._convert_to_dict(scene)
            if scene_data.get('scene_number') == scene_id:
                return scene_data
        
        return {}
    
    def _get_timeline_analysis_for_scene(self, state: ScriptAnalysisState, scene_id: int) -> Dict:
        """Get timeline analysis data for specific scene"""
        if not state.timeline_analysis:
            return {}
        
        timeline_dict = self._convert_to_dict(state.timeline_analysis)
        
        for scene in timeline_dict.get('scene_timelines', []):
            scene_data = self._convert_to_dict(scene)
            if scene_data.get('scene_number') == scene_id:
                return scene_data
        
        return {}
    
    def _get_total_shoot_days(self, state: ScriptAnalysisState) -> int:
        """Get total shooting days from timeline analysis"""
        if not state.timeline_analysis:
            return 0
        
        timeline_dict = self._convert_to_dict(state.timeline_analysis)
        return timeline_dict.get('total_shooting_days', 0)
    
    def _get_overall_budget_category(self, state: ScriptAnalysisState) -> BudgetCategory:
        """Get overall budget category from cost analysis"""
        if not state.cost_analysis:
            return BudgetCategory.MEDIUM
        
        cost_dict = self._convert_to_dict(state.cost_analysis)
        budget_str = cost_dict.get('total_budget_range', 'Medium')
        return self._map_budget_category(budget_str)
    
    def _create_empty_script_breakdown(self) -> ScriptBreakdown:
        """Create empty script breakdown for error cases"""
        return ScriptBreakdown(
            summary=ScriptSummary(
                total_scenes=0,
                total_characters=0,
                total_locations=0,
                estimated_shoot_days=0,
                budget_category=BudgetCategory.MEDIUM
            ),
            scenes=[],
            characters=CharactersData(main=[], supporting=[], interactions=[]),
            locations=LocationsData(interior=[], exterior=[], shooting_groups=[]),
            props_and_wardrobe=PropsAndWardrobeData(
                props=PropsData(by_category={}, by_scene=[]),
                wardrobe=WardrobeData(by_character={}),
                set_decoration=[]
            )
        )
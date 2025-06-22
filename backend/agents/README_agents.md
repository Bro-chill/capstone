### backend/agents/pdf_utils.py
* **extract_text_from_pdf**: Extract text from PDF using 2 methods
  * extract_with_pdfplumber
  * extract_with_pypdf2
  * _is_valid extraction
  * clean_extracted_text

* **extract_with_pdfplumber**: Extract using pdfplumber 

* **extract_with_pypdf2**: Extract using PyPDF2

* **_is_valid_extraction**: Check extracted text is valid

* **clean_extracted_text**: Clean and normalize extracted text
  * _fix_concatenated_lines
  * _normalize_whitespace
  * _preserve_script_formatting

* **_fix_concatenated_lines**: Fix concatenated lines 

* **_normalize_whitespace**: Normalize whitespace

* **_preserve_script_formatting**: Preserve formatting patterns

* **validate_script_content**: Validate extracted text look like a script
---
### backend/agents/info_gathering_agent.py
* **extract_script_data_from_file**: Extract raw data from script
  * extract_text_from_pdf (pdf_utils.py)
  * validate_script_content (pdf_utils.py)
  * extract_script_data

* **extract_script_data**: Extract raw data from script(with human feedback)
  * _incorporate_feedback_into_extraction
  * _parse_scenes
  * _validate_scene_count
  * _alternative_scene_parsing
  * script_context
  * _parse_scene_manual
  * _aggregate_data
  * _fallback_extraction

* **_incorporate_feedback_into_extraction**: Human-in-the-loop

* **_parse_scenes**: Split script by scene

* **_parse_scene_manual**: Split script by scene(manually)
  * _match_scene_header
  * _parse_location_time
  * _is_character_name
  * _extract_props_and_special
  * _categorize_content

* **_validate_scene_count**: Validate between extracted and script

* **_alternative_scene_parsing**: Alternative method to split scene

* **_match_scene_header**: Identify scene header

* **_parse_location_time**: Time identifier

* **_is_character_name**: Name identifier

* **_extract_props_and_special**: Props identifier

* **_categorize_content**: Categorize dialogue or action

* **_aggregate_data**: Aggreate data by scene
  * _detect_language

* **_detect_language**: Detect language

* **_fallback_extraction**: Fallback when parsing fails
  * _is_character_name
  * _create_fallback_scenes

* **_create_fallback_scenes**: Fallback scenes
---
### backend/agents/character_analysis_agent.py
* **analyze_characters**: Analyze character by scene and overall
  * _create_fallback_scene_character
  * _count_character_appearances
  * _create_fallback_character_breakdown

* **_count_character_appearances**: Identify character appearances across scenes

* **_create_fallback_scene_character**: Fallback for character analysis by scene

* **_create_fallback_character_breakdown**: Fallback for overall character analysis
---
### backend/agents/cost_analysis_agent.py
* **analyze_costs**: Analyze cost by scene and overall
  * _create_fallback_scene_cost
  * _create_fallback_cost_breakdown

* **_create_fallback_scene_cost**: Fallback scene cost analysis

* **_create_fallback_cost_breakdown**: Fallback overall cost analysis
---
### backend/agents/location_analysis_agent.py
* **analyze_locations**: Analyze location by scene and overall 
  * _create_fallback_scene_location
  * _create_fallback_location_breakdown

* **_create_fallback_scene_location**: Fallback scene location analysis

* **_create_fallback_location_breakdown**: Fallback overall location analysis
  * _group_scenes_by_location

* **_group_scenes_by_location**: Group scene by location
---
### backend/agents/props_analysis_agent.py
* **analyze_props**: Analyze props by scene and overall
  * _create_fallback_scene_props
  * _extract_all_props
  * _create_fallback_props_breakdown

* **_extract_all_props**: Extract props from scene props

* **_create_fallback_scene_props**: Fallback scene props analysis
  * _get_location_props

* **_get_location_props**: Get props based on scene location

* **_create_fallback_props_breakdown**: Fallback overall props analysis
  * _categorize_props

* **_categorize_props**: Categorize props by type
---
### backend/agents/scene_analysis_agent.py
* **analyze_scenes**: Analyze scene structure and elements
  * _create_fallback_scene_breakdown
  * _create_fallback_scene_breakdown_overall

* **_create_fallback_scene_breakdown**: Fallback scene analysis
  * _determine_complexity
  * _determine_action_ratio

* **_determine_complexity**: Determine scene complexity

* **_determine_action_ratio**: Determine action vs dialogue ratio

* **_create_fallback_scene_breakdown_overall**: Fallback overall scene analysis
  * _create_three_act_structure

* **_create_three_act_structure**: 3-act structure breakdown
---
### backend/agents/timeline_analysis_agent.py
* **analyze_timeline**: Analyze timeline by scene and overall
  * _create_fallback_scene_timeline
  * _create_cast_scheduling
  * _create_fallback_timeline_breakdown

* **_create_cast_scheduling**: Cast scheduling by scenes

* **_create_fallback_scene_timeline**: Fallback scene timeline analysis

* **_create_fallback_timeline_breakdown**: Fallback overall timeline analysis
  * _group_scenes_by_location
  * _create_pre_production_timeline
  * _create_post_production_timeline

* **_group_scenes_by_location**: Group scenes by location

* **_create_pre_production_timeline**: Pre production timeline(mock)

* **_create_post_production_timeline**: Post production timeline(mock)
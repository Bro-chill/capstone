### backend/graph/state.py
* **merge_dict**
  * human_feedback
  * needs_revision
  * analyses_complete

* **merge_list**
  * errors

* **merge_bool**
  * task_complete
  * human_review_complete

* **merge_string**
  * current_agent

* **create_default_analyses_complete**
  * analyses_complete

* **create_default_needs_revision**
  * needs_revision
---
### backend/graph/utils.py
* **extract_result**: Extract result form agents
  * ensure_json_serialization

* **ensure_json_serialization**: Ensure data in JSON
  * convert_to_json_serializable

* **convert_to_json_serializable**: Convert data to JSON

* **safe_call_agent**: Safe call agents with JSON validation
  * _get_function_name
  * _execute_agent_function
  * ensure_json_serializable
  * _get_function_name
  * create_fallback_result

* **_execute_agent_function**: Execute agent sync & async
  * agent_func

* **_get_function_name**: Get function name safely

* **create_fallback_result**: Fallback when result from agents fails
  * fallback_func

* **_create_cost_fallback**: Cost analysis fallback

* **_create_props_fallback**: Props analysis fallback

* **_create_location_fallback**: Location analysis fallback

* **_create_character_fallback**: Character analysis fallback

* **_create_scene_fallback**: Scene analysis fallback

* **_create_timeline_fallback**: Timeline analysis fallback

* **_create_generic_fallback**: Analysis agents fallback

* **should_revise**: Determine specific nodes to revise

* **validate_json_structure**: Validate data in JSON structure

* **sanitize_for_json**: Sanitize data for JSON compatibility
---
### backend/graph/nodes.py
* **run_info_gathering**: Extract data from script with JSON validation
  * safe_call_agent
  * validate_json_structure
  * _create_fallback_raw_data
  * ensure_json_serializable
  * _log_extraction_summary

* **_log_extraction_summary**: Log summary

* **_create_fallback_raw_data**: Fallback data structure

* **create_analysis_node**: Generic analysis node with JSON validation
  * analysis_node
  * _create_error_response
  * safe_call_agent
  * extract_result
  * validate_json_structure
  * _create_fallback_analysis_result
  * ensure_json_serializable
  * _create_success_response
  * _create_error_response

* **_create_error_response**: Error response for analysis nodes

* **_create_success_response**: Success response for analysis nodes

* **_create_fallback_analysis_result**: Fallback for specific analysis node

* **human_review**: Human-in-the-loop with JSON validation
  * _validate_all_analyses
  * _handle_revision_mode
  * _handle_initial_review

* **_validate_all_analyses**: Validate current state data structure
  * validate_json_structure

* **_handle_revision_mode**: Handle revision mode processing

* **_handle_initial_review**: Handle initial review completion
---
### backend/graph/workflow.py
* **should_continue_or_end**: Next step after human review
  * _validate_state_json

* **_validate_state_json**: Validate current state JSON serialization

* **create_script_analysis_workflow**: Create and return script analysis
  * _add_workflow_edges

* **_add_workflow_edges**: START -> END
  * create_script_analysis_workflow

* **run_analyze_script_workflow_from_file**: Run workflow from uploaded file
  * _extract_content_from_file
  * run_analyze_script_workflow

* **_extract_content_from_file**: Extract content from file
  * extract_text_from_pdf

* **run_analyze_script_workflow**: Run analysis workflow with JSON validation
  * _validate_input
  * _create_initial_state
  * _validate_final_state
  * _log_completion_summary

* **_validate_input**: Validate input content

* **_create_initial_state**: Create initial workflow state

* **_validate_final_state**: Validate final JSON structure

* **_log_completion_summary**: Log workflow summary

* **get_workflow_state**: Get current state with JSON validation
  * _validate_retrieved_state

* **_validate_retrieved_state**: Validate JSON structure

* **resume_workflow**: Resume if JSON structure validated 
  * get_workflow_state
  * _apply_human_feedback
  * _validate_resumed_state

* **_apply_human_feedback**: Human-in-the-loop to current state
  * _validate_feedback_structure

* **_validate_feedback_structure**: Validate feedback structure

* **_validate_resumed_state**: Validate resumed structure

* **_calculate_total_time**: Calculate processing time

* **validate_workflow_state**: Validate all components JSON compatible
  * validate_json_structure
---
### backend/graph/main.py
* **main**: Main function
  * _generate_thread_id
  * run_analyze_script_workflow
  * _display_workflow_results
  * _demonstrate_checkpoint_functionality

* **_generate_thread_id**: Generate unique id for each script

* **_display_workflow_results**: Display analysis result
  * _display_section

* **_display_section**: Display single section of results

* **_demonstrate_checkpoint_functionality**: Checkpoint retrieval
  * get_workflow_state
  * _display_checkpoint_info

* **_display_checkpoint_info**: Checkpoint information

* **_format_location_types**: Format location types for display

* **_format_prop_categories**: Format prop categories for display
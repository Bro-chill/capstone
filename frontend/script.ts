import { defineStore } from "pinia";
import axios, { AxiosResponse, AxiosError } from "axios";

// Enhanced types matching the new backend structure
interface MetaInfo {
  success: boolean;
  version: string;
  timestamp: string;
  processing_time_ms?: number;
}

interface WorkflowProgress {
  completed_analyses: number;
  total_analyses: number;
  percentage: number;
}

interface WorkflowInfo {
  thread_id: string;
  status: 'initializing' | 'extracting' | 'analyzing' | 'reviewing' | 'completed' | 'failed';
  current_phase: string;
  requires_review: boolean;
  progress: WorkflowProgress;
}

interface SourceInfo {
  filename?: string;
  file_type?: string;
  language: string;
  total_pages: number;
  extraction_method?: string;
}

interface ScriptSummary {
  total_scenes: number;
  total_characters: number;
  total_locations: number;
  estimated_shoot_days: number;
  budget_category: 'low' | 'medium' | 'high' | 'premium';
}

interface LocationInfo {
  name: string;
  type: 'interior' | 'exterior';
  time_of_day: 'day' | 'night' | 'dawn' | 'dusk';
}

interface SceneContent {
  estimated_pages: number;
  dialogue_lines: string[];
  action_lines: string[];
  special_requirements: string[];
}

interface NarrativeAnalysis {
  purpose: string;
  dramatic_weight: 'low' | 'medium' | 'high';
  emotional_tone: string;
  content_type: 'dialogue_heavy' | 'action_heavy' | 'balanced';
}

interface ProductionAnalysis {
  complexity: 'simple' | 'moderate' | 'complex';
  estimated_shoot_hours: number;
  setup_hours: number;
  crew_size: 'minimal' | 'standard' | 'large';
  equipment_needs: string[];
}

interface CostAnalysis {
  category: 'low' | 'medium' | 'high' | 'premium';
  factors: string[];
}

interface SceneAnalysisData {
  narrative: NarrativeAnalysis;
  production: ProductionAnalysis;
  cost: CostAnalysis;
}

interface Scene {
  id: number;
  header: string;
  location: LocationInfo;
  content: SceneContent;
  characters: string[];
  props: string[];
  analysis: SceneAnalysisData;
}

// Character interfaces
interface Character {
  name: string;
  scenes: number[];
  scene_count: number;
  role_type: string;
  casting_notes: string;
}

interface CharacterInteraction {
  scene_id: number;
  characters: string[];
  relationship: string;
  dialogue_complexity: 'simple' | 'moderate' | 'complex';
}

interface CharactersData {
  main: Character[];
  supporting: Character[];
  interactions: CharacterInteraction[];
}

// Location interfaces
interface LocationDetail {
  name: string;
  scenes: number[];
  setup_complexity: 'simple' | 'moderate' | 'complex';
  permit_required: boolean;
  equipment_access: string;
}

interface ShootingGroup {
  location: string;
  scenes: number[];
  estimated_days: number;
}

interface LocationsData {
  interior: LocationDetail[];
  exterior: LocationDetail[];
  shooting_groups: ShootingGroup[];
}

// Props and Wardrobe interfaces
interface SceneProps {
  scene_id: number;
  required: string[];
  complexity: 'simple' | 'moderate' | 'complex';
}

interface PropsData {
  by_category: Record<string, string[]>;
  by_scene: SceneProps[];
}

interface CharacterWardrobe {
  scenes: number[];
  requirements: string[];
  changes: number;
}

interface WardrobeData {
  by_character: Record<string, CharacterWardrobe>;
}

interface SetDecoration {
  location: string;
  requirements: string[];
}

interface PropsAndWardrobeData {
  props: PropsData;
  wardrobe: WardrobeData;
  set_decoration: SetDecoration[];
}

// Production Planning interfaces
interface LocationSchedule {
  location: string;
  scenes: number[];
  estimated_days: number;
  priority: string;
}

interface CastSchedule {
  scenes: number[];
  total_days: number;
  consecutive: boolean;
}

interface ScheduleData {
  total_shoot_days: number;
  by_location: LocationSchedule[];
  cast_schedule: Record<string, CastSchedule>;
}

interface SceneBudget {
  scene_id: number;
  category: 'low' | 'medium' | 'high' | 'premium';
  factors: string[];
}

interface BudgetData {
  overall_category: 'low' | 'medium' | 'high' | 'premium';
  major_cost_drivers: string[];
  optimization_opportunities: string[];
  scene_breakdown: SceneBudget[];
}

interface SceneCrew {
  scene_id: number;
  crew_size: 'minimal' | 'standard' | 'large';
  specialists: string[];
}

interface CrewRequirements {
  core_crew: string[];
  by_scene: SceneCrew[];
}

interface ProductionPlanning {
  schedule: ScheduleData;
  budget: BudgetData;
  crew_requirements: CrewRequirements;
}

interface ScriptBreakdown {
  summary: ScriptSummary;
  scenes: Scene[];
  characters: CharactersData;
  locations: LocationsData;
  props_and_wardrobe: PropsAndWardrobeData;
}

interface QualityControl {
  validation: {
    data_complete: boolean;
    json_valid: boolean;
    analysis_errors: string[];
  };
  human_review: {
    completed: boolean;
    feedback_incorporated: boolean;
    revisions_needed: Record<string, boolean>;
  };
}

interface EnhancedScriptAnalysisResponse {
  meta: MetaInfo;
  workflow: WorkflowInfo;
  source: SourceInfo;
  script_breakdown: ScriptBreakdown;
  production_planning: ProductionPlanning;
  quality_control: QualityControl;
}

interface EnhancedApiResponse {
  meta: MetaInfo;
  workflow: WorkflowInfo;
  source: SourceInfo;
  script_breakdown: ScriptBreakdown;
  production_planning: ProductionPlanning;
  quality_control: QualityControl;
  message?: string;
  error?: {
    message: string;
    details?: string;
  };
}

interface FeedbackData {
  feedback: Record<string, string>;
  needs_revision: Record<string, boolean>;
}

interface ProductionSummary {
  totalShootDays: number;
  budgetCategory: string;
  locationCount: number;
  castMembers: number;
  coreCrew: number;
  majorCostDrivers: string[];
  optimizationTips: string[];
}

interface AnalysisSummary {
  // Script info
  totalScenes: number;
  totalCharacters: number;
  totalLocations: number;
  estimatedShootDays: number;
  budgetCategory: string;
  
  // Source info
  language: string;
  totalPages: number;
  fileType?: string;
  
  // Workflow info
  status: string;
  progress: number;
  requiresReview: boolean;
  
  // Quality info
  dataComplete: boolean;
  jsonValid: boolean;
  errors: string[];
}

// Create configured axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000, // Increased to 2 minutes for complex analysis
  headers: {
    'Accept': 'application/json',
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    config.headers['Accept'] = 'application/json';
    
    if (config.data && !(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json';
    }
    
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      headers: config.headers,
      dataType: config.data instanceof FormData ? 'FormData' : typeof config.data
    });
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Enhanced response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('✅ API Response received:', {
      status: response.status,
      contentType: response.headers['content-type'],
      dataType: typeof response.data,
      hasMetaSuccess: response.data?.meta?.success
    });
    
    // Validate content type
    const contentType = response.headers['content-type'];
    if (contentType && !contentType.includes('application/json')) {
      console.warn('⚠️ Response is not JSON:', contentType);
      throw new Error(`Expected JSON response, got ${contentType}`);
    }
    
    // Validate enhanced response structure
    if (typeof response.data !== 'object' || response.data === null) {
      console.error('❌ Response data is not an object:', response.data);
      throw new Error('Invalid response format - expected JSON object');
    }
    
    // Check for enhanced structure
    if (!response.data.meta || typeof response.data.meta.success !== 'boolean') {
      console.error('❌ Response missing meta.success field:', response.data);
      throw new Error('Invalid enhanced API response format');
    }
    
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    
    // Enhanced error extraction
    if (error.response?.data && typeof error.response.data === 'object') {
      const errorData = error.response.data as any;
      if (errorData.error?.message) {
        error.message = errorData.error.message;
      } else if (errorData.message) {
        error.message = errorData.message;
      }
    }
    
    return Promise.reject(error);
  }
);

// Enhanced type guards
function isEnhancedApiResponse(data: any): data is EnhancedApiResponse {
  return (
    data &&
    typeof data === 'object' &&
    data.meta &&
    typeof data.meta.success === 'boolean' &&
    data.workflow &&
    data.script_breakdown &&
    data.production_planning &&
    data.quality_control
  );
}

function isValidScriptBreakdown(data: any): boolean {
  return (
    data &&
    typeof data === 'object' &&
    data.summary &&
    Array.isArray(data.scenes) &&
    data.characters &&
    data.locations &&
    data.props_and_wardrobe
  );
}

function isValidCharactersData(data: any): data is CharactersData {
  return (
    data &&
    typeof data === 'object' &&
    Array.isArray(data.main) &&
    Array.isArray(data.supporting) &&
    Array.isArray(data.interactions)
  );
}

function isValidLocationsData(data: any): data is LocationsData {
  return (
    data &&
    typeof data === 'object' &&
    Array.isArray(data.interior) &&
    Array.isArray(data.exterior) &&
    Array.isArray(data.shooting_groups)
  );
}

function isValidPropsAndWardrobeData(data: any): data is PropsAndWardrobeData {
  return (
    data &&
    typeof data === 'object' &&
    data.props &&
    data.wardrobe &&
    Array.isArray(data.set_decoration)
  );
}

export const useScriptStore = defineStore('script', {
  state: () => ({
    // Enhanced analysis data
    analysisData: null as EnhancedScriptAnalysisResponse | null,
    
    // Workflow state
    threadId: null as string | null,
    isAnalyzing: false,
    isSubmittingFeedback: false,
    needsHumanReview: false,
    taskComplete: false,
    
    // File handling
    uploadedFile: null as File | null,
    fileName: '',
    
    // User feedback
    userFeedback: {} as Record<string, string>,
    revisionsNeeded: {} as Record<string, boolean>,
    
    // UI state
    currentStep: 'upload' as 'upload' | 'analyzing' | 'review' | 'complete',
    error: null as string | null,
    successMessage: null as string | null,
    
    // Analysis sections for review (updated keys)
    analysisSections: [
      { key: 'cost', label: 'Cost Analysis', icon: '💰' },
      { key: 'character', label: 'Character Analysis', icon: '👥' },
      { key: 'location', label: 'Location Analysis', icon: '📍' },
      { key: 'props', label: 'Props Analysis', icon: '🎭' },
      { key: 'scene', label: 'Scene Analysis', icon: '🎬' },
      { key: 'timeline', label: 'Timeline Analysis', icon: '⏰' }
    ]
  }),

  getters: {
    // Check if analysis is available
    hasAnalysisData: (state) => state.analysisData !== null,
    
    // Enhanced getters for new structure
    scriptSummary: (state): ScriptSummary | undefined => 
      state.analysisData?.script_breakdown?.summary,
    
    scenes: (state): Scene[] => 
      state.analysisData?.script_breakdown?.scenes || [],
    
    characters: (state): CharactersData | undefined => 
      state.analysisData?.script_breakdown?.characters,
    
    locations: (state): LocationsData | undefined => 
      state.analysisData?.script_breakdown?.locations,
    
    propsAndWardrobe: (state): PropsAndWardrobeData | undefined => 
      state.analysisData?.script_breakdown?.props_and_wardrobe,
    
    // Production planning getters
    budget: (state): BudgetData | undefined => 
      state.analysisData?.production_planning?.budget,
    
    schedule: (state): ScheduleData | undefined => 
      state.analysisData?.production_planning?.schedule,
    
    crewRequirements: (state): CrewRequirements | undefined => 
      state.analysisData?.production_planning?.crew_requirements,
    
    // Workflow getters
    workflowInfo: (state): WorkflowInfo | undefined => 
      state.analysisData?.workflow,
    
    sourceInfo: (state): SourceInfo | undefined => 
      state.analysisData?.source,
    
    qualityControl: (state): QualityControl | undefined => 
      state.analysisData?.quality_control,
    
    // Progress tracking (enhanced)
    completedAnalyses: (state): number => {
      return state.analysisData?.workflow?.progress?.completed_analyses || 0;
    },
    
    totalAnalyses: (state): number => {
      return state.analysisData?.workflow?.progress?.total_analyses || state.analysisSections.length;
    },
    
    progressPercentage: (state): number => {
      return state.analysisData?.workflow?.progress?.percentage || 0;
    },
    
    // Check if any revisions are pending
    hasPendingRevisions: (state): boolean => {
      const qualityControl = state.analysisData?.quality_control?.human_review?.revisions_needed;
      return qualityControl ? Object.values(qualityControl).some(Boolean) : 
             Object.values(state.revisionsNeeded).some(Boolean);
    },
    
    // Get sections that need revision
    sectionsNeedingRevision: (state): string[] => {
      const qualityControl = state.analysisData?.quality_control?.human_review?.revisions_needed;
      const revisions = qualityControl || state.revisionsNeeded;
      return Object.entries(revisions)
        .filter(([_, needs]) => needs)
        .map(([key, _]) => key);
    },

    // Enhanced analysis getters with fallbacks
    costAnalysis: (state): BudgetData | undefined => 
      state.analysisData?.production_planning?.budget,
    
    characterAnalysis: (state): CharactersData | undefined => 
      state.analysisData?.script_breakdown?.characters,
    
    locationAnalysis: (state): LocationsData | undefined => 
      state.analysisData?.script_breakdown?.locations,
    
    propsAnalysis: (state): PropsAndWardrobeData | undefined => 
      state.analysisData?.script_breakdown?.props_and_wardrobe,
    
    sceneAnalysis: (state): Scene[] => 
      state.analysisData?.script_breakdown?.scenes || [],
    
    timelineAnalysis: (state): ScheduleData | undefined => 
      state.analysisData?.production_planning?.schedule,
    
    // Workflow status
    workflowStatus: (state): string => 
      state.analysisData?.workflow?.status || 'initializing',
    
    isWorkflowComplete: (state): boolean => 
      state.analysisData?.workflow?.status === 'completed',
    
    requiresReview: (state): boolean => 
      state.analysisData?.workflow?.requires_review || false,

    // New specific getters for UI components
    mainCharacters: (state): Character[] => 
      state.analysisData?.script_breakdown?.characters?.main || [],
    
    supportingCharacters: (state): Character[] => 
      state.analysisData?.script_breakdown?.characters?.supporting || [],
    
    characterInteractions: (state): CharacterInteraction[] => 
      state.analysisData?.script_breakdown?.characters?.interactions || [],
    
    interiorLocations: (state): LocationDetail[] => 
      state.analysisData?.script_breakdown?.locations?.interior || [],
    
    exteriorLocations: (state): LocationDetail[] => 
      state.analysisData?.script_breakdown?.locations?.exterior || [],
    
    shootingGroups: (state): ShootingGroup[] => 
      state.analysisData?.script_breakdown?.locations?.shooting_groups || [],
    
    propsByCategory: (state): Record<string, string[]> => 
      state.analysisData?.script_breakdown?.props_and_wardrobe?.props?.by_category || {},
    
    propsByScene: (state): SceneProps[] => 
      state.analysisData?.script_breakdown?.props_and_wardrobe?.props?.by_scene || [],
    
    wardrobeByCharacter: (state): Record<string, CharacterWardrobe> => 
      state.analysisData?.script_breakdown?.props_and_wardrobe?.wardrobe?.by_character || {},
    
    setDecorations: (state): SetDecoration[] => 
      state.analysisData?.script_breakdown?.props_and_wardrobe?.set_decoration || [],
    
    // Budget getters
    budgetCategory: (state): string => 
      state.analysisData?.production_planning?.budget?.overall_category || 'unknown',
    
    majorCostDrivers: (state): string[] => 
      state.analysisData?.production_planning?.budget?.major_cost_drivers || [],
    
    optimizationOpportunities: (state): string[] => 
      state.analysisData?.production_planning?.budget?.optimization_opportunities || [],
    
    sceneBudgets: (state): SceneBudget[] => 
      state.analysisData?.production_planning?.budget?.scene_breakdown || [],
    
    // Schedule getters
    totalShootDays: (state): number => 
      state.analysisData?.production_planning?.schedule?.total_shoot_days || 0,
    
    locationSchedules: (state): LocationSchedule[] => 
      state.analysisData?.production_planning?.schedule?.by_location || [],
    
    castSchedules: (state): Record<string, CastSchedule> => 
      state.analysisData?.production_planning?.schedule?.cast_schedule || {},
    
    // Crew getters
    coreCrew: (state): string[] => 
      state.analysisData?.production_planning?.crew_requirements?.core_crew || [],
    
    sceneCrews: (state): SceneCrew[] => 
      state.analysisData?.production_planning?.crew_requirements?.by_scene || [],
  },

  actions: {
    // Set uploaded file
    setUploadedFile(file: File) {
      this.uploadedFile = file;
      this.fileName = file.name;
      this.currentStep = 'upload';
      this.clearMessages();
    },

    // Enhanced analyze script from file upload
    async analyzeScriptFile(file: File) {
      this.isAnalyzing = true;
      this.currentStep = 'analyzing';
      this.clearMessages();
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('📤 Uploading file for analysis:', file.name);
        
        const response = await api.post<EnhancedApiResponse>(
          '/analyze-script-file',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Accept': 'application/json'
            }
          }
        );
        
        // Validate enhanced response structure
        if (!isEnhancedApiResponse(response.data)) {
          throw new Error('Invalid enhanced response format from server');
        }
        
        if (response.data.meta.success) {
          console.log('✅ File analysis successful');
          this.handleEnhancedAnalysisResponse(response.data);
        } else {
          throw new Error(response.data.error?.message || 'Analysis failed');
        }
      } catch (error) {
        this.handleError('Failed to analyze script file', error);
      } finally {
        this.isAnalyzing = false;
      }
    },

    // Enhanced analyze script from text content
    async analyzeScriptText(scriptContent: string) {
      this.isAnalyzing = true;
      this.currentStep = 'analyzing';
      this.clearMessages();
      
      try {
        console.log('📤 Sending script text for analysis');
        
        const response = await api.post<EnhancedApiResponse>(
          '/analyze-script',
          { script_content: scriptContent }
        );
        
        // Validate enhanced response structure
        if (!isEnhancedApiResponse(response.data)) {
          throw new Error('Invalid enhanced response format from server');
        }
        
        if (response.data.meta.success) {
          console.log('✅ Text analysis successful');
          this.handleEnhancedAnalysisResponse(response.data);
        } else {
          throw new Error(response.data.error?.message || 'Analysis failed');
        }
      } catch (error) {
        this.handleError('Failed to analyze script text', error);
      } finally {
        this.isAnalyzing = false;
      }
    },

    // Enhanced submit feedback
    async submitFeedback() {
      if (!this.threadId) {
        this.error = 'No active analysis session';
        return;
      }

      this.isSubmittingFeedback = true;
      this.clearMessages();
      
      try {
        const feedbackData: FeedbackData = {
          feedback: this.userFeedback,
          needs_revision: this.revisionsNeeded
        };
        
        console.log('📤 Submitting feedback:', feedbackData);

        const response = await api.post<EnhancedApiResponse>(
          '/submit-feedback',
          {
            thread_id: this.threadId,
            ...feedbackData
          }
        );
        
        // Validate enhanced response structure
        if (!isEnhancedApiResponse(response.data)) {
          throw new Error('Invalid enhanced response format from server');
        }
        
        if (response.data.meta.success) {
          console.log('✅ Feedback submission successful');
          this.handleEnhancedAnalysisResponse(response.data);
          this.successMessage = 'Feedback processed successfully';
          
          // Clear feedback if no more revisions needed
          if (!response.data.workflow.requires_review) {
            this.clearFeedback();
          }
        } else {
          throw new Error(response.data.error?.message || 'Feedback submission failed');
        }
      } catch (error) {
        this.handleError('Failed to submit feedback', error);
      } finally {
        this.isSubmittingFeedback = false;
      }
    },

    // Enhanced check workflow status
    async checkWorkflowStatus() {
      if (!this.threadId) return;
      
      try {
        console.log('📤 Checking workflow status for:', this.threadId);
        
        const response = await api.get<EnhancedApiResponse>(
          `/workflow-status/${this.threadId}`
        );
        
        if (!isEnhancedApiResponse(response.data)) {
          throw new Error('Invalid enhanced response format from server');
        }
        
        if (response.data.meta.success) {
          this.handleEnhancedAnalysisResponse(response.data);
          console.log('✅ Status check successful');
        } else {
          throw new Error(response.data.error?.message || 'Status check failed');
        }
      } catch (error) {
        console.error('Failed to check workflow status:', error);
      }
    },

    // Enhanced response handler
    handleEnhancedAnalysisResponse(response: EnhancedApiResponse) {
      console.log('📥 Handling enhanced analysis response:', response);
      
      // Validate script breakdown structure
      if (response.script_breakdown && !isValidScriptBreakdown(response.script_breakdown)) {
        console.warn('⚠️ Script breakdown structure may be invalid');
      }
      
      // Additional validation for nested structures
      if (response.script_breakdown?.characters && !isValidCharactersData(response.script_breakdown.characters)) {
        console.warn('⚠️ Characters data structure may be invalid');
      }
      
      if (response.script_breakdown?.locations && !isValidLocationsData(response.script_breakdown.locations)) {
        console.warn('⚠️ Locations data structure may be invalid');
      }
      
      if (response.script_breakdown?.props_and_wardrobe && !isValidPropsAndWardrobeData(response.script_breakdown.props_and_wardrobe)) {
        console.warn('⚠️ Props and wardrobe data structure may be invalid');
      }
      
      // Store the complete enhanced response
      this.analysisData = response;
      this.threadId = response.workflow.thread_id;
      this.needsHumanReview = response.workflow.requires_review;
      this.taskComplete = response.workflow.status === 'completed';
      
      // Update filename from source info
      if (response.source.filename) {
        this.fileName = response.source.filename;
      }
      
      // Update current step based on workflow status
      switch (response.workflow.status) {
        case 'completed':
          this.currentStep = 'complete';
          break;
        case 'reviewing':
          this.currentStep = 'review';
          break;
        case 'analyzing':
          this.currentStep = 'analyzing';
          break;
        default:
          if (this.needsHumanReview) {
            this.currentStep = 'review';
          }
      }
      
      // Update revisions needed from quality control
      if (response.quality_control?.human_review?.revisions_needed) {
        this.revisionsNeeded = { ...response.quality_control.human_review.revisions_needed };
      }
      
      this.successMessage = 'Analysis updated successfully';
      console.log('✅ Enhanced response handled successfully');
    },

    // Get specific scene data
    async getSceneData(sceneId: number) {
      if (!this.threadId) {
        this.error = 'No active analysis session';
        return null;
      }
      
      try {
        console.log(`📤 Fetching scene ${sceneId} data`);
        
        const response = await api.get<any>(
          `/scenes/${this.threadId}/${sceneId}`
        );
        
        if (response.data.meta?.success) {
          console.log(`✅ Scene ${sceneId} data retrieved`);
          return response.data;
        } else {
          throw new Error(response.data.error?.message || 'Failed to get scene data');
        }
      } catch (error) {
        this.handleError(`Failed to get scene ${sceneId} data`, error);
        return null;
      }
    },

    // Get department-specific data
    async getDepartmentData(department: string) {
      if (!this.threadId) {
        this.error = 'No active analysis session';
        return null;
      }
      
      try {
        console.log(`📤 Fetching ${department} department data`);
        
        const response = await api.get<any>(
          `/departments/${this.threadId}/${department}`
        );
        
        if (response.data.meta?.success) {
          console.log(`✅ ${department} department data retrieved`);
          return response.data;
        } else {
          throw new Error(response.data.error?.message || `Failed to get ${department} data`);
        }
      } catch (error) {
        this.handleError(`Failed to get ${department} department data`, error);
        return null;
      }
    },

    // Update user feedback for a specific section
    updateFeedback(section: string, feedback: string) {
      this.userFeedback[section] = feedback;
      console.log(`📝 Updated feedback for ${section}:`, feedback);
    },

    // Toggle revision needed for a section
    toggleRevision(section: string, needsRevision: boolean) {
      this.revisionsNeeded[section] = needsRevision;
      console.log(`🔄 Revision ${needsRevision ? 'requested' : 'cleared'} for ${section}`);
    },

    // Clear all feedback
    clearFeedback() {
      this.userFeedback = {};
      this.revisionsNeeded = {};
      console.log('🧹 Feedback cleared');
    },

    // Enhanced reset store
    resetStore() {
      console.log('🔄 Resetting store');
      this.analysisData = null;
      this.threadId = null;
      this.isAnalyzing = false;
      this.isSubmittingFeedback = false;
      this.needsHumanReview = false;
      this.taskComplete = false;
      this.uploadedFile = null;
      this.fileName = '';
      this.currentStep = 'upload';
      this.clearFeedback();
      this.clearMessages();
    },

    // Utility methods
    clearMessages() {
      this.error = null;
      this.successMessage = null;
    },

    handleError(message: string, error: any) {
      console.error('❌', message, error);
      
      let errorMessage = message;
      
      if (axios.isAxiosError(error)) {
        if (error.response?.data) {
          const errorData = error.response.data as any;
          // Handle enhanced error structure
          if (errorData.error?.message) {
            errorMessage = errorData.error.message;
          } else if (errorData.error?.details) {
            errorMessage = errorData.error.details;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      this.error = errorMessage;
      this.currentStep = 'upload';
    },

    // Enhanced export analysis data
    exportAnalysisData() {
      if (!this.analysisData) {
        console.warn('⚠️ No analysis data to export');
        return null;
      }
      
      try {
        const exportData = {
          fileName: this.fileName,
          threadId: this.threadId,
          analysisDate: new Date().toISOString(),
          version: this.analysisData.meta.version,
          data: this.analysisData
        };
        
        const jsonString = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonString], {
          type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `enhanced-script-analysis-${this.fileName || 'export'}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        
        console.log('✅ Enhanced analysis data exported successfully');
      } catch (error) {
        console.error('❌ Failed to export analysis data:', error);
        this.error = 'Failed to export analysis data';
      }
    },

    // Enhanced validation
    validateAnalysisData(): boolean {
      if (!this.analysisData) {
        console.warn('⚠️ No analysis data available');
        return false;
      }
      
      // Validate enhanced structure
      const requiredTopLevel = ['meta', 'workflow', 'script_breakdown', 'production_planning', 'quality_control'];
      
      for (const field of requiredTopLevel) {
        if (!(field in this.analysisData)) {
          console.warn(`⚠️ Missing required top-level field: ${field}`);
          return false;
        }
      }
      
      // Validate meta structure
      if (!this.analysisData.meta.success || !this.analysisData.meta.version) {
        console.warn('⚠️ Invalid meta structure');
        return false;
      }
      
      // Validate workflow structure
      if (!this.analysisData.workflow.thread_id || !this.analysisData.workflow.status) {
        console.warn('⚠️ Invalid workflow structure');
        return false;
      }
      
      // Validate script breakdown
      if (!isValidScriptBreakdown(this.analysisData.script_breakdown)) {
        console.warn('⚠️ Invalid script breakdown structure');
        return false;
      }
      
      console.log('✅ Enhanced analysis data validation passed');
      return true;
    },

    // Get analysis summary for display
    getAnalysisSummary(): AnalysisSummary | null {
      if (!this.analysisData) return null;
      
      const summary = this.analysisData.script_breakdown.summary;
      const workflow = this.analysisData.workflow;
      const source = this.analysisData.source;
      
      return {
        // Script info
        totalScenes: summary.total_scenes,
        totalCharacters: summary.total_characters,
        totalLocations: summary.total_locations,
        estimatedShootDays: summary.estimated_shoot_days,
        budgetCategory: summary.budget_category,
        
        // Source info
        language: source.language,
        totalPages: source.total_pages,
        fileType: source.file_type,
        
        // Workflow info
        status: workflow.status,
        progress: workflow.progress.percentage,
        requiresReview: workflow.requires_review,
        
        // Quality info
        dataComplete: this.analysisData.quality_control.validation.data_complete,
        jsonValid: this.analysisData.quality_control.validation.json_valid,
        errors: this.analysisData.quality_control.validation.analysis_errors
      };
    },

    // Enhanced helper methods with proper typing
    getScenesByLocation(locationName: string): Scene[] {
      if (!this.analysisData) return [];
      
      return this.analysisData.script_breakdown.scenes.filter(
        scene => scene.location.name === locationName
      );
    },

    getScenesByCharacter(characterName: string): Scene[] {
      if (!this.analysisData) return [];
      
      return this.analysisData.script_breakdown.scenes.filter(
        scene => scene.characters.includes(characterName)
      );
    },

    getScenesByComplexity(complexity: 'simple' | 'moderate' | 'complex'): Scene[] {
      if (!this.analysisData) return [];
      
      return this.analysisData.script_breakdown.scenes.filter(
        scene => scene.analysis.production.complexity === complexity
      );
    },

    getScenesByType(type: 'interior' | 'exterior'): Scene[] {
      if (!this.analysisData) return [];
      
      return this.analysisData.script_breakdown.scenes.filter(
        scene => scene.location.type === type
      );
    },

    getScenesByTimeOfDay(timeOfDay: 'day' | 'night' | 'dawn' | 'dusk'): Scene[] {
      if (!this.analysisData) return [];
      
      return this.analysisData.script_breakdown.scenes.filter(
        scene => scene.location.time_of_day === timeOfDay
      );
    },

    getBudgetByCategory(category: 'low' | 'medium' | 'high' | 'premium'): SceneBudget[] {
      if (!this.analysisData?.production_planning?.budget?.scene_breakdown) return [];
      
      return this.analysisData.production_planning.budget.scene_breakdown.filter(
        scene => scene.category === category
      );
    },

    getLocationsByType(type: 'interior' | 'exterior'): LocationDetail[] {
      if (!this.analysisData?.script_breakdown?.locations) return [];
      
      return type === 'interior' 
        ? this.analysisData.script_breakdown.locations.interior
        : this.analysisData.script_breakdown.locations.exterior;
    },

    getCharactersByRole(roleType: string): Character[] {
      if (!this.analysisData?.script_breakdown?.characters) return [];
      
      const allCharacters = [
        ...this.analysisData.script_breakdown.characters.main,
        ...this.analysisData.script_breakdown.characters.supporting
      ];
      
      return allCharacters.filter(char => char.role_type === roleType);
    },

    getPropsByCategory(category: string): string[] {
      if (!this.analysisData?.script_breakdown?.props_and_wardrobe?.props?.by_category) return [];
      
      return this.analysisData.script_breakdown.props_and_wardrobe.props.by_category[category] || [];
    },

    getCrewBySize(crewSize: 'minimal' | 'standard' | 'large'): SceneCrew[] {
      if (!this.analysisData?.production_planning?.crew_requirements?.by_scene) return [];
      
      return this.analysisData.production_planning.crew_requirements.by_scene.filter(
        crew => crew.crew_size === crewSize
      );
    },

    // New method for getting comprehensive scene data
    getSceneDetails(sceneId: number): Scene | undefined {
      if (!this.analysisData) return undefined;
      
      return this.analysisData.script_breakdown.scenes.find(
        scene => scene.id === sceneId
      );
    },

    // Method to get production summary
    getProductionSummary(): ProductionSummary | null {
      if (!this.analysisData) return null;
      
      const schedule = this.analysisData.production_planning.schedule;
      const budget = this.analysisData.production_planning.budget;
      const crew = this.analysisData.production_planning.crew_requirements;
      
      return {
        totalShootDays: schedule.total_shoot_days,
        budgetCategory: budget.overall_category,
        locationCount: schedule.by_location.length,
        castMembers: Object.keys(schedule.cast_schedule).length,
        coreCrew: crew.core_crew.length,
        majorCostDrivers: budget.major_cost_drivers,
        optimizationTips: budget.optimization_opportunities
      };
    },

    // Get character interaction summary
    getCharacterInteractionSummary(): { [key: string]: number } {
      if (!this.analysisData?.script_breakdown?.characters?.interactions) return {};
      
      const interactions = this.analysisData.script_breakdown.characters.interactions;
      const summary: { [key: string]: number } = {};
      
      interactions.forEach(interaction => {
        const key = interaction.characters.sort().join(' & ');
        summary[key] = (summary[key] || 0) + 1;
      });
      
      return summary;
    },

    // Get location utilization stats
    getLocationUtilization(): { [key: string]: { scenes: number; days: number } } {
      if (!this.analysisData) return {};
      
      const locations = this.analysisData.script_breakdown.locations;
      const utilization: { [key: string]: { scenes: number; days: number } } = {};
      
      // Process interior locations
      locations.interior.forEach(loc => {
        utilization[loc.name] = {
          scenes: loc.scenes.length,
          days: 0 // Will be calculated from shooting groups
        };
      });
      
      // Process exterior locations
      locations.exterior.forEach(loc => {
        utilization[loc.name] = {
          scenes: loc.scenes.length,
          days: 0 // Will be calculated from shooting groups
        };
      });
      
      // Add days from shooting groups
      locations.shooting_groups.forEach(group => {
        if (utilization[group.location]) {
          utilization[group.location].days = group.estimated_days;
        }
      });
      
      return utilization;
    },

    // Get budget distribution
    getBudgetDistribution(): { [key: string]: number } {
      if (!this.analysisData?.production_planning?.budget?.scene_breakdown) return {};
      
      const sceneBreakdown = this.analysisData.production_planning.budget.scene_breakdown;
      const distribution: { [key: string]: number } = {
        low: 0,
        medium: 0,
        high: 0,
        premium: 0
      };
      
      sceneBreakdown.forEach(scene => {
        distribution[scene.category] = (distribution[scene.category] || 0) + 1;
      });
      
      return distribution;
    },

    // Get crew requirements summary
    getCrewRequirementsSummary(): { [key: string]: number } {
      if (!this.analysisData?.production_planning?.crew_requirements?.by_scene) return {};
      
      const sceneCrews = this.analysisData.production_planning.crew_requirements.by_scene;
      const summary: { [key: string]: number } = {
        minimal: 0,
        standard: 0,
        large: 0
      };
      
      sceneCrews.forEach(crew => {
        summary[crew.crew_size] = (summary[crew.crew_size] || 0) + 1;
      });
      
      return summary;
    },

    // Get props complexity distribution
    getPropsComplexityDistribution(): { [key: string]: number } {
      if (!this.analysisData?.script_breakdown?.props_and_wardrobe?.props?.by_scene) return {};
      
      const sceneProps = this.analysisData.script_breakdown.props_and_wardrobe.props.by_scene;
      const distribution: { [key: string]: number } = {
        simple: 0,
        moderate: 0,
        complex: 0
      };
      
      sceneProps.forEach(prop => {
        distribution[prop.complexity] = (distribution[prop.complexity] || 0) + 1;
      });
      
      return distribution;
    },

    // Get scene statistics
    getSceneStatistics() {
      if (!this.analysisData) return null;
      
      const scenes = this.analysisData.script_breakdown.scenes;
      
      const stats = {
        totalScenes: scenes.length,
        averagePages: scenes.reduce((sum, scene) => sum + scene.content.estimated_pages, 0) / scenes.length,
        averageCharacters: scenes.reduce((sum, scene) => sum + scene.characters.length, 0) / scenes.length,
        averageProps: scenes.reduce((sum, scene) => sum + scene.props.length, 0) / scenes.length,
        complexityDistribution: {
          simple: 0,
          moderate: 0,
          complex: 0
        },
        typeDistribution: {
          interior: 0,
          exterior: 0
        },
        timeDistribution: {
          day: 0,
          night: 0,
          dawn: 0,
          dusk: 0
        }
      };
      
      scenes.forEach(scene => {
        stats.complexityDistribution[scene.analysis.production.complexity]++;
        stats.typeDistribution[scene.location.type]++;
        stats.timeDistribution[scene.location.time_of_day]++;
      });
      
      return stats;
    }
  }
});

// Export the configured API instance for use in other files
export { api };

// Export types for use in components
export type {
  EnhancedScriptAnalysisResponse,
  Scene,
  Character,
  LocationDetail,
  SceneProps,
  CharacterWardrobe,
  BudgetData,
  ScheduleData,
  CrewRequirements,
  ProductionSummary,
  AnalysisSummary
};
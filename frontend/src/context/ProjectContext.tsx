// src/context/ProjectContext.tsx

import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import type {
  Project,
  ProjectTable,
  Bucket,
  PromptTemplate,
  GenerationOutput
} from '../types/index';

// State Types
interface ProjectState {
  currentProject: Project | null;
  projects: Project[];
  projectTables: ProjectTable[];
  projectBuckets: Bucket[];
  projectPrompts: PromptTemplate[];
  recentOutputs: GenerationOutput[];
  isLoading: boolean;
  error: string | null;
}

// Action Types
type ProjectAction =
  | { type: 'SET_CURRENT_PROJECT'; payload: Project | null }
  | { type: 'SET_PROJECTS'; payload: Project[] }
  | { type: 'ADD_PROJECT'; payload: Project }
  | { type: 'UPDATE_PROJECT'; payload: Project }
  | { type: 'REMOVE_PROJECT'; payload: string }
  | { type: 'SET_PROJECT_TABLES'; payload: ProjectTable[] }
  | { type: 'SET_PROJECT_BUCKETS'; payload: Bucket[] }
  | { type: 'UPDATE_BUCKET'; payload: Bucket }
  | { type: 'SET_PROJECT_PROMPTS'; payload: PromptTemplate[] }
  | { type: 'ADD_PROMPT'; payload: PromptTemplate }
  | { type: 'UPDATE_PROMPT'; payload: PromptTemplate }
  | { type: 'SET_RECENT_OUTPUTS'; payload: GenerationOutput[] }
  | { type: 'ADD_OUTPUT'; payload: GenerationOutput }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_PROJECT_DATA' };

// Initial State
const initialState: ProjectState = {
  currentProject: null,
  projects: [],
  projectTables: [],
  projectBuckets: [],
  projectPrompts: [],
  recentOutputs: [],
  isLoading: false,
  error: null,
};

// Reducer
function projectReducer(state: ProjectState, action: ProjectAction): ProjectState {
  switch (action.type) {
    case 'SET_CURRENT_PROJECT':
      return { ...state, currentProject: action.payload };

    case 'SET_PROJECTS':
      return { ...state, projects: action.payload };

    case 'ADD_PROJECT':
      return {
        ...state,
        projects: [...state.projects, action.payload],
      };

    case 'UPDATE_PROJECT':
      return {
        ...state,
        projects: state.projects.map(p =>
          p.id === action.payload.id ? action.payload : p
        ),
        currentProject:
          state.currentProject?.id === action.payload.id
            ? action.payload
            : state.currentProject,
      };

    case 'REMOVE_PROJECT':
      return {
        ...state,
        projects: state.projects.filter(p => p.id !== action.payload),
        currentProject:
          state.currentProject?.id === action.payload
            ? null
            : state.currentProject,
      };

    case 'SET_PROJECT_TABLES':
      return { ...state, projectTables: action.payload };

    case 'SET_PROJECT_BUCKETS':
      return { ...state, projectBuckets: action.payload };

    case 'UPDATE_BUCKET':
      return {
        ...state,
        projectBuckets: state.projectBuckets.map(b =>
          b.id === action.payload.id ? action.payload : b
        ),
      };

    case 'SET_PROJECT_PROMPTS':
      return { ...state, projectPrompts: action.payload };

    case 'ADD_PROMPT':
      return {
        ...state,
        projectPrompts: [...state.projectPrompts, action.payload],
      };

    case 'UPDATE_PROMPT':
      return {
        ...state,
        projectPrompts: state.projectPrompts.map(p =>
          p.id === action.payload.id ? action.payload : p
        ),
      };

    case 'SET_RECENT_OUTPUTS':
      return { ...state, recentOutputs: action.payload };

    case 'ADD_OUTPUT':
      return {
        ...state,
        recentOutputs: [action.payload, ...state.recentOutputs].slice(0, 50), // Keep last 50
      };

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload };

    case 'CLEAR_PROJECT_DATA':
      return {
        ...state,
        currentProject: null,
        projectTables: [],
        projectBuckets: [],
        projectPrompts: [],
        recentOutputs: [],
      };

    default:
      return state;
  }
}

// Context Types
interface ProjectContextType {
  state: ProjectState;
  dispatch: React.Dispatch<ProjectAction>;
  // Helper functions
  selectProject: (project: Project) => void;
  clearCurrentProject: () => void;
  isProjectSelected: () => boolean;
  getCurrentProjectId: () => string | null;
}

// Create Context
const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

// Provider Component
interface ProjectProviderProps {
  children: ReactNode;
}

export function ProjectProvider({ children }: ProjectProviderProps) {
  const [state, dispatch] = useReducer(projectReducer, initialState);

  // Helper functions
  const selectProject = (project: Project) => {
    dispatch({ type: 'SET_CURRENT_PROJECT', payload: project });

    // Store in localStorage for persistence
    try {
      localStorage.setItem('nell_current_project_id', project.id);
    } catch (error) {
      console.warn('Could not save current project to localStorage:', error);
    }
  };

  const clearCurrentProject = () => {
    dispatch({ type: 'CLEAR_PROJECT_DATA' });

    // Remove from localStorage
    try {
      localStorage.removeItem('nell_current_project_id');
    } catch (error) {
      console.warn('Could not remove current project from localStorage:', error);
    }
  };

  const isProjectSelected = () => {
    return state.currentProject !== null;
  };

  const getCurrentProjectId = () => {
    return state.currentProject?.id || null;
  };

  // Load current project from localStorage on mount
  useEffect(() => {
    try {
      const savedProjectId = localStorage.getItem('nell_current_project_id');
      if (savedProjectId && state.projects.length > 0) {
        const savedProject = state.projects.find(p => p.id === savedProjectId);
        if (savedProject) {
          dispatch({ type: 'SET_CURRENT_PROJECT', payload: savedProject });
        }
      }
    } catch (error) {
      console.warn('Could not load current project from localStorage:', error);
    }
  }, [state.projects]);

  const value: ProjectContextType = {
    state,
    dispatch,
    selectProject,
    clearCurrentProject,
    isProjectSelected,
    getCurrentProjectId,
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
}

// Custom Hook
export function useProject() {
  const context = useContext(ProjectContext);
  if (context === undefined) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
}

// Convenience hooks
export function useCurrentProject() {
  const { state } = useProject();
  return state.currentProject;
}

export function useProjectData() {
  const { state } = useProject();
  return {
    currentProject: state.currentProject,
    tables: state.projectTables,
    buckets: state.projectBuckets,
    prompts: state.projectPrompts,
    outputs: state.recentOutputs,
  };
}


// src/hooks/useProjects.ts
// Simplified version to avoid import errors

import { useState, useEffect } from 'react';
import type { Project } from '../types';

// Mock project data for now
const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Romantic Comedy Script',
    description: 'A lighthearted romance set in modern NYC',
    status: 'active',
    createdAt: new Date('2025-06-01'),
    updatedAt: new Date('2025-06-02'),
    dbPath: './projects/1/project.db',
    lightragPath: './projects/1/lightrag_working_dir',
    tables: ['characters', 'scenes'],
    bucketCount: 3
  },
  {
    id: '2',
    name: 'Amazon BRD Template',
    description: 'Business requirements document templates',
    status: 'active',
    createdAt: new Date('2025-05-30'),
    updatedAt: new Date('2025-06-01'),
    dbPath: './projects/2/project.db',
    lightragPath: './projects/2/lightrag_working_dir',
    tables: ['requirements', 'stakeholders'],
    bucketCount: 2
  }
];

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>(mockProjects);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock API calls
  const fetchProjects = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      setProjects(mockProjects);
      setError(null);
    } catch (err) {
      setError('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (projectData: any) => {
    setLoading(true);
    try {
      // Simulate API call
      const newProject: Project = {
        id: Date.now().toString(),
        name: projectData.name,
        description: projectData.description,
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date(),
        dbPath: `./projects/${Date.now()}/project.db`,
        lightragPath: `./projects/${Date.now()}/lightrag_working_dir`,
        tables: [],
        bucketCount: 0
      };

      setProjects(prev => [...prev, newProject]);
      setCurrentProject(newProject);
      setError(null);

      return newProject;
    } catch (err) {
      setError('Failed to create project');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const selectProject = (project: Project) => {
    setCurrentProject(project);
  };

  const selectProjectById = (id: string) => {
    const project = projects.find(p => p.id === id);
    if (project) {
      setCurrentProject(project);
    }
  };

  const clearCurrentProject = () => {
    setCurrentProject(null);
  };

  const getProjectById = (id: string) => {
    return projects.find(p => p.id === id) || null;
  };

  const isProjectSelected = (id: string) => {
    return currentProject?.id === id;
  };

  const getRecentProjects = (limit: number = 5) => {
    return projects
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
      .slice(0, limit);
  };

  // Load projects on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  return {
    // State
    projects,
    currentProject,

    // Loading states
    loading,
    loadingProjects: loading,
    creatingProject: loading,
    updatingProject: false,
    deletingProject: false,

    // Errors
    error,

    // Actions
    fetchProjects,
    createProject,
    updateProject: () => Promise.resolve(),
    deleteProject: () => Promise.resolve(),
    selectProject,
    selectProjectById,
    switchProject: selectProject,
    clearCurrentProject,

    // Helpers
    getProjectById,
    isProjectSelected,
    getRecentProjects,
  };
}

// Simplified project data hook
export function useProjectData() {
  const [loading, setLoading] = useState(false);

  // Mock data
  const mockData = {
    tables: ['characters', 'scenes', 'plot_points'],
    buckets: [
      { id: '1', name: 'books', active: true, docCount: 23 },
      { id: '2', name: 'scripts', active: true, docCount: 15 },
      { id: '3', name: 'plays', active: false, docCount: 8 }
    ],
    prompts: ['cheesy-romcom', 'romantic-dramedy', 'neutral'],
    outputs: []
  };

  const loadProjectData = async () => {
    setLoading(true);
    // Simulate loading
    await new Promise(resolve => setTimeout(resolve, 300));
    setLoading(false);
  };

  return {
    // Data
    tables: mockData.tables,
    buckets: mockData.buckets,
    prompts: mockData.prompts,
    outputs: mockData.outputs,

    // Loading states
    loading,
    loadingTables: false,
    loadingBuckets: false,
    loadingPrompts: false,
    loadingOutputs: false,

    // Actions
    loadProjectData,
    refreshTables: () => Promise.resolve(),
    refreshBuckets: () => Promise.resolve(),
    refreshPrompts: () => Promise.resolve(),
    refreshOutputs: () => Promise.resolve(),
  };
}


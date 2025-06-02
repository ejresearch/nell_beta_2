// src/layouts/Layout.tsx

import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Settings,
  Folder,
  FileText,
  Brain,
  Pencil,
  BookOpen,
  MessageSquare
} from 'lucide-react';
import { useCurrentProject } from '../context/ProjectContext';
import { useAppState } from '../context/AppContext';
import Miranda from '../components/Miranda';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const currentProject = useCurrentProject();
  const appState = useAppState();

  const navItems = [
    { path: '/', label: 'Home', icon: <Home size={18} /> },
    { path: '/setup', label: 'Setup', icon: <Settings size={18} /> },
    { path: '/project', label: 'Project', icon: <Folder size={18} /> },
    { path: '/editor', label: 'Editor', icon: <FileText size={18} /> },
    { path: '/brainstorm', label: 'Brainstorm', icon: <Brain size={18} /> },
    { path: '/write', label: 'Write', icon: <Pencil size={18} /> },
    { path: '/outputs', label: 'Outputs', icon: <BookOpen size={18} /> },
    { path: '/chat', label: 'Chat', icon: <MessageSquare size={18} /> },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white">
      {/* Sidebar */}
      <aside className="w-60 bg-gray-100 p-4 border-r flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-bold">Nell</h2>
          <p className="text-xs text-gray-500 mt-1">AI Writing Platform</p>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-2 text-sm flex-1">
          {navItems.map(({ path, label, icon }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-200 transition-colors ${
                location.pathname === path ? 'bg-blue-100 font-medium text-blue-700' : 'text-gray-700'
              }`}
            >
              {icon}
              {label}
            </Link>
          ))}
        </nav>

        {/* App Status */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={appState.isOnline ? 'text-green-600' : 'text-red-600'}>
                {appState.isOnline ? '🟢 Online' : '🔴 Offline'}
              </span>
            </div>
            {appState.isLoading && (
              <div className="flex justify-between">
                <span>Loading:</span>
                <span className="text-blue-600">⏳ Active</span>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col">
        {/* Topbar */}
        <header className="h-16 border-b flex items-center px-6 bg-white shadow-sm">
          <div className="flex items-center gap-4">
            <span className="font-medium">
              🧠 Project: 
              {currentProject ? (
                <span className="text-blue-600 ml-1">{currentProject.name}</span>
              ) : (
                <span className="text-gray-500 ml-1">No project selected</span>
              )}
            </span>
            
            {currentProject && (
              <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                {currentProject.type.replace('_', ' ')}
              </span>
            )}
          </div>

          {/* Global loading indicator */}
          {appState.isLoading && (
            <div className="ml-auto flex items-center gap-2 text-blue-600 text-sm">
              <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
              Loading...
            </div>
          )}
        </header>

        {/* Page content */}
        <section className="p-6 overflow-y-auto flex-1 bg-white">
          {children}
        </section>
      </main>

      {/* Miranda Assistant */}
      <Miranda />
    </div>
  );
}

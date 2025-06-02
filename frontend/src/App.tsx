// src/App.tsx

import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Link,
  useLocation
} from 'react-router-dom';
import {
  Menu,
  X,
  Home,
  Settings,
  FolderOpen,
  Lightbulb,
  PenTool,
  MessageSquare,
  Database,
  FileText
} from 'lucide-react';

// Import your pages
import LandingPage from './pages/LandingPage';
import EnvironmentSetupPage from './pages/EnvironmentSetupPage';
import ProjectSelectorPage from './pages/ProjectSelectorPage';
import ProjectEditorPage from './pages/ProjectEditorPage';
import BrainstormPage from './pages/BrainstormPage';
import WritePage from './pages/WritePage';
import OutputLogPage from './pages/OutputLogPage';
import ChatPage from './pages/ChatPage';

// Import components
import Miranda from './components/Miranda';

// Import context providers (with type-only imports fixed)
import { AppProvider } from './context/AppContext';
import { ProjectProvider } from './context/ProjectContext';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

function NavigationSidebar({
  sidebarOpen,
  setSidebarOpen
}: {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}) {
  const location = useLocation();

  // Define your navigation menu items
  const navigation: NavigationItem[] = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Setup', href: '/setup', icon: Settings },
    { name: 'Projects', href: '/projects', icon: FolderOpen },
    { name: 'Editor', href: '/editor', icon: Database },
    { name: 'Brainstorm', href: '/brainstorm', icon: Lightbulb },
    { name: 'Write', href: '/write', icon: PenTool },
    { name: 'Outputs', href: '/outputs', icon: FileText },
    { name: 'Chat', href: '/chat', icon: MessageSquare }
  ];

  return (
    <div
      className={`
        ${sidebarOpen ? 'w-64' : 'w-16'} 
        bg-white shadow-sm border-r border-gray-200 
        transition-all duration-300 flex flex-col
      `}
    >
      {/* Logo / Branding */}
      <div className="h-16 flex items-center px-4 border-b border-gray-200">
        {sidebarOpen ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">N</span>
            </div>
            <span className="text-xl font-bold text-gray-900">Nell Beta 2</span>
          </div>
        ) : (
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center mx-auto">
            <span className="text-white font-bold text-sm">N</span>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map(item => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-lg transition-colors
                ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              <item.icon className="w-5 h-5" />
              {sidebarOpen && <span className="font-medium">{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Sidebar Toggle Button */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="w-full flex items-center justify-center p-2 text-gray-500 hover:text-gray-700 transition-colors"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>
    </div>
  );
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mirandaVisible, setMirandaVisible] = useState(false);

  return (
    <AppProvider>
      <ProjectProvider>
        <Router>
          <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <NavigationSidebar
              sidebarOpen={sidebarOpen}
              setSidebarOpen={setSidebarOpen}
            />

            {/* Main Content Wrapper */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Top Bar */}
              <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
                <h1 className="text-lg font-semibold text-gray-900">
                  AI Writing Platform
                </h1>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setMirandaVisible(prev => !prev)}
                    className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
                    title="Toggle Miranda Assistant"
                  >
                    <MessageSquare className="w-5 h-5" />
                  </button>
                  <div className="w-8 h-8 bg-gray-300 rounded-full" />
                </div>
              </header>

              {/* Page Content */}
              <main className="flex-1 overflow-auto">
                <Routes>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/setup" element={<EnvironmentSetupPage />} />
                  <Route path="/projects" element={<ProjectSelectorPage />} />
                  <Route path="/editor" element={<ProjectEditorPage />} />
                  <Route path="/brainstorm" element={<BrainstormPage />} />
                  <Route path="/write" element={<WritePage />} />
                  <Route path="/outputs" element={<OutputLogPage />} />
                  <Route path="/chat" element={<ChatPage />} />
                  {/* Catch‐all route redirects to Home */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </main>
            </div>

            {/* Miranda Assistant Panel */}
            <Miranda
              isVisible={mirandaVisible}
              onToggle={() => setMirandaVisible(prev => !prev)}
            />
          </div>
        </Router>
      </ProjectProvider>
    </AppProvider>
  );
}

export default App;


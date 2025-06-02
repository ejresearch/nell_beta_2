// src/router/App.tsx

import { Routes, Route } from 'react-router-dom';
import Layout from '../layouts/Layout';
import LandingPage from '../pages/LandingPage';
import EnvironmentSetupPage from '../pages/EnvironmentSetupPage';
import ProjectSelectorPage from '../pages/ProjectSelectorPage';
import ProjectEditorPage from '../pages/ProjectEditorPage';
import BrainstormPage from '../pages/BrainstormPage';
import WritePage from '../pages/WritePage';
import OutputLogPage from '../pages/OutputLogPage';
import ChatPage from '../pages/ChatPage';
import ApiTest from '../components/ApiTest'; // Our test component

export default function App() {
  return (
    <Routes>
      {/* Landing page - no layout */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Test route - temporary for development */}
      <Route path="/test" element={<ApiTest />} />
      
      {/* All other routes use the Layout */}
      <Route
        path="/*"
        element={
          <Layout>
            <Routes>
              <Route path="setup" element={<EnvironmentSetupPage />} />
              <Route path="project" element={<ProjectSelectorPage />} />
              <Route path="editor" element={<ProjectEditorPage />} />
              <Route path="brainstorm" element={<BrainstormPage />} />
              <Route path="write" element={<WritePage />} />
              <Route path="outputs" element={<OutputLogPage />} />
              <Route path="chat" element={<ChatPage />} />
            </Routes>
          </Layout>
        }
      />
    </Routes>
  );
}

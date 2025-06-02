// src/pages/LandingPage.tsx

import React from 'react';
import { Link } from 'react-router-dom'; 

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      {/* Centered status card */}
      <div className="flex-1 flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            🎉 Nell Beta 2 is Working! 🎉
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Your frontend is now successfully running! We've bypassed all the import errors.
          </p>
          <div className="bg-white p-8 rounded-lg shadow-sm border max-w-2xl mx-auto">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Next Steps:</h2>
            <ul className="text-left space-y-3 text-gray-700">
              <li>✅ <strong>Frontend:</strong> React app running successfully</li>
              <li>✅ <strong>Backend:</strong> FastAPI + LightRAG ready</li>
              <li>⏭️ <strong>Next:</strong> Add navigation and connect to APIs</li>
            </ul>
          </div>
          <div className="mt-8">
            <p className="text-sm text-gray-500">
              AI Writing Platform • Modular Workflows • LightRAG Integration
            </p>
          </div>
        </div>
      </div>

      {/* Navigation links at the bottom of the page */}
      <div className="bg-white border-t border-gray-200 py-6">
        <nav className="max-w-4xl mx-auto flex flex-wrap justify-center gap-6 px-6">
          <Link
            to="/"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">🏠</span>
            <span className="mt-1">Home</span>
          </Link>
          <Link
            to="/setup"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">⚙️</span>
            <span className="mt-1">Setup</span>
          </Link>
          <Link
            to="/projects"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">📁</span>
            <span className="mt-1">Projects</span>
          </Link>
          <Link
            to="/editor"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">🖥️</span>
            <span className="mt-1">Editor</span>
          </Link>
          <Link
            to="/brainstorm"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">💡</span>
            <span className="mt-1">Brainstorm</span>
          </Link>
          <Link
            to="/write"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">✍️</span>
            <span className="mt-1">Write</span>
          </Link>
          <Link
            to="/outputs"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">📄</span>
            <span className="mt-1">Outputs</span>
          </Link>
          <Link
            to="/chat"
            className="flex flex-col items-center text-gray-700 hover:text-blue-600 transition-colors"
          >
            <span className="text-2xl">💬</span>
            <span className="mt-1">Chat</span>
          </Link>
        </nav>
      </div>
    </div>
  );
}


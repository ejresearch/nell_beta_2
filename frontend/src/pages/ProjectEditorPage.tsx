import React, { useState } from 'react';

export default function ProjectEditorPage() {
  const [tables] = useState([
    { name: 'characters', rows: 5, columns: ['name', 'age', 'background', 'motivation'] },
    { name: 'scenes', rows: 12, columns: ['scene_number', 'location', 'description', 'emotional_arc'] },
    { name: 'plot_points', rows: 8, columns: ['act', 'event', 'impact', 'resolution'] }
  ]);

  const [selectedTable, setSelectedTable] = useState('characters');
  const [showCreateTable, setShowCreateTable] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Project Editor</h1>
          <p className="text-gray-600 mt-1">Manage your project tables and data</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar - Table List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Tables</h2>
                <button
                  onClick={() => setShowCreateTable(true)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  + Add
                </button>
              </div>
              
              <div className="space-y-2">
                {tables.map((table) => (
                  <button
                    key={table.name}
                    onClick={() => setSelectedTable(table.name)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedTable === table.name
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{table.name}</div>
                    <div className="text-sm text-gray-500">{table.rows} rows</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content - Table Editor */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Table Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 capitalize">
                      {selectedTable}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {tables.find(t => t.name === selectedTable)?.columns.length} columns, {tables.find(t => t.name === selectedTable)?.rows} rows
                    </p>
                  </div>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    Add Row
                  </button>
                </div>
              </div>

              {/* Table Content */}
              <div className="p-6">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-medium text-gray-900">ID</th>
                        {tables.find(t => t.name === selectedTable)?.columns.map((col) => (
                          <th key={col} className="text-left py-3 px-4 font-medium text-gray-900 capitalize">
                            {col.replace('_', ' ')}
                          </th>
                        ))}
                        <th className="text-right py-3 px-4 font-medium text-gray-900">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[1, 2, 3].map((row) => (
                        <tr key={row} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4 text-gray-600">{row}</td>
                          {tables.find(t => t.name === selectedTable)?.columns.map((col) => (
                            <td key={col} className="py-3 px-4">
                              <input
                                type="text"
                                placeholder={`Enter ${col.replace('_', ' ')}`}
                                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500 focus:border-transparent"
                              />
                            </td>
                          ))}
                          <td className="py-3 px-4 text-right">
                            <button className="text-red-600 hover:text-red-700 text-sm">
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create Table Modal */}
      {showCreateTable && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Table</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Table Name
                </label>
                <input
                  type="text"
                  placeholder="e.g., characters, scenes, notes"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Columns (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g., name, age, description"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowCreateTable(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2 px-4 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors">
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState } from 'react';

interface OutputEntry {
  id: string;
  type: 'brainstorm' | 'write' | 'edit';
  version: number;
  content: string;
  preview: string;
  wordCount?: number;
  createdAt: string;
  sourceTable: string;
  sourceRows: number[];
  bucketsUsed?: string[];
  tone: string;
}

export default function OutputLogPage() {
  const [filter, setFilter] = useState<'all' | 'brainstorm' | 'write' | 'edit'>('all');
  const [selectedEntry, setSelectedEntry] = useState<OutputEntry | null>(null);

  const outputs: OutputEntry[] = [
    {
      id: 'write_v3',
      type: 'write',
      version: 3,
      content: 'CHAPTER 1: THE BOOKSTORE ENCOUNTER\n\nThe morning sun streamed through the tall windows of "Between the Lines," casting golden rectangles across the hardwood floors...',
      preview: 'Chapter 1 opening scene with Emma and James meeting at the bookstore',
      wordCount: 487,
      createdAt: '2025-06-02 12:15:00',
      sourceTable: 'characters',
      sourceRows: [1, 2],
      tone: 'cheesy-romcom'
    },
    {
      id: 'brainstorm_v3',
      type: 'brainstorm',
      version: 3,
      content: 'BRAINSTORM SESSION - Version 3\nGenerated from: characters (rows: 1, 2)\nUsing buckets: books, scripts\n\nBased on your character profiles and the romantic comedy conventions...',
      preview: 'Character dynamics and plot development ideas for romantic comedy',
      createdAt: '2025-06-02 11:45:00',
      sourceTable: 'characters',
      sourceRows: [1, 2],
      bucketsUsed: ['books', 'scripts'],
      tone: 'cheesy-romcom'
    },
    {
      id: 'write_v2',
      type: 'write',
      version: 2,
      content: 'CHAPTER 1: FIRST DRAFT\n\nEmma walked into the bookstore, not knowing that her life was about to change forever...',
      preview: 'Earlier version of Chapter 1 opening',
      wordCount: 324,
      createdAt: '2025-06-02 10:30:00',
      sourceTable: 'characters',
      sourceRows: [1, 2],
      tone: 'romantic-dramedy'
    },
    {
      id: 'brainstorm_v2',
      type: 'brainstorm',
      version: 2,
      content: 'Initial character development session focusing on Emma and James backstories...',
      preview: 'Character backstory exploration and motivation analysis',
      createdAt: '2025-06-02 09:15:00',
      sourceTable: 'characters',
      sourceRows: [1, 2],
      bucketsUsed: ['books', 'plays'],
      tone: 'neutral'
    }
  ];

  const filteredOutputs = filter === 'all' ? outputs : outputs.filter(output => output.type === filter);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'brainstorm': return 'bg-blue-100 text-blue-800';
      case 'write': return 'bg-green-100 text-green-800';
      case 'edit': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'brainstorm':
        return <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />;
      case 'write':
        return <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />;
      case 'edit':
        return <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />;
      default:
        return <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Output History</h1>
          <p className="text-gray-600 mt-1">View and manage all generated content</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Filter Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Filter Outputs</h3>
              
              <div className="space-y-2">
                {[
                  { key: 'all', label: 'All Outputs', count: outputs.length },
                  { key: 'brainstorm', label: 'Brainstorm', count: outputs.filter(o => o.type === 'brainstorm').length },
                  { key: 'write', label: 'Write', count: outputs.filter(o => o.type === 'write').length },
                  { key: 'edit', label: 'Edit', count: outputs.filter(o => o.type === 'edit').length }
                ].map((filterOption) => (
                  <button
                    key={filterOption.key}
                    onClick={() => setFilter(filterOption.key as any)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      filter === filterOption.key
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{filterOption.label}</span>
                      <span className="text-sm text-gray-500">{filterOption.count}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Export Options */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Export</h3>
              
              <div className="space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                  Export All as PDF
                </button>
                <button className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors">
                  Export Selected
                </button>
              </div>
            </div>
          </div>

          {/* Output List */}
          <div className="lg:col-span-2">
            <div className="space-y-4">
              {filteredOutputs.length === 0 ? (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-500">No outputs found for this filter</p>
                </div>
              ) : (
                filteredOutputs.map((output) => (
                  <div
                    key={output.id}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setSelectedEntry(output)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(output.type)}`}>
                          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {getTypeIcon(output.type)}
                          </svg>
                          {output.type} v{output.version}
                        </div>
                        {output.wordCount && (
                          <span className="text-sm text-gray-500">{output.wordCount} words</span>
                        )}
                      </div>
                      <span className="text-sm text-gray-500">{output.createdAt}</span>
                    </div>

                    <h4 className="text-lg font-medium text-gray-900 mb-2">{output.preview}</h4>
                    
                    <div className="text-sm text-gray-600 mb-3">
                      <div className="flex flex-wrap gap-4">
                        <span>Table: <strong>{output.sourceTable}</strong></span>
                        <span>Rows: <strong>{output.sourceRows.join(', ')}</strong></span>
                        <span>Tone: <strong>{output.tone}</strong></span>
                        {output.bucketsUsed && (
                          <span>Buckets: <strong>{output.bucketsUsed.join(', ')}</strong></span>
                        )}
                      </div>
                    </div>

                    <div className="text-gray-700 text-sm line-clamp-2">
                      {output.content.substring(0, 150)}...
                    </div>

                    <div className="flex justify-end mt-4 gap-2">
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        View Full
                      </button>
                      <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                        Export
                      </button>
                      <button className="text-gray-600 hover:text-gray-700 text-sm font-medium">
                        Copy
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Full Content Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {selectedEntry.type} v{selectedEntry.version}
                </h2>
                <p className="text-gray-600">{selectedEntry.preview}</p>
              </div>
              <button
                onClick={() => setSelectedEntry(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-gray-700 font-serif leading-relaxed">
                  {selectedEntry.content}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

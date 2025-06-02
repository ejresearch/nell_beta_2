import React, { useState, useEffect } from 'react';

interface ApiEndpoint {
  name: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  url: string;
  description: string;
  testData?: any;
}

export default function ApiTest() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('health');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = 'http://localhost:8000';

  const endpoints: ApiEndpoint[] = [
    {
      name: 'health',
      method: 'GET',
      url: '/health',
      description: 'API health check'
    },
    {
      name: 'list-projects',
      method: 'GET', 
      url: '/api/v1/projects',
      description: 'List all projects'
    },
    {
      name: 'create-project',
      method: 'POST',
      url: '/api/v1/projects',
      description: 'Create new project',
      testData: {
        name: 'Test Project',
        description: 'A test project for API validation',
        tables: [
          { 'characters': ['name', 'age', 'background'] },
          { 'scenes': ['location', 'description'] }
        ]
      }
    },
    {
      name: 'tone-presets',
      method: 'GET',
      url: '/api/v1/tone-presets',
      description: 'Get available tone presets'
    },
    {
      name: 'project-tables',
      method: 'GET',
      url: '/api/v1/projects/test-id/tables',
      description: 'List project tables'
    },
    {
      name: 'project-buckets',
      method: 'GET',
      url: '/api/v1/projects/test-id/buckets',
      description: 'List project buckets'
    }
  ];

  const testEndpoint = async (endpoint: ApiEndpoint) => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const options: RequestInit = {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
        },
      };

      if (endpoint.testData) {
        options.body = JSON.stringify(endpoint.testData);
      }

      const response = await fetch(`${API_BASE}${endpoint.url}`, options);
      const data = await response.json();
      
      setResponse({
        status: response.status,
        statusText: response.statusText,
        data: data
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Test health endpoint on component mount
    const healthEndpoint = endpoints.find(e => e.name === 'health');
    if (healthEndpoint) {
      testEndpoint(healthEndpoint);
    }
  }, []);

  const selectedEndpointData = endpoints.find(e => e.name === selectedEndpoint);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">API Testing Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Endpoint Selection */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Endpoint</h2>
            
            <div className="space-y-3">
              {endpoints.map((endpoint) => (
                <button
                  key={endpoint.name}
                  onClick={() => setSelectedEndpoint(endpoint.name)}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${
                    selectedEndpoint === endpoint.name
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">{endpoint.name}</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
                      endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800' :
                      endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {endpoint.method}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-1">{endpoint.url}</div>
                  <div className="text-sm text-gray-500">{endpoint.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Test Controls */}
          {selectedEndpointData && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Test Endpoint</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL
                  </label>
                  <div className="bg-gray-100 p-3 rounded text-sm font-mono">
                    {selectedEndpointData.method} {API_BASE}{selectedEndpointData.url}
                  </div>
                </div>

                {selectedEndpointData.testData && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Request Body
                    </label>
                    <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                      {JSON.stringify(selectedEndpointData.testData, null, 2)}
                    </pre>
                  </div>
                )}

                <button
                  onClick={() => testEndpoint(selectedEndpointData)}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors"
                >
                  {loading ? 'Testing...' : 'Test Endpoint'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Response Display */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Response</h2>
            
            {loading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Testing endpoint...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="text-red-400">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <div className="mt-2 text-sm text-red-700">{error}</div>
                  </div>
                </div>
              </div>
            )}

            {response && !loading && (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 text-sm font-medium rounded ${
                    response.status >= 200 && response.status < 300
                      ? 'bg-green-100 text-green-800'
                      : response.status >= 400
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {response.status} {response.statusText}
                  </span>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Response Data
                  </label>
                  <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto max-h-96">
                    {JSON.stringify(response.data, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {!response && !loading && !error && (
              <div className="text-center py-8 text-gray-500">
                <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                </svg>
                <p>Select an endpoint and click "Test Endpoint" to see the response</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

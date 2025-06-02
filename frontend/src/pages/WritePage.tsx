import React, { useState } from 'react';

export default function WritePage() {
  const [selectedBrainstorm, setSelectedBrainstorm] = useState('latest');
  const [selectedTable, setSelectedTable] = useState('characters');
  const [selectedRows, setSelectedRows] = useState<number[]>([1, 2]);
  const [tone, setTone] = useState('cheesy-romcom');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  const [wordCount, setWordCount] = useState(0);

  const brainstormSessions = [
    { id: 'latest', version: 3, created: '2025-06-02 12:00', preview: 'Character dynamics and plot development...' },
    { id: 'v2', version: 2, created: '2025-06-02 10:30', preview: 'Initial character concepts and setting...' },
    { id: 'v1', version: 1, created: '2025-06-01 16:45', preview: 'Basic story outline and themes...' }
  ];

  const tables = ['characters', 'scenes', 'plot_points'];
  const tones = [
    'neutral', 'cheesy-romcom', 'romantic-dramedy', 
    'shakespearean-romance', 'professional', 'academic'
  ];

  const handleGenerate = async () => {
    setIsGenerating(true);
    
    // Mock generation delay
    setTimeout(() => {
      const content = `
CHAPTER 1: THE BOOKSTORE ENCOUNTER

The morning sun streamed through the tall windows of "Between the Lines," casting golden rectangles across the hardwood floors. Emma Rodriguez pushed through the heavy glass door, the familiar scent of aged paper and fresh coffee wrapping around her like a warm embrace. She was already running late for her shift, but she couldn't resist pausing to admire the new display of first-edition classics that Mr. Chen had arranged near the entrance.

"You're staring at those books like they hold the secrets of the universe," came a voice from behind her, tinged with amusement and just a hint of pretension.

Emma turned to find herself face-to-face with someone she'd never seen before – tall, dark-haired, with the kind of effortlessly disheveled look that suggested either he'd just rolled out of bed or spent considerable time crafting the appearance of having just rolled out of bed. He was holding a worn copy of "Pride and Prejudice" and wearing an expression that somehow managed to be both condescending and charming.

"Maybe they do," Emma replied, crossing her arms. "Though I'm guessing you're more of a 'judge books by their covers' type."

His eyebrows shot up, clearly not expecting pushback. "Actually, I prefer to judge them by their substance. Like this one." He held up the Austen novel. "Overrated romantic drivel disguised as social commentary."

Emma felt her jaw drop. In the three years she'd worked at the bookstore, she'd encountered many opinions about literature, but dismissing Jane Austen as "drivel" was fighting words.

"Overrated?" she said, her voice rising slightly. "Austen practically invented the modern novel structure. Her social commentary was revolutionary for its time, and her wit is still unmatched. If you can't see that, maybe you should stick to comic books."

The stranger's grin widened, as if he'd been hoping for exactly this reaction. "Comic books can be quite sophisticated, actually. But I appreciate passion in defense of literature, even when it's misguided."

"Misguided?" Emma stepped closer, close enough to see flecks of gold in his brown eyes. "Let me guess – you're one of those people who thinks only brooding male authors writing about war and whiskey constitute 'real' literature."

"Absolutely not," he said, his voice softening slightly. "I happen to think Virginia Woolf wrote circles around Hemingway. I just think Austen gets credit for being progressive when she was really just writing wish-fulfillment fantasies for upper-class women."

Emma opened her mouth to deliver what she was sure would be a devastating retort, when Mr. Chen's voice carried across the store.

"Emma! There you are. And I see you've met our new rare books consultant, James Morrison."

[This would continue for several more pages, developing the meet-cute into a proper romantic comedy opening scene...]

Word Count: 487 words
Generated using: Brainstorm v3 + Characters (Emma, James) + Cheesy-Romcom tone
      `;
      
      setGeneratedContent(content);
      setWordCount(487);
      setIsGenerating(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Write</h1>
          <p className="text-gray-600 mt-1">Generate polished content from your brainstormed ideas</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Brainstorm Selection */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Brainstorm</h3>
              
              <div className="space-y-3">
                {brainstormSessions.map((session) => (
                  <label key={session.id} className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name="brainstorm"
                      value={session.id}
                      checked={selectedBrainstorm === session.id}
                      onChange={(e) => setSelectedBrainstorm(e.target.value)}
                      className="mt-1 text-blue-600 focus:ring-blue-500"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">
                        Version {session.version} 
                        {session.id === 'latest' && <span className="text-blue-600 text-sm ml-1">(Latest)</span>}
                      </div>
                      <div className="text-sm text-gray-500">{session.created}</div>
                      <div className="text-sm text-gray-600 mt-1">{session.preview}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Source Data */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Source Data</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Table
                  </label>
                  <select
                    value={selectedTable}
                    onChange={(e) => setSelectedTable(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {tables.map((table) => (
                      <option key={table} value={table}>{table}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Rows
                  </label>
                  <div className="text-sm text-gray-600">
                    Rows: {selectedRows.join(', ')} (2 selected)
                  </div>
                </div>
              </div>
            </div>

            {/* Writing Configuration */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Writing Style</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tone
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {tones.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Custom Instructions
                  </label>
                  <textarea
                    value={customInstructions}
                    onChange={(e) => setCustomInstructions(e.target.value)}
                    placeholder="Additional writing instructions..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
              >
                {isGenerating ? 'Writing...' : 'Generate Content'}
              </button>
            </div>
          </div>

          {/* Content Panel */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Generated Content</h3>
                  {wordCount > 0 && (
                    <p className="text-sm text-gray-500 mt-1">{wordCount} words</p>
                  )}
                </div>
                {generatedContent && (
                  <div className="flex gap-2">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      Edit
                    </button>
                    <button className="text-green-600 hover:text-green-700 text-sm font-medium">
                      Export
                    </button>
                  </div>
                )}
              </div>
              
              <div className="p-6 h-full min-h-96">
                {isGenerating ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600">Generating content...</span>
                  </div>
                ) : generatedContent ? (
                  <div className="prose max-w-none">
                    <div className="whitespace-pre-wrap text-gray-700 font-serif leading-relaxed text-base">
                      {generatedContent}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                    <p>Your generated content will appear here</p>
                    <p className="text-sm mt-2">Select a brainstorm session and configure your writing preferences</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

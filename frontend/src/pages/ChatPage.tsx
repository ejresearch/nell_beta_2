import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'project_query' | 'suggestion';
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm Miranda, your AI writing assistant. I have access to your project data, LightRAG buckets, and previous outputs. How can I help you today?",
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Mock response logic based on user input
    setTimeout(() => {
      let responseContent = '';
      let responseType: 'text' | 'project_query' | 'suggestion' = 'text';

      const input = inputMessage.toLowerCase();
      
      if (input.includes('project') || input.includes('table')) {
        responseContent = `I can see you're working on a romantic comedy project with these tables:
        
**Characters Table** (2 rows):
- Emma Rodriguez (protagonist, bookstore employee)
- James Morrison (love interest, rare books consultant)

**Scenes Table** (12 rows):
- Various locations including "Between the Lines" bookstore
- Plot progression from meet-cute to resolution

**Plot Points Table** (8 rows):
- Three-act structure with romantic comedy beats

Would you like me to help you explore any specific aspect of your project?`;
        responseType = 'project_query';
      } else if (input.includes('bucket') || input.includes('knowledge')) {
        responseContent = `Your project has 3 LightRAG knowledge buckets:

**📚 Books** (23 documents, Active)
- Romance novels and writing guides
- Character development resources

**🎬 Scripts** (15 documents, Active) 
- Romantic comedy screenplays
- Dialogue examples and structure

**🎭 Plays** (8 documents, Inactive)
- Classical romantic works
- Shakespearean comedies

The books and scripts buckets are currently active for brainstorming and writing. Would you like me to help you work with any specific bucket?`;
        responseType = 'project_query';
      } else if (input.includes('help') || input.includes('what can you do')) {
        responseContent = `I can help you with many aspects of your writing project:

**🔍 Project Navigation:**
- Explain your project structure and data
- Show recent outputs and history
- Help you understand the workflow

**💡 Creative Assistance:**
- Suggest improvements to characters or plot
- Help brainstorm new ideas
- Provide writing tips based on your buckets

**📊 Data Insights:**
- Analyze your project tables
- Show connections between outputs
- Track your writing progress

**🚀 Workflow Guidance:**
- Explain how to use brainstorm → write pipeline
- Help configure buckets and prompts
- Suggest next steps for your project

What would you like to explore?`;
        responseType = 'suggestion';
      } else if (input.includes('emma') || input.includes('james') || input.includes('character')) {
        responseContent = `Based on your character data, Emma and James have great potential for romantic tension:

**Emma Rodriguez:**
- Passionate about literature (especially Jane Austen)
- Works at "Between the Lines" bookstore
- Defensive about her literary opinions
- Strong, independent personality

**James Morrison:**
- New rare books consultant
- Intellectually confident, slightly pretentious
- Challenges Emma's views (creating conflict)
- Hidden depth beneath the surface

The dynamic between them mirrors classic romantic comedy opposites-attract patterns. Their shared love of books provides common ground, while their different approaches to literature creates initial conflict.

Would you like me to suggest some scene ideas or dialogue approaches for these characters?`;
        responseType = 'project_query';
      } else {
        responseContent = `That's an interesting question! While I can help with writing and project guidance, I work best when discussing your specific project elements.

Try asking me about:
- Your project tables and data
- Character development ideas  
- Plot suggestions
- Writing workflow guidance
- LightRAG bucket contents

What aspect of your romantic comedy project would you like to explore?`;
        responseType = 'text';
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        type: responseType
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageStyle = (type?: string) => {
    switch (type) {
      case 'project_query':
        return 'border-l-4 border-blue-500 bg-blue-50';
      case 'suggestion':
        return 'border-l-4 border-green-500 bg-green-50';
      default:
        return 'bg-gray-50';
    }
  };

  const suggestedQuestions = [
    "What's in my project tables?",
    "Show me my LightRAG buckets",
    "Help me develop Emma's character",
    "Suggest plot ideas for my rom-com",
    "How does the brainstorm workflow work?",
    "What should I write next?"
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-lg">M</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Chat with Miranda</h1>
            <p className="text-sm text-gray-600">Your AI writing assistant with project context</p>
          </div>
          <div className="ml-auto">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              ● Online
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                  {message.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-semibold text-xs">M</span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">Miranda</span>
                      <span className="text-xs text-gray-500">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  )}
                  
                  <div
                    className={`p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : `text-gray-800 ${getMessageStyle(message.type)}`
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                  
                  {message.role === 'user' && (
                    <div className="text-xs text-gray-500 mt-1 text-right">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="max-w-3xl">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold text-xs">M</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">Miranda</span>
                    <span className="text-xs text-gray-500">typing...</span>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <div className="max-w-4xl mx-auto px-6 pb-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(question)}
                className="text-left p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Miranda about your project, characters, or writing process..."
                rows={2}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

import { create } from 'zustand';

// Main application store
export const useStore = create((set, get) => ({
  // Code state
  code: `# Welcome to AI Code Review Agent! 🤖
# Paste your code here or try the example below

def calculate_average(numbers):
    # TODO: Add input validation
    total = 0
    for num in numbers:
        total = total + num
    average = total / len(numbers)
    return average

def process_data(data):
    try:
        result = eval(data)  # Security issue!
        print(result)
    except:  # Bare except
        pass
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add(self, item):
        self.data.append(item)
    
    def process_all(self):
        for i in range(0, len(self.data)):
            self.process_item(self.data[i])
    
    def process_item(self, item):
        # Missing docstring
        return item * 2
`,
  language: 'python',
  docStyle: 'google',
  
  // Review results
  reviewResult: null,
  isLoading: false,
  error: null,
  
  // UI state
  activeTab: 'review',
  showDocumentation: true,
  showMetrics: true,
  darkMode: true,
  
  // Actions
  setCode: (code) => set({ code }),
  setLanguage: (language) => set({ language }),
  setDocStyle: (docStyle) => set({ docStyle }),
  setReviewResult: (result) => set({ reviewResult: result, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  toggleDocumentation: () => set((state) => ({ showDocumentation: !state.showDocumentation })),
  toggleMetrics: () => set((state) => ({ showMetrics: !state.showMetrics })),
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  
  clearResults: () => set({ reviewResult: null, error: null }),
}));

// History store for review history
export const useHistoryStore = create((set, get) => ({
  history: [],
  
  addToHistory: (review) => set((state) => ({
    history: [
      {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        language: review.language,
        score: review.overall_score,
        issuesCount: Object.values(review.issues_count || {}).reduce((a, b) => a + b, 0),
        preview: review.summary?.substring(0, 100) || 'Review completed',
      },
      ...state.history.slice(0, 19), // Keep last 20
    ],
  })),
  
  clearHistory: () => set({ history: [] }),
}));

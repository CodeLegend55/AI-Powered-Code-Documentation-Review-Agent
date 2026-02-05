import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import {
  Hero,
  Header,
  Footer,
  CodeEditor,
  ReviewResults,
  LoadingOverlay,
} from './components';
import { useStore, useHistoryStore } from './store/useStore';
import { reviewCode, checkHealth } from './services/api';

function App() {
  const [showHero, setShowHero] = useState(true);
  const [showMenu, setShowMenu] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');
  
  const { 
    code, 
    language, 
    docStyle, 
    reviewResult, 
    setReviewResult, 
    isLoading, 
    setLoading,
    setError,
    error 
  } = useStore();
  
  const { addToHistory } = useHistoryStore();

  // Check API health on mount
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const health = await checkHealth();
        setApiStatus(health.status === 'healthy' ? 'connected' : 'error');
        if (health.llm_status !== 'connected') {
          toast.error('LLM not configured. Please set GOOGLE_API_KEY.', {
            duration: 5000,
            icon: '⚠️',
          });
        }
      } catch (err) {
        setApiStatus('error');
        toast.error('Cannot connect to backend. Make sure the server is running.', {
          duration: 5000,
        });
      }
    };
    
    checkAPI();
  }, []);

  const handleReview = async (options) => {
    if (!code.trim()) {
      toast.error('Please enter some code to review');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await reviewCode(code, language, docStyle, {
        checkSecurity: options.checkSecurity,
        generateDocs: options.generateDocs,
      });
      
      setReviewResult(result);
      addToHistory(result);
      
      // Show success toast with score
      const scoreEmoji = result.overall_score >= 80 ? '🎉' : 
                         result.overall_score >= 60 ? '👍' : 
                         result.overall_score >= 40 ? '⚠️' : '🔴';
      
      toast.success(`Review complete! Score: ${Math.round(result.overall_score)}/100 ${scoreEmoji}`, {
        duration: 4000,
      });
      
    } catch (err) {
      console.error('Review error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to review code';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGetStarted = () => {
    setShowHero(false);
  };

  return (
    <div className="min-h-screen bg-dark-950">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #334155',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#f1f5f9',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#f1f5f9',
            },
          },
        }}
      />

      <AnimatePresence mode="wait">
        {showHero ? (
          <motion.div
            key="hero"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Hero onGetStarted={handleGetStarted} />
          </motion.div>
        ) : (
          <motion.div
            key="app"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col min-h-screen"
          >
            <Header showMenu={showMenu} setShowMenu={setShowMenu} />
            
            {/* API Status indicator */}
            <div className="fixed bottom-4 left-4 z-40">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                apiStatus === 'connected' 
                  ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                  : apiStatus === 'error'
                  ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                  : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
              }`}>
                <span className={`w-2 h-2 rounded-full ${
                  apiStatus === 'connected' ? 'bg-green-400' :
                  apiStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400 animate-pulse'
                }`} />
                {apiStatus === 'connected' ? 'API Connected' :
                 apiStatus === 'error' ? 'API Error' : 'Connecting...'}
              </div>
            </div>

            {/* Main content */}
            <main className="flex-1 pt-16">
              <div className="h-[calc(100vh-4rem)] flex flex-col lg:flex-row">
                {/* Editor panel */}
                <div className="w-full lg:w-1/2 h-1/2 lg:h-full border-b lg:border-b-0 lg:border-r border-dark-700 bg-dark-900 relative">
                  <CodeEditor onReview={handleReview} isLoading={isLoading} />
                  
                  {/* Loading overlay */}
                  <AnimatePresence>
                    {isLoading && <LoadingOverlay />}
                  </AnimatePresence>
                </div>

                {/* Results panel */}
                <div className="w-full lg:w-1/2 h-1/2 lg:h-full bg-dark-900/50 overflow-hidden">
                  <ReviewResults result={reviewResult} />
                </div>
              </div>
            </main>

            {/* <Footer /> */}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;

import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCpu, FiPlay, FiCheckCircle, FiShield } from 'react-icons/fi';
import EditorComponent from './components/Editor';
import ReviewTab from './components/ReviewTab';

function App() {
  const [code, setCode] = useState('// Write or paste your code here\n\nfunction example() {\n  return "secure code";\n}');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:5000/api/review/analyze', { code });
      setResult(response.data);
    } catch (error) {
      console.error(error);
      setResult({
        error: error.response?.data?.error || "Failed to analyze code. Make sure the backend is running.",
        details: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <FiShield /> Antigen Code Reviewer
        </motion.h1>
        
        <motion.button 
          className="btn-primary"
          onClick={handleAnalyze}
          disabled={loading}
          whileTap={{ scale: 0.95 }}
        >
          {loading ? (
            <>
              <FiCpu className="spin-icon" /> Analyzing...
            </>
          ) : (
            <>
              <FiPlay /> Analyze Code
            </>
          )}
        </motion.button>
      </header>

      <main className="main-content">
        <motion.div 
          className="glass-panel" 
          style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div style={{ padding: '12px 20px', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Source Code</span>
            <div style={{ display: 'flex', gap: '6px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }}></div>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b' }}></div>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }}></div>
            </div>
          </div>
          <EditorComponent code={code} onChange={setCode} />
        </motion.div>

        <motion.div 
          className="glass-panel"
          style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--glass-border)' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-accent)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FiCheckCircle /> Analysis Results
            </span>
          </div>
          
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
            <AnimatePresence mode="wait">
              {loading ? (
                <motion.div 
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}
                >
                  <div className="pulse-ring"></div>
                  <p style={{ marginTop: '16px' }}>Consulting LLM and RAG Knowledge Base...</p>
                </motion.div>
              ) : result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <ReviewTab data={result} />
                </motion.div>
              ) : (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#475569', textAlign: 'center' }}
                >
                  <FiCpu size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                  <p>Submit your code to generate a security review <br/>and rich documentation.</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </main>

      <style>{`
        .spin-icon {
          animation: spin 2s linear infinite;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .pulse-ring {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          border: 3px solid var(--accent-color);
          border-top-color: transparent;
          animation: spin 1s infinite cubic-bezier(0.55, 0.15, 0.45, 0.85);
        }
      `}</style>
    </div>
  );
}

export default App;

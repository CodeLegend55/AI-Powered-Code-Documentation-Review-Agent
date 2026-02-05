import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { motion } from 'framer-motion';
import {
  PlayIcon,
  DocumentDuplicateIcon,
  ArrowPathIcon,
  Cog6ToothIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { useStore } from '../store/useStore';

const languageOptions = [
  { value: 'python', label: 'Python', icon: '🐍' },
  { value: 'javascript', label: 'JavaScript', icon: '💛' },
  { value: 'typescript', label: 'TypeScript', icon: '💙' },
  { value: 'java', label: 'Java', icon: '☕' },
  { value: 'cpp', label: 'C++', icon: '⚡' },
  { value: 'go', label: 'Go', icon: '🐹' },
];

const docStyleOptions = [
  { value: 'google', label: 'Google Style' },
  { value: 'numpy', label: 'NumPy Style' },
  { value: 'sphinx', label: 'Sphinx/reST' },
  { value: 'jsdoc', label: 'JSDoc' },
  { value: 'javadoc', label: 'Javadoc' },
];

export default function CodeEditor({ onReview, isLoading }) {
  const { code, setCode, language, setLanguage, docStyle, setDocStyle } = useStore();
  const editorRef = useRef(null);
  const [showSettings, setShowSettings] = useState(false);
  const [checkSecurity, setCheckSecurity] = useState(true);
  const [generateDocs, setGenerateDocs] = useState(true);

  const handleEditorMount = (editor) => {
    editorRef.current = editor;
  };

  const handleClear = () => {
    setCode('');
    if (editorRef.current) {
      editorRef.current.focus();
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
  };

  const handleFormat = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  const handleReview = () => {
    onReview({
      checkSecurity,
      generateDocs,
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex flex-col h-full"
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-dark-700">
        <div className="flex items-center gap-4">
          {/* Language selector */}
          <div className="relative">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="appearance-none bg-dark-800 border border-dark-600 rounded-lg px-4 py-2 pr-10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50 cursor-pointer"
            >
              {languageOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.icon} {opt.label}
                </option>
              ))}
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg className="w-4 h-4 text-dark-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          {/* Doc style selector */}
          <div className="relative">
            <select
              value={docStyle}
              onChange={(e) => setDocStyle(e.target.value)}
              className="appearance-none bg-dark-800 border border-dark-600 rounded-lg px-4 py-2 pr-10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/50 cursor-pointer"
            >
              {docStyleOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg className="w-4 h-4 text-dark-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Action buttons */}
          <button
            onClick={handleCopy}
            className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
            title="Copy code"
          >
            <DocumentDuplicateIcon className="w-5 h-5" />
          </button>
          <button
            onClick={handleFormat}
            className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
            title="Format code"
          >
            <ArrowPathIcon className="w-5 h-5" />
          </button>
          <button
            onClick={handleClear}
            className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
            title="Clear"
          >
            <TrashIcon className="w-5 h-5" />
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 rounded-lg transition-colors ${
              showSettings ? 'bg-primary-500/20 text-primary-400' : 'hover:bg-dark-700 text-dark-400 hover:text-white'
            }`}
            title="Settings"
          >
            <Cog6ToothIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="p-4 border-b border-dark-700 bg-dark-800/50"
        >
          <div className="flex flex-wrap gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={checkSecurity}
                onChange={(e) => setCheckSecurity(e.target.checked)}
                className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-500 focus:ring-primary-500/50"
              />
              <span className="text-sm text-dark-300">Security Analysis</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={generateDocs}
                onChange={(e) => setGenerateDocs(e.target.checked)}
                className="w-4 h-4 rounded border-dark-600 bg-dark-700 text-primary-500 focus:ring-primary-500/50"
              />
              <span className="text-sm text-dark-300">Generate Documentation</span>
            </label>
          </div>
        </motion.div>
      )}

      {/* Editor */}
      <div className="flex-1 min-h-0">
        <Editor
          height="100%"
          language={language}
          value={code}
          onChange={(value) => setCode(value || '')}
          onMount={handleEditorMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: "'JetBrains Mono', monospace",
            lineNumbers: 'on',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            padding: { top: 16, bottom: 16 },
            renderLineHighlight: 'all',
            cursorBlinking: 'smooth',
            smoothScrolling: true,
          }}
        />
      </div>

      {/* Review button */}
      <div className="p-4 border-t border-dark-700">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleReview}
          disabled={isLoading || !code.trim()}
          className={`w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 transition-all ${
            isLoading || !code.trim()
              ? 'bg-dark-700 text-dark-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-primary-500 to-purple-500 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40'
          }`}
        >
          {isLoading ? (
            <>
              <ArrowPathIcon className="w-6 h-6 animate-spin" />
              <span>Analyzing<span className="loading-dots"></span></span>
            </>
          ) : (
            <>
              <PlayIcon className="w-6 h-6" />
              <span>Review Code</span>
            </>
          )}
        </motion.button>
      </div>
    </motion.div>
  );
}

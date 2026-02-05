import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  ShieldExclamationIcon,
  LightBulbIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClipboardDocumentIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const severityConfig = {
  error: {
    icon: ExclamationCircleIcon,
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    label: 'Error',
  },
  warning: {
    icon: ExclamationTriangleIcon,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30',
    label: 'Warning',
  },
  info: {
    icon: InformationCircleIcon,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    label: 'Info',
  },
  security: {
    icon: ShieldExclamationIcon,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/30',
    label: 'Security',
  },
  suggestion: {
    icon: LightBulbIcon,
    color: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30',
    label: 'Suggestion',
  },
};

function ScoreCircle({ score }) {
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;
  
  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="64"
          cy="64"
          r="45"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-dark-700"
        />
        <circle
          cx="64"
          cy="64"
          r="45"
          fill="none"
          stroke={getScoreColor(score)}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="score-circle"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-white">{Math.round(score)}</span>
        <span className="text-xs text-dark-400">/ 100</span>
      </div>
    </div>
  );
}

function IssueCard({ issue }) {
  const [expanded, setExpanded] = useState(false);
  const config = severityConfig[issue.severity] || severityConfig.info;
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-lg border ${config.border} ${config.bg} overflow-hidden`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-start gap-3 text-left"
      >
        <Icon className={`w-5 h-5 ${config.color} flex-shrink-0 mt-0.5`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs font-medium px-2 py-0.5 rounded ${config.bg} ${config.color}`}>
              {config.label}
            </span>
            {issue.line && (
              <span className="text-xs text-dark-500">Line {issue.line}</span>
            )}
          </div>
          <p className="text-sm text-white">{issue.message}</p>
        </div>
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          className="text-dark-400"
        >
          <ChevronDownIcon className="w-5 h-5" />
        </motion.div>
      </button>
      
      <AnimatePresence>
        {expanded && (issue.suggestion || issue.code_snippet) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-dark-700"
          >
            <div className="p-4 space-y-3">
              {issue.suggestion && (
                <div>
                  <span className="text-xs font-medium text-dark-400 uppercase">Suggestion</span>
                  <p className="text-sm text-dark-300 mt-1">{issue.suggestion}</p>
                </div>
              )}
              {issue.code_snippet && (
                <div>
                  <span className="text-xs font-medium text-dark-400 uppercase">Code</span>
                  <div className="mt-1 rounded-lg overflow-hidden">
                    <SyntaxHighlighter
                      language="python"
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        padding: '12px',
                        fontSize: '13px',
                        background: '#1e293b',
                      }}
                    >
                      {issue.code_snippet}
                    </SyntaxHighlighter>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function TabButton({ active, onClick, children, icon: Icon }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        active
          ? 'bg-primary-500/20 text-primary-400'
          : 'text-dark-400 hover:text-white hover:bg-dark-700'
      }`}
    >
      {Icon && <Icon className="w-4 h-4" />}
      {children}
    </button>
  );
}

export default function ReviewResults({ result }) {
  const [activeTab, setActiveTab] = useState('issues');
  const [showDocCode, setShowDocCode] = useState(false);

  if (!result) {
    return (
      <div className="h-full flex items-center justify-center text-dark-500">
        <div className="text-center">
          <DocumentTextIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">No review results yet</p>
          <p className="text-sm mt-2">Enter your code and click "Review Code" to get started</p>
        </div>
      </div>
    );
  }

  const handleCopyDocumentation = () => {
    if (result.documentation) {
      navigator.clipboard.writeText(result.documentation);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="h-full flex flex-col"
    >
      {/* Header with score */}
      <div className="p-6 border-b border-dark-700">
        <div className="flex items-center gap-6">
          <ScoreCircle score={result.overall_score} />
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-white mb-2">Review Complete</h2>
            <p className="text-dark-400 text-sm mb-3">{result.summary}</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(result.issues_count || {}).map(([severity, count]) => {
                if (count === 0) return null;
                const config = severityConfig[severity] || severityConfig.info;
                return (
                  <span
                    key={severity}
                    className={`px-2 py-1 rounded text-xs font-medium ${config.bg} ${config.color} border ${config.border}`}
                  >
                    {count} {config.label}{count > 1 ? 's' : ''}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
        
        {/* Defect prediction */}
        {result.defect_prediction && (
          <div className={`mt-4 p-3 rounded-lg ${
            result.defect_prediction.risk_level === 'high' ? 'risk-high' :
            result.defect_prediction.risk_level === 'medium' ? 'risk-medium' : 'risk-low'
          }`}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                Risk Level: {result.defect_prediction.risk_level.toUpperCase()}
              </span>
              <span className="text-xs opacity-75">
                Score: {(result.defect_prediction.risk_score * 100).toFixed(0)}% • 
                Confidence: {(result.defect_prediction.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 p-4 border-b border-dark-700">
        <TabButton
          active={activeTab === 'issues'}
          onClick={() => setActiveTab('issues')}
          icon={ExclamationTriangleIcon}
        >
          Issues ({result.issues?.length || 0})
        </TabButton>
        <TabButton
          active={activeTab === 'documentation'}
          onClick={() => setActiveTab('documentation')}
          icon={DocumentTextIcon}
        >
          Documentation
        </TabButton>
        <TabButton
          active={activeTab === 'metrics'}
          onClick={() => setActiveTab('metrics')}
          icon={ChartBarIcon}
        >
          Details
        </TabButton>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-auto p-4">
        <AnimatePresence mode="wait">
          {activeTab === 'issues' && (
            <motion.div
              key="issues"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              {result.issues?.length > 0 ? (
                result.issues.map((issue, index) => (
                  <IssueCard key={index} issue={issue} />
                ))
              ) : (
                <div className="text-center py-8 text-dark-500">
                  <CheckCircleIcon className="w-12 h-12 mx-auto mb-3 text-green-500" />
                  <p>No issues found! Your code looks great.</p>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'documentation' && (
            <motion.div
              key="documentation"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {result.documentation ? (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-white">Generated Documentation</h3>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setShowDocCode(!showDocCode)}
                        className="px-3 py-1.5 rounded-lg bg-dark-700 text-sm text-dark-300 hover:text-white transition-colors"
                      >
                        {showDocCode ? 'Hide Code' : 'Show Code'}
                      </button>
                      <button
                        onClick={handleCopyDocumentation}
                        className="p-2 rounded-lg bg-dark-700 text-dark-300 hover:text-white transition-colors"
                        title="Copy to clipboard"
                      >
                        <ClipboardDocumentIcon className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                  
                  {showDocCode && (
                    <div className="rounded-lg overflow-hidden mb-4">
                      <SyntaxHighlighter
                        language={result.language_detected || 'python'}
                        style={vscDarkPlus}
                        showLineNumbers
                        customStyle={{
                          margin: 0,
                          padding: '16px',
                          fontSize: '13px',
                          background: '#1e293b',
                          maxHeight: '400px',
                        }}
                      >
                        {result.documentation}
                      </SyntaxHighlighter>
                    </div>
                  )}

                  {/* Functions documented */}
                  {result.functions_documented?.length > 0 && (
                    <div className="mb-6">
                      <h4 className="text-sm font-medium text-dark-400 uppercase mb-3">
                        Functions ({result.functions_documented.length})
                      </h4>
                      <div className="space-y-3">
                        {result.functions_documented.map((func, index) => (
                          <div key={index} className="p-4 rounded-lg bg-dark-800 border border-dark-700">
                            <code className="text-primary-400 text-sm">{func.signature || func.name}</code>
                            <div className="mt-2 text-sm text-dark-400 whitespace-pre-wrap">
                              {func.docstring?.substring(0, 200)}
                              {func.docstring?.length > 200 && '...'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Classes documented */}
                  {result.classes_documented?.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-dark-400 uppercase mb-3">
                        Classes ({result.classes_documented.length})
                      </h4>
                      <div className="space-y-3">
                        {result.classes_documented.map((cls, index) => (
                          <div key={index} className="p-4 rounded-lg bg-dark-800 border border-dark-700">
                            <code className="text-purple-400 text-sm">class {cls.name}</code>
                            <div className="mt-2 text-sm text-dark-400 whitespace-pre-wrap">
                              {cls.docstring?.substring(0, 200)}
                              {cls.docstring?.length > 200 && '...'}
                            </div>
                            {cls.methods?.length > 0 && (
                              <div className="mt-3 pl-4 border-l border-dark-600">
                                <span className="text-xs text-dark-500">
                                  {cls.methods.length} method{cls.methods.length > 1 ? 's' : ''} documented
                                </span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 text-dark-500">
                  <DocumentTextIcon className="w-12 h-12 mx-auto mb-3" />
                  <p>No documentation generated</p>
                  <p className="text-sm mt-1">Enable "Generate Documentation" in settings</p>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'metrics' && (
            <motion.div
              key="metrics"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {/* Processing info */}
              <div className="p-4 rounded-lg bg-dark-800 border border-dark-700">
                <h4 className="text-sm font-medium text-dark-400 uppercase mb-3">Processing Info</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-dark-500 text-sm">Language</span>
                    <p className="text-white font-medium">{result.language_detected}</p>
                  </div>
                  <div>
                    <span className="text-dark-500 text-sm">Processing Time</span>
                    <p className="text-white font-medium">{result.processing_time?.toFixed(2)}s</p>
                  </div>
                </div>
              </div>

              {/* RAG Context */}
              {result.rag_context && (
                <div className="p-4 rounded-lg bg-dark-800 border border-dark-700">
                  <h4 className="text-sm font-medium text-dark-400 uppercase mb-3">
                    RAG Context Used
                  </h4>
                  <p className="text-dark-300 text-sm">
                    {result.rag_context.sources_used || 0} documentation sources retrieved
                  </p>
                  {result.rag_context.context_preview && (
                    <p className="text-dark-500 text-xs mt-2 truncate">
                      {result.rag_context.context_preview}
                    </p>
                  )}
                </div>
              )}

              {/* Timestamp */}
              <div className="text-center text-dark-500 text-sm">
                Reviewed at {new Date(result.timestamp).toLocaleString()}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

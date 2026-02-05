import { motion } from 'framer-motion';
import {
  CodeBracketIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  SparklesIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    icon: CodeBracketIcon,
    title: 'Code Analysis',
    description: 'Deep analysis of code structure, complexity, and best practices using AST parsing.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: ShieldCheckIcon,
    title: 'Security Scanning',
    description: 'Detect security vulnerabilities, injection risks, and sensitive data exposure.',
    color: 'from-red-500 to-orange-500',
  },
  {
    icon: DocumentTextIcon,
    title: 'Auto Documentation',
    description: 'Generate comprehensive docstrings in Google, NumPy, Sphinx, or JSDoc style.',
    color: 'from-green-500 to-emerald-500',
  },
  {
    icon: CpuChipIcon,
    title: 'ML Defect Detection',
    description: 'Pre-flag high-risk code sections using trained machine learning models.',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: SparklesIcon,
    title: 'RAG-Powered',
    description: 'Context-aware reviews grounded in programming standards and documentation.',
    color: 'from-yellow-500 to-amber-500',
  },
  {
    icon: ChartBarIcon,
    title: 'Quality Metrics',
    description: 'Detailed metrics including complexity score, code coverage, and maintainability.',
    color: 'from-indigo-500 to-violet-500',
  },
];

export default function Hero({ onGetStarted }) {
  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center px-4 py-16 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-hero-pattern opacity-50" />
      <div className="absolute top-1/4 -left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />
      
      {/* Hero content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 text-center max-w-4xl mx-auto"
      >
        {/* Badge */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/30 mb-8"
        >
          <SparklesIcon className="w-5 h-5 text-primary-400" />
          <span className="text-primary-300 text-sm font-medium">Powered by LangChain & Google Gemini</span>
        </motion.div>
        
        {/* Title */}
        <h1 className="text-5xl md:text-7xl font-bold mb-6">
          <span className="gradient-text">AI-Powered</span>
          <br />
          <span className="text-white">Code Review Agent</span>
        </h1>
        
        {/* Subtitle */}
        <p className="text-xl text-dark-300 mb-8 max-w-2xl mx-auto">
          Intelligent code analysis, documentation generation, and security scanning 
          using advanced LLM orchestration with RAG-enhanced context.
        </p>
        
        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onGetStarted}
            className="px-8 py-4 rounded-xl bg-gradient-to-r from-primary-500 to-purple-500 text-white font-semibold text-lg shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 transition-shadow"
          >
            Start Reviewing Code
          </motion.button>
          <motion.a
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 rounded-xl bg-dark-800 border border-dark-600 text-white font-semibold text-lg hover:bg-dark-700 transition-colors"
          >
            View on GitHub
          </motion.a>
        </div>
      </motion.div>
      
      {/* Features grid */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.8 }}
        className="relative z-10 w-full max-w-6xl mx-auto"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ y: -5 }}
              className="glass rounded-2xl p-6 card-hover"
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-dark-400 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
      
      {/* Tech stack */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="relative z-10 mt-16 text-center"
      >
        <p className="text-dark-500 text-sm mb-4">Built with</p>
        <div className="flex flex-wrap justify-center gap-4">
          {['LangChain', 'Google Gemini', 'ChromaDB', 'FastAPI', 'React', 'Python'].map((tech) => (
            <span
              key={tech}
              className="px-4 py-2 rounded-lg bg-dark-800/50 text-dark-300 text-sm font-medium"
            >
              {tech}
            </span>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

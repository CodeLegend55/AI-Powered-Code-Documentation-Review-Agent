import { motion } from 'framer-motion';

export default function LoadingOverlay({ message = 'Analyzing your code...' }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 bg-dark-900/80 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div className="text-center">
        {/* Animated logo */}
        <div className="relative w-24 h-24 mx-auto mb-6">
          {/* Outer ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary-500 border-r-purple-500"
          />
          {/* Middle ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-2 rounded-full border-4 border-transparent border-t-purple-500 border-l-primary-500"
          />
          {/* Inner ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="absolute inset-4 rounded-full border-4 border-transparent border-b-primary-400 border-r-purple-400"
          />
          {/* Center dot */}
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="absolute inset-8 rounded-full bg-gradient-to-br from-primary-500 to-purple-500"
          />
        </div>

        {/* Processing steps */}
        <div className="space-y-3">
          <motion.h3
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xl font-semibold text-white"
          >
            {message}
          </motion.h3>
          
          <div className="flex flex-col items-center gap-2">
            <ProcessingStep label="Parsing code structure" delay={0} />
            <ProcessingStep label="Running defect analysis" delay={0.5} />
            <ProcessingStep label="Retrieving standards (RAG)" delay={1} />
            <ProcessingStep label="Generating review & documentation" delay={1.5} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function ProcessingStep({ label, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-center gap-2 text-dark-400"
    >
      <motion.div
        animate={{ opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1.5, repeat: Infinity, delay }}
        className="w-2 h-2 rounded-full bg-primary-500"
      />
      <span className="text-sm">{label}</span>
    </motion.div>
  );
}

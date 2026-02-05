import { motion } from 'framer-motion';
import { HeartIcon } from '@heroicons/react/24/solid';

export default function Footer() {
  return (
    <footer className="border-t border-dark-700 bg-dark-900/50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-dark-400 text-sm">
            <span>Built with</span>
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <HeartIcon className="w-4 h-4 text-red-500" />
            </motion.span>
            <span>for Senior Design Project</span>
          </div>
          
          <div className="flex items-center gap-6 text-dark-500 text-sm">
            <span>B.Tech Final Year • 2024-2026</span>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-primary-400 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-dark-800 flex flex-wrap justify-center gap-4 text-xs text-dark-600">
          <span>LangChain</span>
          <span>•</span>
          <span>Google Gemini</span>
          <span>•</span>
          <span>ChromaDB</span>
          <span>•</span>
          <span>FastAPI</span>
          <span>•</span>
          <span>React</span>
          <span>•</span>
          <span>Tailwind CSS</span>
        </div>
      </div>
    </footer>
  );
}

import { motion } from 'framer-motion';
import {
  Bars3Icon,
  XMarkIcon,
  CodeBracketIcon,
  Cog6ToothIcon,
  QuestionMarkCircleIcon,
  MoonIcon,
  SunIcon,
} from '@heroicons/react/24/outline';
import { useStore } from '../store/useStore';

export default function Header({ showMenu, setShowMenu }) {
  const { darkMode, toggleDarkMode } = useStore();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-dark-700/50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center"
            >
              <CodeBracketIcon className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-lg font-semibold text-white">Code Review Agent</h1>
              <p className="text-xs text-dark-400">AI-Powered Analysis</p>
            </div>
          </div>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="text-sm text-dark-300 hover:text-white transition-colors">
              Documentation
            </a>
            <a href="#" className="text-sm text-dark-300 hover:text-white transition-colors">
              API
            </a>
            <a href="#" className="text-sm text-dark-300 hover:text-white transition-colors">
              GitHub
            </a>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
            >
              {darkMode ? (
                <SunIcon className="w-5 h-5" />
              ) : (
                <MoonIcon className="w-5 h-5" />
              )}
            </button>
            <button className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors">
              <Cog6ToothIcon className="w-5 h-5" />
            </button>
            <button className="p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors">
              <QuestionMarkCircleIcon className="w-5 h-5" />
            </button>
            
            {/* Mobile menu button */}
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="md:hidden p-2 rounded-lg hover:bg-dark-700 text-dark-400 hover:text-white transition-colors"
            >
              {showMenu ? (
                <XMarkIcon className="w-6 h-6" />
              ) : (
                <Bars3Icon className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {showMenu && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="md:hidden border-t border-dark-700"
        >
          <nav className="px-4 py-4 space-y-2">
            <a
              href="#"
              className="block px-4 py-2 rounded-lg text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
            >
              Documentation
            </a>
            <a
              href="#"
              className="block px-4 py-2 rounded-lg text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
            >
              API
            </a>
            <a
              href="#"
              className="block px-4 py-2 rounded-lg text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
            >
              GitHub
            </a>
          </nav>
        </motion.div>
      )}
    </header>
  );
}

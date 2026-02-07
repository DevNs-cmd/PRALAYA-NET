import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CommandCenter from "./components/CommandCenter";
import EnhancedCommandCenter from "./components/EnhancedCommandCenter";
import ErrorBoundary from "./components/ErrorBoundary";
import "./index.css";

function App() {
  return (
    <Router>
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-900">
          {/* Navigation */}
          <nav className="bg-gray-800 border-b border-gray-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-white font-bold text-xl">🚀 PRALAYA-NET</h1>
                </div>
                <div className="flex space-x-4">
                  <Link
                    to="/"
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/command-center"
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Command Center
                  </Link>
                  <Link
                    to="/enhanced-command-center"
                    className="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium bg-green-600"
                  >
                    Enhanced CC
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* Routes */}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/command-center" element={<CommandCenter />} />
            <Route path="/enhanced-command-center" element={<EnhancedCommandCenter />} />
          </Routes>
        </div>
      </ErrorBoundary>
    </Router>
  );
}

export default App;

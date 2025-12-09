import { Navbar } from "./components/Navbar";
import { Sidebar } from './components/Sidebar';
import { Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ChatWindow from './components/tabs/ChatWindow';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <div className="flex flex-col h-screen">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Navigate to="/ai-co-founder" replace />} />
              <Route path="/ai-assistant" element={<ChatWindow activeTab="ai-assistant" />} />
              <Route path="/ai-co-founder" element={<ChatWindow activeTab="ai-co-founder" />} />
            </Routes>
          
        </div>
      </div>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </div>
  );
}

export default App;

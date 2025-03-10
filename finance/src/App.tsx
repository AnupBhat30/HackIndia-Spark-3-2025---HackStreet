import { Routes, Route } from 'react-router-dom';
import Home from './components/HomePage'; 
import ChatPage from './components/ChatPage';
import CalculatorPage from './components/CalculatorPage';
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/chat" element={<ChatPage />} />
      <Route path="/calc" element={<CalculatorPage />} />
    </Routes>
  );
}

export default App;

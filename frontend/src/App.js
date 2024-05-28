// App.js
import React from 'react';
import { Routes, Route, BrowserRouter } from "react-router-dom";
import UploadTeam from './pages/UploadTeam';
import View from './pages/View';
import MainPage from './pages/MainPage';
import ComplexView from './pages/ComplexView'
import Squad from './pages/Squad';
import UploadTransfer from './pages/UploadTransfer';
import TransferView from './pages/TransferView';

function App() {
  
  return (
    <div className="App">
      <BrowserRouter>
          <Routes>
          <Route path="/" element={<MainPage />} />
            <Route path="/upload_team" element={<UploadTeam />} />
            <Route path="/team_basic" element={<View />} />
            <Route path="/team_complex" element={<ComplexView />} />
            <Route path="/squad" element={<Squad />} />
            <Route path="/upload_transfer" element={<UploadTransfer />} />
            <Route path="/transfer_complex" element={<TransferView />} />
          </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;